"""Vault MCP tools — direct Obsidian vault access via filesystem.

Three tools following the "fewer tools, more parameters" pattern:
- vault_query:  discovery (list_structure, search_content, search_by_metadata, recent_changes)
- vault_read:   reading (read_note, read_multiple, daily_note)
- vault_manage: writes (create_note, append_note, edit_note, move_note, delete_note, create_folder)

Reference: reference/obsidian-ai-agent/app/features/
"""

import json
import logging

from src.server import mcp, vault_manager

logger = logging.getLogger(__name__)

VALID_QUERY_OPS = ("list_structure", "search_content", "search_by_metadata", "recent_changes")
VALID_READ_OPS = ("read_note", "read_multiple", "daily_note")
VALID_MANAGE_OPS = (
    "create_note",
    "append_note",
    "edit_note",
    "move_note",
    "delete_note",
    "create_folder",
)


def _parse_csv(value: str) -> list[str]:
    """Parse a comma-separated string into a list of stripped non-empty strings."""
    return [t.strip() for t in value.split(",") if t.strip()]


@mcp.tool()
async def vault_query(
    operation: str,
    query: str = "",
    folder: str = "",
    tags: str = "",
    date_range_days: int = 0,
    limit: int = 10,
    recursive: bool = False,
) -> str:
    """Search and discover notes in the Obsidian vault.

    Args:
        operation: One of: list_structure, search_content, search_by_metadata, recent_changes.
        query: Search query text (for search_content).
        folder: Folder path to scope (for list_structure, search_by_metadata).
        tags: Comma-separated tag filter (for search_by_metadata).
        date_range_days: Only notes modified within N days (for search_by_metadata).
        limit: Max results to return (default 10).
        recursive: Include subfolders (for list_structure).
    """
    if operation not in VALID_QUERY_OPS:
        return json.dumps(
            {"error": f"Unknown operation '{operation}'. Use: {', '.join(VALID_QUERY_OPS)}"}
        )

    try:
        if operation == "list_structure":
            results = vault_manager.list_notes(folder or None, recursive)
            return json.dumps([r.model_dump(mode="json") for r in results], default=str)

        if operation == "search_content":
            if not query:
                return json.dumps({"error": "search_content requires 'query' parameter"})
            results = vault_manager.search_content(query, limit)
            return json.dumps([r.model_dump(mode="json") for r in results], default=str)

        if operation == "search_by_metadata":
            tag_list = _parse_csv(tags) if tags else None
            results = vault_manager.search_by_metadata(
                tags=tag_list,
                folder=folder or None,
                date_range_days=date_range_days if date_range_days > 0 else None,
            )
            return json.dumps([r.model_dump(mode="json") for r in results], default=str)

        if operation == "recent_changes":
            results = vault_manager.get_recent_notes(limit)
            return json.dumps([r.model_dump(mode="json") for r in results], default=str)

    except Exception as e:
        return json.dumps({"error": f"vault_query failed: {e}"})

    return json.dumps({"error": "Unexpected operation"})


@mcp.tool()
async def vault_read(
    operation: str,
    path: str = "",
    paths: str = "",
    date: str = "",
) -> str:
    """Read full content of notes from the Obsidian vault.

    Args:
        operation: One of: read_note, read_multiple, daily_note.
        path: Vault-relative path to a note (for read_note).
        paths: Comma-separated vault-relative paths (for read_multiple).
        date: Date string YYYY-MM-DD (for daily_note, defaults to today).
    """
    if operation not in VALID_READ_OPS:
        return json.dumps(
            {"error": f"Unknown operation '{operation}'. Use: {', '.join(VALID_READ_OPS)}"}
        )

    try:
        if operation == "read_note":
            if not path:
                return json.dumps({"error": "read_note requires 'path' parameter"})
            note = vault_manager.read_note(path)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "read_multiple":
            if not paths:
                return json.dumps({"error": "read_multiple requires 'paths' parameter"})
            path_list = _parse_csv(paths)
            notes = vault_manager.read_multiple(path_list)
            return json.dumps([n.model_dump(mode="json") for n in notes], default=str)

        if operation == "daily_note":
            note = vault_manager.daily_note(date or None)
            return json.dumps(note.model_dump(mode="json"), default=str)

    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"vault_read failed: {e}"})

    return json.dumps({"error": "Unexpected operation"})


@mcp.tool()
async def vault_manage(
    operation: str,
    path: str = "",
    content: str = "",
    tags: str = "",
    metadata: str = "",
    source: str = "",
    destination: str = "",
    old_text: str = "",
    new_text: str = "",
    confirm_destructive: bool = False,
) -> str:
    """Create, edit, and organize notes in the Obsidian vault.

    IMPORTANT: Delete operations require confirm_destructive=true.

    Args:
        operation: One of: create_note, append_note, edit_note, move_note, delete_note, create_folder.
        path: Target note/folder path (for create, append, edit, delete, create_folder).
        content: Note content in markdown (for create_note, append_note).
        tags: Comma-separated tags (for create_note).
        metadata: JSON string of additional frontmatter key-value pairs (for create_note).
        source: Source path (for move_note).
        destination: Destination path (for move_note).
        old_text: Text to find (for edit_note).
        new_text: Replacement text (for edit_note).
        confirm_destructive: Must be true for delete operations.
    """
    if operation not in VALID_MANAGE_OPS:
        return json.dumps(
            {"error": f"Unknown operation '{operation}'. Use: {', '.join(VALID_MANAGE_OPS)}"}
        )

    try:
        if operation == "create_note":
            if not path:
                return json.dumps({"error": "create_note requires 'path' parameter"})
            tag_list = _parse_csv(tags) if tags else None
            meta_dict = None
            if metadata:
                try:
                    meta_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    return json.dumps({"error": "metadata must be a valid JSON string"})
            note = vault_manager.write_note(path, content, tag_list, meta_dict)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "append_note":
            if not path:
                return json.dumps({"error": "append_note requires 'path' parameter"})
            if not content:
                return json.dumps({"error": "append_note requires 'content' parameter"})
            note = vault_manager.append_to_note(path, content)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "edit_note":
            if not path:
                return json.dumps({"error": "edit_note requires 'path' parameter"})
            if not old_text:
                return json.dumps({"error": "edit_note requires 'old_text' parameter"})
            note = vault_manager.edit_note(path, old_text, new_text)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "move_note":
            if not source:
                return json.dumps({"error": "move_note requires 'source' parameter"})
            if not destination:
                return json.dumps({"error": "move_note requires 'destination' parameter"})
            note = vault_manager.move_note(source, destination)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "delete_note":
            if not path:
                return json.dumps({"error": "delete_note requires 'path' parameter"})
            deleted = vault_manager.delete_note(path, confirm_destructive)
            if not deleted:
                return json.dumps({"error": "Delete requires confirm_destructive=true"})
            return json.dumps({"success": True, "message": f"Deleted {path}"})

        if operation == "create_folder":
            if not path:
                return json.dumps({"error": "create_folder requires 'path' parameter"})
            vault_manager.create_folder(path)
            return json.dumps({"success": True, "message": f"Created folder {path}"})

    except (FileNotFoundError, FileExistsError, ValueError) as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"vault_manage failed: {e}"})

    return json.dumps({"error": "Unexpected operation"})
