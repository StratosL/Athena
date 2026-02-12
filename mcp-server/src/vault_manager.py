"""Obsidian vault filesystem access — read, write, query, and organize notes.

This is the core class that all vault MCP tools delegate to.
Inspired by reference/obsidian-ai-agent/app/shared/vault/vault_manager.py.

Key responsibilities:
- Path validation and directory traversal prevention
- YAML frontmatter parsing and writing (via python-frontmatter)
- Note CRUD operations (create, read, append, edit, delete, move)
- Vault structure queries (list, search, recent changes)
"""

import logging
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import frontmatter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Map top-level vault folder names to note_type values (mirrors indexer/src/parser.py)
NOTE_TYPE_FOLDER_MAP: dict[str, str] = {
    "projects": "project",
    "ideas": "idea",
    "meeting notes": "meeting",
    "daily notes": "daily",
    "research": "research",
}


class NoteSummary(BaseModel):
    """Lightweight note info for list/search results."""

    path: str
    title: str
    tags: list[str] = Field(default_factory=list)
    note_type: str = "note"
    word_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class NoteContent(BaseModel):
    """Full note content with frontmatter."""

    path: str
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    note_type: str = "note"
    word_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


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


class VaultManager:
    """Manages Obsidian vault filesystem operations with path security."""

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_root = Path(vault_path).resolve()
        if not self.vault_root.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_root}")
        if not self.vault_root.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {self.vault_root}")
        logger.info("VaultManager initialized: %s", self.vault_root)

    def _validate_path(self, relative_path: str) -> Path:
        """Resolve a vault-relative path and verify it stays within vault root."""
        abs_path = (self.vault_root / relative_path).resolve()
        if not str(abs_path).startswith(str(self.vault_root)):
            raise ValueError(f"Path escapes vault root: {relative_path}")
        return abs_path

    def _parse_frontmatter(self, file_path: Path) -> tuple[dict, str]:
        """Parse frontmatter from a markdown file.

        Returns:
            (metadata_dict, content_string). On error: ({}, raw_text).
        """
        try:
            with file_path.open("r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            metadata = dict(post.metadata) if post.metadata else {}
            return metadata, post.content
        except Exception:
            logger.warning("Failed to parse frontmatter: %s", file_path)
            raw = file_path.read_text(encoding="utf-8")
            return {}, raw

    def _note_type_from_path(self, rel_path: str) -> str:
        """Infer note_type from the first folder component of the vault-relative path."""
        parts = Path(rel_path).parts
        if len(parts) > 1:
            folder = parts[0].lower()
            if folder in NOTE_TYPE_FOLDER_MAP:
                return NOTE_TYPE_FOLDER_MAP[folder]
        return "note"

    def _build_note_summary(self, file_path: Path) -> NoteSummary:
        """Parse frontmatter and build a NoteSummary for a file."""
        rel_path = str(file_path.relative_to(self.vault_root))
        metadata, content = self._parse_frontmatter(file_path)

        title_raw = metadata.get("title")
        title = str(title_raw) if title_raw is not None else file_path.stem

        tags_raw = metadata.get("tags", [])
        if isinstance(tags_raw, str):
            tags = [tags_raw]
        elif isinstance(tags_raw, list):
            tags = [str(t) for t in tags_raw]
        else:
            tags = []

        note_type = metadata.get("type") or self._note_type_from_path(rel_path)

        created_at = _parse_datetime(metadata.get("created"))
        updated_at = _parse_datetime(metadata.get("updated") or metadata.get("modified"))
        stat = file_path.stat()
        if created_at is None:
            created_at = datetime.fromtimestamp(stat.st_ctime, tz=UTC)
        if updated_at is None:
            updated_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

        return NoteSummary(
            path=rel_path,
            title=title,
            tags=tags,
            note_type=str(note_type),
            word_count=len(content.split()),
            created_at=created_at,
            updated_at=updated_at,
        )

    def read_note(self, relative_path: str) -> NoteContent:
        """Read a single note and return full content with metadata."""
        abs_path = self._validate_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Note not found: {relative_path}")
        if not abs_path.is_file():
            raise ValueError(f"Path is not a file: {relative_path}")

        rel_path = str(abs_path.relative_to(self.vault_root))
        metadata, content = self._parse_frontmatter(abs_path)

        title_raw = metadata.get("title")
        title = str(title_raw) if title_raw is not None else abs_path.stem

        tags_raw = metadata.get("tags", [])
        if isinstance(tags_raw, str):
            tags = [tags_raw]
        elif isinstance(tags_raw, list):
            tags = [str(t) for t in tags_raw]
        else:
            tags = []

        note_type = metadata.get("type") or self._note_type_from_path(rel_path)

        created_at = _parse_datetime(metadata.get("created"))
        updated_at = _parse_datetime(metadata.get("updated") or metadata.get("modified"))
        stat = abs_path.stat()
        if created_at is None:
            created_at = datetime.fromtimestamp(stat.st_ctime, tz=UTC)
        if updated_at is None:
            updated_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

        return NoteContent(
            path=rel_path,
            title=title,
            content=content,
            tags=tags,
            note_type=str(note_type),
            word_count=len(content.split()),
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )

    def read_multiple(self, paths: list[str]) -> list[NoteContent]:
        """Read multiple notes, skipping errors with warnings."""
        results: list[NoteContent] = []
        for p in paths:
            try:
                results.append(self.read_note(p.strip()))
            except Exception as e:
                logger.warning("Skipping %s: %s", p, e)
        return results

    def daily_note(self, date_str: str | None = None) -> NoteContent:
        """Find and read today's daily note.

        Tries: Daily Notes/{date}.md, daily/{date}.md, {date}.md.
        """
        if date_str is None:
            date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        candidates = [
            f"Daily Notes/{date_str}.md",
            f"daily/{date_str}.md",
            f"{date_str}.md",
        ]
        for candidate in candidates:
            try:
                abs_path = self._validate_path(candidate)
                if abs_path.exists():
                    return self.read_note(candidate)
            except ValueError:
                continue

        raise FileNotFoundError(
            f"Daily note not found for {date_str}. Tried: {', '.join(candidates)}"
        )

    def write_note(
        self,
        relative_path: str,
        content: str,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> NoteContent:
        """Create a new note with frontmatter. Raises FileExistsError if already exists."""
        abs_path = self._validate_path(relative_path)
        if abs_path.exists():
            raise FileExistsError(f"Note already exists: {relative_path}")

        abs_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        title = abs_path.stem

        fm_metadata: dict = {
            "title": title,
            "created": now,
            "updated": now,
        }
        if tags:
            fm_metadata["tags"] = tags
        if metadata:
            fm_metadata.update(metadata)

        post = frontmatter.Post(content, **fm_metadata)
        abs_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        logger.info("Created note: %s", relative_path)
        return self.read_note(relative_path)

    def append_to_note(self, relative_path: str, content: str) -> NoteContent:
        """Append content to an existing note, preserving frontmatter."""
        abs_path = self._validate_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Note not found: {relative_path}")

        with abs_path.open("r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        post.content = post.content.rstrip() + "\n\n" + content
        post.metadata["updated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        abs_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        logger.info("Appended to note: %s", relative_path)
        return self.read_note(relative_path)

    def edit_note(self, relative_path: str, old_text: str, new_text: str) -> NoteContent:
        """Replace text in a note. Exactly one occurrence must match."""
        abs_path = self._validate_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Note not found: {relative_path}")

        with abs_path.open("r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        count = post.content.count(old_text)
        if count == 0:
            raise ValueError("Text not found")
        if count > 1:
            raise ValueError("Text matches multiple locations — provide more context")

        post.content = post.content.replace(old_text, new_text, 1)
        post.metadata["updated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        abs_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        logger.info("Edited note: %s", relative_path)
        return self.read_note(relative_path)

    def delete_note(self, relative_path: str, confirm_destructive: bool) -> bool:
        """Delete a note. Requires confirm_destructive=True."""
        if not confirm_destructive:
            return False

        abs_path = self._validate_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Note not found: {relative_path}")

        abs_path.unlink()
        logger.info("Deleted note: %s", relative_path)
        return True

    def move_note(self, source: str, destination: str) -> NoteContent:
        """Move a note to a new location, auto-creating parent dirs."""
        src_path = self._validate_path(source)
        dst_path = self._validate_path(destination)

        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        if dst_path.exists():
            raise FileExistsError(f"Destination already exists: {destination}")

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        logger.info("Moved note: %s -> %s", source, destination)
        return self.read_note(destination)

    def create_folder(self, relative_path: str) -> bool:
        """Create a folder (and parents) within the vault."""
        abs_path = self._validate_path(relative_path)
        abs_path.mkdir(parents=True, exist_ok=True)
        logger.info("Created folder: %s", relative_path)
        return True

    def list_notes(self, folder: str | None = None, recursive: bool = False) -> list[NoteSummary]:
        """List .md files in the vault, optionally scoped to a folder."""
        if folder:
            root = self._validate_path(folder)
            if not root.is_dir():
                raise ValueError(f"Not a directory: {folder}")
        else:
            root = self.vault_root

        pattern = "**/*.md" if recursive else "*.md"
        results: list[NoteSummary] = []
        for md_file in sorted(root.glob(pattern)):
            # Skip hidden directories
            rel = md_file.relative_to(self.vault_root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            try:
                results.append(self._build_note_summary(md_file))
            except Exception as e:
                logger.warning("Skipping %s: %s", md_file, e)
        return results

    def search_content(self, query: str, limit: int = 10) -> list[NoteSummary]:
        """Case-insensitive keyword search across title + content.

        Scoring: filename match=100, title match=50, content match=1.
        """
        query_lower = query.lower()
        scored: list[tuple[int, NoteSummary]] = []

        for md_file in self.vault_root.rglob("*.md"):
            rel = md_file.relative_to(self.vault_root)
            if any(part.startswith(".") for part in rel.parts):
                continue

            try:
                metadata, content = self._parse_frontmatter(md_file)
            except Exception:
                logger.debug("Skipping unparseable file: %s", md_file)
                continue

            score = 0
            filename = md_file.stem.lower()
            if query_lower in filename:
                score += 100

            title_raw = metadata.get("title")
            title = str(title_raw).lower() if title_raw is not None else filename
            if query_lower in title:
                score += 50

            if query_lower in content.lower():
                score += 1

            if score > 0:
                summary = self._build_note_summary(md_file)
                scored.append((score, summary))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:limit]]

    def search_by_metadata(
        self,
        tags: list[str] | None = None,
        folder: str | None = None,
        date_range_days: int | None = None,
    ) -> list[NoteSummary]:
        """Filter notes by tag intersection, folder prefix, and/or recency."""
        if folder:
            root = self._validate_path(folder)
            if not root.is_dir():
                raise ValueError(f"Not a directory: {folder}")
        else:
            root = self.vault_root

        cutoff = None
        if date_range_days and date_range_days > 0:
            cutoff = datetime.now(UTC).timestamp() - (date_range_days * 86400)

        results: list[NoteSummary] = []
        for md_file in root.rglob("*.md"):
            rel = md_file.relative_to(self.vault_root)
            if any(part.startswith(".") for part in rel.parts):
                continue

            if cutoff and md_file.stat().st_mtime < cutoff:
                continue

            try:
                summary = self._build_note_summary(md_file)
            except Exception:
                logger.debug("Skipping unparseable file: %s", md_file)
                continue

            if tags:
                note_tags_lower = {t.lower() for t in summary.tags}
                if not all(t.lower() in note_tags_lower for t in tags):
                    continue

            results.append(summary)

        return results

    def get_recent_notes(self, limit: int = 10) -> list[NoteSummary]:
        """Return the most recently modified notes."""
        all_files: list[tuple[float, Path]] = []
        for md_file in self.vault_root.rglob("*.md"):
            rel = md_file.relative_to(self.vault_root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            all_files.append((md_file.stat().st_mtime, md_file))

        all_files.sort(key=lambda x: x[0], reverse=True)

        results: list[NoteSummary] = []
        for _, md_file in all_files[:limit]:
            try:
                results.append(self._build_note_summary(md_file))
            except Exception as e:
                logger.warning("Skipping %s: %s", md_file, e)
        return results
