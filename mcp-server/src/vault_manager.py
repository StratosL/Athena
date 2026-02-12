"""Obsidian vault filesystem access — read, write, query, and organize notes.

This is the core class that all vault MCP tools delegate to.
Inspired by reference/obsidian-ai-agent/app/shared/vault/vault_manager.py.

Key responsibilities:
- Path validation and directory traversal prevention
- YAML frontmatter parsing and writing (via python-frontmatter)
- Note CRUD operations (create, read, append, edit, delete, move)
- Vault structure queries (list, search, recent changes)
"""
