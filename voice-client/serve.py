"""Athena Voice Proxy Server.

Serves the static voice client UI and proxies requests to:
- Kibana Agent Builder converse API (chat)
- OpenAI Whisper API (speech-to-text)
- OpenAI TTS API (text-to-speech)

All API keys stay server-side — the browser never sees them.
"""

import logging
from pathlib import Path

import frontmatter
import httpx
from aiohttp import web
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}


@web.middleware
async def cors_middleware(request: web.Request, handler) -> web.Response:
    """Add CORS headers to all responses and handle preflight requests."""
    if request.method == "OPTIONS":
        return web.Response(headers=CORS_HEADERS)
    resp = await handler(request)
    resp.headers.update(CORS_HEADERS)
    return resp


class VoiceSettings(BaseSettings):
    """Configuration loaded from .env."""

    elastic_url: str = ""
    elastic_api_key: str = ""
    agent_id: str = "athena"
    openai_api_key: str = ""
    vault_path: str = "/vault"
    voice_server_port: int = 3001

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def kibana_url(self) -> str:
        """Derive Kibana URL from Elasticsearch URL."""
        return self.elastic_url.replace(".es.", ".kb.")


settings = VoiceSettings()

MAX_MEMORY_CHARS = 20_000


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (between --- delimiters) from markdown text."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip("\n")
    return text


def _read_memory_context() -> str:
    """Read user profile and agent memory files from the vault.

    Returns a formatted string for injection into systemPromptAddition,
    or empty string if no memory files exist.
    """
    vault = Path(settings.vault_path)
    sections: list[str] = []

    for filename, header in [
        ("Meta/user-profile.md", "## User Profile"),
        ("Meta/memory.md", "## Agent Memory"),
    ]:
        filepath = vault / filename
        try:
            raw = filepath.read_text(encoding="utf-8")
            content = _strip_frontmatter(raw)[:MAX_MEMORY_CHARS]
            sections.append(f"{header}\n\n{content}")
        except FileNotFoundError:
            logger.debug("Memory file not found: %s", filepath)
        except Exception:
            logger.warning("Failed to read memory file: %s", filepath, exc_info=True)

    # Inject available skill names and trigger phrases for fast matching
    skills_dir = vault / "Meta" / "Skills"
    if skills_dir.is_dir():
        skill_lines: list[str] = []
        for skill_file in sorted(skills_dir.glob("*.md")):
            try:
                post = frontmatter.loads(skill_file.read_text(encoding="utf-8"))
                title = post.metadata.get("title", skill_file.stem)
                triggers = post.metadata.get("trigger_phrases", [])
                skill_lines.append(f"- **{title}**: {', '.join(triggers[:3])}")
            except Exception:
                logger.warning("Failed to parse skill: %s", skill_file, exc_info=True)
        if skill_lines:
            sections.append("## Available Skills\n\n" + "\n".join(skill_lines))

    return "\n\n".join(sections)


# Persistent HTTP clients — reuse TCP connections + TLS sessions across requests.
# Created at module level, closed via app cleanup signal.
kibana_client = httpx.AsyncClient(
    timeout=120.0,
    headers={
        "Authorization": f"ApiKey {settings.elastic_api_key}",
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
    },
)
openai_client = httpx.AsyncClient(
    timeout=30.0,
    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
)


# --- Routes ---


async def health(_request: web.Request) -> web.Response:
    """Health check."""
    return web.json_response({"status": "ok"})


