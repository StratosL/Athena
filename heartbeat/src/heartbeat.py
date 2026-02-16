"""Core heartbeat logic — scheduler, tick function, alert delivery.

Each tick:
1. Reads Meta/heartbeat.md from the vault (user-editable checklist)
2. Injects user profile + agent memory (same pattern as voice proxy)
3. Calls the Kibana converse API with a heartbeat prompt
4. Suppresses HEARTBEAT_OK responses, delivers real alerts to the daily note
"""

import asyncio
import logging
import signal
from datetime import UTC, datetime
from pathlib import Path

import frontmatter
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import HeartbeatSettings

logger = logging.getLogger(__name__)

MAX_MEMORY_CHARS = 20_000
HEARTBEAT_OK_SENTINEL = "HEARTBEAT_OK"

HEARTBEAT_PROMPT_TEMPLATE = (
    "HEARTBEAT CHECK: You are running as a scheduled background check. "
    "Read the following checklist and evaluate each relevant section using your available tools. "
    "Base your evaluation on the current time and day.\n\n"
    "If NOTHING needs the user's attention right now, respond with exactly "
    "`HEARTBEAT_OK` and nothing else.\n\n"
    "If something DOES need attention, describe it clearly and suggest a specific action. "
    "Do NOT ask for confirmation — just report what you found.\n\n"
    "---\n\n{checklist}"
)


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (between --- delimiters) from markdown text."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip("\n")
    return text


def _read_memory_context(vault_path: Path) -> str:
    """Read user profile and agent memory files from the vault.

    Returns a formatted string for injection into systemPromptAddition,
    or empty string if no memory files exist.
    """
    sections: list[str] = []

    for filename, header in [
        ("Meta/user-profile.md", "## User Profile"),
        ("Meta/memory.md", "## Agent Memory"),
    ]:
        filepath = vault_path / filename
        try:
            raw = filepath.read_text(encoding="utf-8")
            content = _strip_frontmatter(raw)[:MAX_MEMORY_CHARS]
            sections.append(f"{header}\n\n{content}")
        except FileNotFoundError:
            logger.debug("Memory file not found: %s", filepath)
        except Exception:
            logger.warning("Failed to read memory file: %s", filepath, exc_info=True)

    return "\n\n".join(sections)


def _read_heartbeat_checklist(vault_path: Path) -> str | None:
    """Read Meta/heartbeat.md from the vault, strip frontmatter.

    Returns the checklist content, or None if missing/empty.
    """
    filepath = vault_path / "Meta" / "heartbeat.md"
    try:
        raw = filepath.read_text(encoding="utf-8")
        content = _strip_frontmatter(raw).strip()
        return content if content else None
    except FileNotFoundError:
        logger.debug("Heartbeat checklist not found: %s", filepath)
        return None
    except Exception:
        logger.warning("Failed to read heartbeat checklist: %s", filepath, exc_info=True)
        return None


def _load_conversation_id(path: str) -> str | None:
    """Read persisted conversation ID from file, or None."""
    try:
        return Path(path).read_text(encoding="utf-8").strip() or None
    except FileNotFoundError:
        return None
    except Exception:
        logger.warning("Failed to read conversation ID file: %s", path, exc_info=True)
        return None


def _save_conversation_id(path: str, conversation_id: str) -> None:
    """Write conversation ID to file for session continuity."""
    try:
        Path(path).write_text(conversation_id, encoding="utf-8")
    except Exception:
        logger.warning("Failed to save conversation ID: %s", path, exc_info=True)


