"""Skills MCP tool — discover, load, and manage reusable multi-step workflows.

Skills are markdown files stored in Meta/Skills/ in the Obsidian vault.
Each skill has YAML frontmatter (title, tags, trigger_phrases) and structured steps
that reference existing Athena tools.

Single tool with operation-based dispatch, following the vault_query/vault_read/vault_manage pattern:
- skill_manager: list_skills, load_skill, create_skill, edit_skill, delete_skill
"""

import json
import logging
from datetime import UTC, datetime

import frontmatter

from src.server import mcp, vault_manager

logger = logging.getLogger(__name__)

SKILLS_FOLDER = "Meta/Skills"
VALID_OPS = ("list_skills", "load_skill", "create_skill", "edit_skill", "delete_skill")


def _skill_path(name: str) -> str:
    """Build the vault-relative path for a skill by name."""
    clean = name.removesuffix(".md")
    return f"{SKILLS_FOLDER}/{clean}.md"


def _list_skill_files() -> list[dict]:
    """Scan Meta/Skills/*.md and extract frontmatter metadata from each."""
    skills: list[dict] = []
    vault_root = vault_manager.vault_root
    skills_dir = vault_root / SKILLS_FOLDER

    if not skills_dir.is_dir():
        return skills

    for skill_file in sorted(skills_dir.glob("*.md")):
        try:
            post = frontmatter.loads(skill_file.read_text(encoding="utf-8"))
            skills.append({
                "name": skill_file.stem,
                "title": post.metadata.get("title", skill_file.stem),
                "trigger_phrases": post.metadata.get("trigger_phrases", []),
                "tags": post.metadata.get("tags", []),
            })
        except Exception:
            logger.warning("Failed to parse skill file: %s", skill_file, exc_info=True)

    return skills


@mcp.tool()
async def skill_manager(
    operation: str,
    name: str = "",
    content: str = "",
    description: str = "",
    trigger_phrases: str = "",
    confirm_destructive: bool = False,
) -> str:
    """Manage reusable multi-step workflow skills stored in the vault.

    Skills are markdown files in Meta/Skills/ with structured steps referencing existing tools.

    Args:
        operation: One of: list_skills, load_skill, create_skill, edit_skill, delete_skill.
        name: Skill filename without .md (for load, create, edit, delete).
        content: Markdown body with ## Steps section (for create_skill, edit_skill).
        description: Brief description of the skill (for create_skill).
        trigger_phrases: Comma-separated phrases that activate this skill (for create_skill).
        confirm_destructive: Must be true for delete operations.
    """
    if operation not in VALID_OPS:
        return json.dumps(
            {"error": f"Unknown operation '{operation}'. Use: {', '.join(VALID_OPS)}"}
        )

    try:
        if operation == "list_skills":
            skills = _list_skill_files()
            return json.dumps({"skills": skills, "count": len(skills)})

        if operation == "load_skill":
            if not name:
                return json.dumps({"error": "load_skill requires 'name' parameter"})
            note = vault_manager.read_note(_skill_path(name))
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "create_skill":
            if not name:
                return json.dumps({"error": "create_skill requires 'name' parameter"})
            if not content:
                return json.dumps({"error": "create_skill requires 'content' parameter"})

            # Ensure the Skills folder exists
            vault_manager.create_folder(SKILLS_FOLDER)

            # Build frontmatter metadata
            phrases = [p.strip() for p in trigger_phrases.split(",") if p.strip()]
            metadata = {
                "trigger_phrases": phrases,
                "created": datetime.now(UTC).strftime("%Y-%m-%d"),
            }
            if description:
                metadata["description"] = description

            tags = ["skill"]
            note = vault_manager.write_note(_skill_path(name), content, tags, metadata)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "edit_skill":
            if not name:
                return json.dumps({"error": "edit_skill requires 'name' parameter"})
            if not content:
                return json.dumps({"error": "edit_skill requires 'content' parameter"})

            path = _skill_path(name)

            # Read existing note to preserve frontmatter
            existing = vault_manager.read_note(path)
            old_metadata = existing.metadata.copy()

            # Delete old and write new with preserved metadata
            vault_manager.delete_note(path, confirm_destructive=True)
            tags = old_metadata.pop("tags", ["skill"])
            note = vault_manager.write_note(path, content, tags, old_metadata)
            return json.dumps(note.model_dump(mode="json"), default=str)

        if operation == "delete_skill":
            if not name:
                return json.dumps({"error": "delete_skill requires 'name' parameter"})
            deleted = vault_manager.delete_note(_skill_path(name), confirm_destructive)
            if not deleted:
                return json.dumps({"error": "Delete requires confirm_destructive=true"})
            return json.dumps({"success": True, "message": f"Deleted skill '{name}'"})

    except FileNotFoundError as e:
        return json.dumps({"error": str(e)})
    except FileExistsError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"skill_manager failed: {e}"})

    return json.dumps({"error": "Unexpected operation"})