async def chat(request: web.Request) -> web.Response:
    """Proxy to Kibana Agent Builder converse API."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)

    input_text = body.get("input", "")
    conversation_id = body.get("conversation_id")
    if not input_text:
        return web.json_response({"error": "Missing 'input' field"}, status=400)

    payload: dict = {
        "input": input_text,
        "agent_id": settings.agent_id,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    memory_context = _read_memory_context()
    if memory_context:
        payload["configuration_overrides"] = {
            "instructions": memory_context,
        }

    try:
        resp = await kibana_client.post(
            f"{settings.kibana_url}/api/agent_builder/converse",
            json=payload,
        )
        resp.raise_for_status()
        return web.json_response(resp.json())
    except httpx.HTTPStatusError as e:
        logger.error("Kibana returned %s: %s", e.response.status_code, e.response.text)
        return web.json_response(
            {"error": f"Agent returned {e.response.status_code}: {e.response.text}"},
            status=e.response.status_code,
        )
    except httpx.ConnectError:
        return web.json_response(
            {"error": "Cannot connect to Kibana. Check ELASTIC_URL."}, status=502
        )
    except Exception as e:
        logger.exception("Chat proxy error")
        return web.json_response({"error": f"Unexpected error: {e}"}, status=500)


async def transcribe(request: web.Request) -> web.Response:
    """Proxy to OpenAI Whisper STT."""
    if not settings.openai_api_key:
        return web.json_response({"error": "OpenAI API key not configured"}, status=503)

    try:
        reader = await request.multipart()
        if reader is None:
            return web.json_response({"error": "Expected multipart form data"}, status=400)

        audio_data: bytes | None = None
        filename = "audio.webm"

        async for part in reader:
            if part.name == "file":
                audio_data = bytes(await part.read())
                if part.filename:
                    filename = part.filename

        if not audio_data:
            return web.json_response({"error": "No audio file provided"}, status=400)

        resp = await openai_client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            files={"file": (filename, audio_data, "audio/webm")},
            data={"model": "whisper-1"},
        )
        resp.raise_for_status()
        return web.json_response(resp.json())
    except httpx.HTTPStatusError as e:
        logger.error("Whisper returned %s: %s", e.response.status_code, e.response.text)
        return web.json_response(
            {"error": f"Whisper error: {e.response.text}"}, status=e.response.status_code
        )
    except Exception as e:
        logger.exception("Transcribe proxy error")
        return web.json_response({"error": f"Unexpected error: {e}"}, status=500)


async def speak(request: web.Request) -> web.Response:
    """Proxy to OpenAI TTS."""
    if not settings.openai_api_key:
        return web.json_response({"error": "OpenAI API key not configured"}, status=503)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)

    text = body.get("text", "")
    voice = body.get("voice", "nova")
    if not text:
        return web.json_response({"error": "Missing 'text' field"}, status=400)

    # TTS API limit
    if len(text) > 4096:
        text = text[:4096]

    try:
        resp = await openai_client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Content-Type": "application/json"},
            json={"model": "tts-1", "voice": voice, "input": text},
        )
        resp.raise_for_status()
        return web.Response(body=resp.content, content_type="audio/mpeg")
    except httpx.HTTPStatusError as e:
        logger.error("TTS returned %s: %s", e.response.status_code, e.response.text)
        return web.json_response(
            {"error": f"TTS error: {e.response.text}"}, status=e.response.status_code
        )
    except Exception as e:
        logger.exception("Speak proxy error")
        return web.json_response({"error": f"Unexpected error: {e}"}, status=500)


# --- App Setup ---


async def on_shutdown(_app: web.Application) -> None:
    """Close persistent HTTP clients on shutdown."""
    await kibana_client.aclose()
    await openai_client.aclose()


def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application(middlewares=[cors_middleware])
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/api/health", health)
    app.router.add_post("/api/chat", chat)
    app.router.add_post("/api/transcribe", transcribe)
    app.router.add_post("/api/speak", speak)
    # Static files — serve index.html at root, other files by name
    app.router.add_get("/", lambda _: web.FileResponse(STATIC_DIR / "index.html"))
    app.router.add_static("/", STATIC_DIR, show_index=False)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logger.info("Starting Athena Voice Proxy on port %s", settings.voice_server_port)
    web.run_app(create_app(), port=settings.voice_server_port)