def _append_alert_to_daily_note(vault_path: Path, alert_text: str) -> str | None:
    """Append a heartbeat alert block to today's daily note.

    Creates the daily note if it doesn't exist. Returns the note path on success,
    or None on failure (non-fatal).
    """
    now = datetime.now(UTC)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    note_path = vault_path / "Daily Notes" / f"{date_str}.md"

    block = f"\n\n## Heartbeat Alert ({time_str} UTC)\n\n{alert_text}"

    try:
        if note_path.exists():
            # Append to existing daily note
            with note_path.open("r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            post.content = post.content.rstrip() + block
            post.metadata["updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            note_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        else:
            # Create new daily note
            note_path.parent.mkdir(parents=True, exist_ok=True)
            weekday_name = now.strftime("%A")
            month_name = now.strftime("%B")
            header = f"# {weekday_name}, {month_name} {now.day}, {now.year}"
            content = f"{header}{block}"
            post = frontmatter.Post(
                content,
                title=date_str,
                tags=["daily", "journal"],
                created=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                updated=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

        rel_path = f"Daily Notes/{date_str}.md"
        logger.info("Alert appended to daily note: %s", rel_path)
        return rel_path
    except Exception:
        logger.warning("Failed to write alert to daily note", exc_info=True)
        return None


async def heartbeat_tick(settings: HeartbeatSettings) -> None:
    """Execute a single heartbeat tick.

    Reads the checklist, calls the converse API, and delivers alerts.
    """
    vault_path = Path(settings.vault_path)

    # 1. Read heartbeat checklist
    checklist = _read_heartbeat_checklist(vault_path)
    if not checklist:
        logger.debug("No heartbeat checklist found or empty — skipping tick")
        return

    # 2. Read memory context
    memory_context = _read_memory_context(vault_path)

    # 3. Load conversation ID for session continuity
    conversation_id = _load_conversation_id(settings.conversation_id_file)

    # 4. Build the heartbeat prompt
    prompt = HEARTBEAT_PROMPT_TEMPLATE.format(checklist=checklist)

    # 5. Build converse API payload
    payload: dict = {
        "input": prompt,
        "agent_id": settings.agent_id,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if memory_context:
        payload["configuration_overrides"] = {
            "systemPromptAddition": memory_context,
        }

    # 6. Call the converse API
    logger.info("Heartbeat tick — calling converse API...")
    async with httpx.AsyncClient(
        timeout=120.0,
        headers={
            "Authorization": f"ApiKey {settings.elastic_api_key}",
            "kbn-xsrf": "true",
            "Content-Type": "application/json",
        },
    ) as client:
        try:
            resp = await client.post(
                f"{settings.kibana_url}/api/agent_builder/converse",
                json=payload,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("Kibana returned %s: %s", e.response.status_code, e.response.text[:500])
            return
        except httpx.ConnectError:
            logger.error("Cannot connect to Kibana at %s", settings.kibana_url)
            return
        except Exception:
            logger.exception("Heartbeat converse API call failed")
            return

    # 7. Parse response
    data = resp.json()
    message = data.get("response", {}).get("message", "")
    new_conversation_id = data.get("conversation_id")

    # 8. Save conversation ID for next tick
    if new_conversation_id:
        _save_conversation_id(settings.conversation_id_file, new_conversation_id)

    # 9. Check for HEARTBEAT_OK
    if HEARTBEAT_OK_SENTINEL in message.strip().upper().replace(" ", "").replace("`", ""):
        logger.info("Heartbeat tick — HEARTBEAT_OK (nothing to report)")
        return

    # 10. Real alert — log and deliver to daily note
    logger.info("Heartbeat alert:\n%s", message)
    _append_alert_to_daily_note(vault_path, message)


def run_scheduler(settings: HeartbeatSettings) -> None:
    """Start the APScheduler loop with CronTrigger for active hours."""
    if not settings.elastic_url or not settings.elastic_api_key:
        logger.error(
            "ELASTIC_URL and ELASTIC_API_KEY are required. "
            "Set them in .env or environment variables."
        )
        return

    # CronTrigger: run every N minutes, but only during active hours
    # hour="8-21" means 08:00 through 21:59 (end hour is inclusive)
    active_hour_end = settings.heartbeat_active_hour_end - 1
    trigger = CronTrigger(
        minute=f"*/{settings.heartbeat_interval_minutes}",
        hour=f"{settings.heartbeat_active_hour_start}-{active_hour_end}",
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        heartbeat_tick,
        trigger,
        args=[settings],
        id="heartbeat_tick",
        replace_existing=True,
        max_instances=1,
    )

    logger.info(
        "Heartbeat scheduler starting — every %d min, active hours %02d:00-%02d:00",
        settings.heartbeat_interval_minutes,
        settings.heartbeat_active_hour_start,
        settings.heartbeat_active_hour_end,
    )

    scheduler.start()

    # Run until interrupted
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def _handle_signal(signum: int, _frame: object) -> None:
        logger.info("Received signal %s — shutting down", signum)
        shutdown_event.set()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    try:
        loop.run_until_complete(shutdown_event.wait())
    finally:
        scheduler.shutdown(wait=True)
        loop.close()
        logger.info("Heartbeat scheduler stopped")
