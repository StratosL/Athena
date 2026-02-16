"""Parse Obsidian vault markdown files into Pydantic models for Elasticsearch indexing."""

import hashlib
import logging
from datetime import UTC, date, datetime
from pathlib import Path

import frontmatter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Map top-level vault folder names to note_type values
NOTE_TYPE_FOLDER_MAP: dict[str, str] = {
    "projects": "project",
    "ideas": "idea",
    "meeting notes": "meeting",
    "daily notes": "daily",
    "research": "research",
    "meta": "meta",
}


class ParsedNote(BaseModel):
    """A parsed Obsidian note ready for Elasticsearch indexing."""

    title: str
    content: str
    content_semantic: str
    tags: list[str] = Field(default_factory=list)
    note_type: str = "note"
    path: str
    vault_relative_path: str
    word_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    checksum: str

    def to_es_document(self) -> dict:
        """Convert to Elasticsearch document dict, serialising datetimes to ISO strings."""
        doc = self.model_dump()
        for key in ("created_at", "updated_at", "indexed_at"):
            val = doc.get(key)
            if isinstance(val, datetime):
                doc[key] = val.isoformat()
            elif val is None:
                doc.pop(key, None)
        return doc

    def es_doc_id(self) -> str:
        """Deterministic ES document _id derived from vault_relative_path (SHA-256)."""
        return hashlib.sha256(self.vault_relative_path.encode()).hexdigest()


def compute_checksum(file_path: Path) -> str:
    """Return MD5 hex digest of file contents (used for change detection)."""
    return hashlib.md5(file_path.read_bytes()).hexdigest()  # noqa: S324


def _infer_note_type(vault_relative_path: str) -> str:
    """Infer note_type from the first folder component of the vault-relative path."""
    parts = Path(vault_relative_path).parts
    if len(parts) > 1:
        folder = parts[0].lower()
        if folder in NOTE_TYPE_FOLDER_MAP:
            return NOTE_TYPE_FOLDER_MAP[folder]
    return "note"


def _parse_datetime(value: object) -> datetime | None:
    """Coerce a frontmatter value to a timezone-aware datetime, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt
        except (ValueError, TypeError):
            return None
    return None


def parse_note(file_path: Path, vault_root: Path) -> ParsedNote:
    """Parse a single .md file into a ParsedNote.

    Args:
        file_path: Absolute path to the markdown file.
        vault_root: Absolute path to the vault root directory.

    Returns:
        A ParsedNote populated from frontmatter + file metadata.

    Raises:
        ValueError: If file_path is outside vault_root.
    """
    file_path = file_path.resolve()
    vault_root = vault_root.resolve()
    if not str(file_path).startswith(str(vault_root)):
        raise ValueError(f"Path {file_path} is outside vault root {vault_root}")

    vault_relative_path = str(file_path.relative_to(vault_root))

    # Parse frontmatter
    with file_path.open("r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    metadata: dict = post.metadata if post.metadata else {}
    content: str = post.content

    # Title: frontmatter → filename stem
    title_raw = metadata.get("title")
    title = str(title_raw) if title_raw is not None else file_path.stem

    # Tags: handle str, list, or absent
    tags_raw = metadata.get("tags", [])
    if isinstance(tags_raw, str):
        tags = [tags_raw]
    elif isinstance(tags_raw, list):
        tags = [str(t) for t in tags_raw]
    else:
        tags = []

    # Dates: frontmatter → filesystem stat fallback
    created_at = _parse_datetime(metadata.get("created"))
    updated_at = _parse_datetime(metadata.get("updated") or metadata.get("modified"))

    stat = file_path.stat()
    if created_at is None:
        created_at = datetime.fromtimestamp(stat.st_ctime, tz=UTC)
    if updated_at is None:
        updated_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

    note_type = metadata.get("type") or _infer_note_type(vault_relative_path)

    return ParsedNote(
        title=title,
        content=content,
        content_semantic=content,
        tags=tags,
        note_type=str(note_type),
        path=str(file_path),
        vault_relative_path=vault_relative_path,
        word_count=len(content.split()),
        created_at=created_at,
        updated_at=updated_at,
        checksum=compute_checksum(file_path),
    )


def parse_vault(vault_root: Path) -> list[tuple[ParsedNote | None, str | None]]:
    """Parse all .md files in a vault directory.

    Args:
        vault_root: Absolute path to the vault root directory.

    Returns:
        List of (ParsedNote, None) on success or (None, error_message) on failure per file.
    """
    vault_root = vault_root.resolve()
    results: list[tuple[ParsedNote | None, str | None]] = []

    for md_file in sorted(vault_root.rglob("*.md")):
        # Skip hidden directories (e.g. .obsidian, .trash)
        if any(part.startswith(".") for part in md_file.relative_to(vault_root).parts):
            continue
        try:
            note = parse_note(md_file, vault_root)
            results.append((note, None))
        except Exception as e:
            error_msg = f"Failed to parse {md_file}: {e}"
            logger.warning(error_msg)
            results.append((None, error_msg))

    return results
