"""Hierarchical RAG tools for the agent.

Reference: examples/tools.py - Adapted for hierarchical search.

These tools implement the hierarchical retrieval strategy:
1. list_categories - Navigate category tree (categorical hierarchy)
2. search_knowledge_base - Vector search with category filtering (both hierarchies)
3. get_chunk_context - Expand context via parent chunks (structural hierarchy)
4. get_document_overview - High-level document summary

Tools are registered with the agent via register_tools().
"""

from typing import Optional, List

from pydantic_ai import Agent, RunContext

from .dependencies import AgentDependencies
from ..db import operations as db_ops


async def list_categories(ctx: RunContext[AgentDependencies]) -> str:
    """List the full category hierarchy in the knowledge base.

    Use this to understand what topics are available and find the right
    category IDs for scoped searches.

    Returns:
        Formatted tree of categories with IDs and document counts.
    """
    if not ctx.deps.db_pool:
        await ctx.deps.initialize()

    tree = await db_ops.get_category_tree(ctx.deps.db_pool)

    # Format as indented tree
    def format_tree(nodes: List, indent: int = 0) -> List[str]:
        lines = []
        for node in nodes:
            prefix = "  " * indent
            connector = "├── " if indent > 0 else ""
            lines.append(
                f"{prefix}{connector}{node['name']} (id: {node['id']}) - "
                f"{node['doc_count']} documents"
            )
            if node.get('children'):
                lines.extend(format_tree(node['children'], indent + 1))
        return lines

    if not tree:
        return "No categories found in the knowledge base."

    return "Knowledge Base Categories:\n" + "\n".join(format_tree(tree))


async def search_knowledge_base(
    ctx: RunContext[AgentDependencies],
    query: str,
    category_ids: Optional[List[int]] = None,
    top_k: int = 5,
) -> str:
    """Search for relevant content in the knowledge base.

    Args:
        query: The search query.
        category_ids: Optional list of category IDs to search within.
                      If provided, only searches documents in those categories.
                      If None, searches across all categories.
        top_k: Number of results to return.

    Returns:
        Formatted search results with chunk IDs for context expansion.
    """
    if not ctx.deps.db_pool:
        await ctx.deps.initialize()

    # Generate embedding
    query_embedding = await ctx.deps.get_embedding(query)

    # Search chunks (pass embedding as list, pgvector handles conversion)
    results = await db_ops.search_chunks(
        ctx.deps.db_pool, query_embedding, category_ids, top_k
    )

    # Format results
    if not results:
        return "No relevant information found in the knowledge base."

    response_parts = [f"Found {len(results)} relevant chunks:\n"]
    for i, result in enumerate(results, 1):
        heading_path = result.get('heading_path', [])
        section = ' > '.join(heading_path) if heading_path else 'General'

        response_parts.append(
            f"\n--- Result {i} (similarity: {result['similarity']:.3f}) ---\n"
            f"Category: {result.get('category_name', 'Unknown')}\n"
            f"Document: {result['document_title']}\n"
            f"Document ID: {result.get('document_id', 'Unknown')}\n"
            f"Section: {section}\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Content: {result['content'][:400]}..."
        )

    return "\n".join(response_parts)


async def get_chunk_context(
    ctx: RunContext[AgentDependencies],
    chunk_id: int
) -> str:
    """Get expanded context for a chunk by retrieving its parent and siblings.

    This navigates the within-document hierarchy: if you found a relevant
    paragraph (leaf chunk), this returns the full section it belongs to
    (parent chunk) plus adjacent paragraphs (siblings).

    Args:
        chunk_id: The ID of a chunk from search results.

    Returns:
        Hierarchical context including parent section and siblings.
    """
    if not ctx.deps.db_pool:
        await ctx.deps.initialize()

    context = await db_ops.get_chunk_with_context(ctx.deps.db_pool, chunk_id)

    if not context:
        return f"No chunk found with ID {chunk_id}"

    # Format hierarchical context
    hierarchy_path = context.get('hierarchy_path', [])
    hierarchy_str = ' > '.join(hierarchy_path) if hierarchy_path else 'Document Root'

    lines = [
        f"=== Context for Chunk {chunk_id} ===\n",
        f"Document: {context.get('document_title', 'Unknown')}\n",
        f"Hierarchy: {hierarchy_str}\n",
    ]

    # Parent section
    if context.get('parent_content'):
        lines.append(f"\n--- Parent Section ---\n{context['parent_content']}\n")

    # Current chunk
    lines.append(f"\n--- Current Chunk ---\n{context['chunk_content']}\n")

    # Siblings
    siblings = context.get('siblings', [])
    if siblings:
        lines.append(f"\n--- Sibling Chunks ({len(siblings)}) ---")
        for sib in siblings[:3]:  # Show max 3 siblings
            content_preview = sib['content'][:200] + "..." if len(sib['content']) > 200 else sib['content']
            lines.append(f"\n[{sib['sequence']}] {content_preview}")

    return "\n".join(lines)


async def get_document_overview(
    ctx: RunContext[AgentDependencies],
    document_id: int
) -> str:
    """Get a high-level overview of a document.

    Includes the document summary, category path, and section structure.

    Args:
        document_id: The document ID from search results.

    Returns:
        Document overview with summary and sections.
    """
    if not ctx.deps.db_pool:
        await ctx.deps.initialize()

    doc = await db_ops.get_document_overview(ctx.deps.db_pool, document_id)

    if not doc:
        return f"No document found with ID {document_id}"

    lines = [
        f"=== Document Overview ===\n",
        f"Title: {doc['title']}",
        f"Category: {doc['category_path']}",
        f"\nSummary:\n{doc['summary']}\n",
        f"\nSections:",
    ]

    for section in doc.get('sections', []):
        lines.append(f"  - {section['heading']} ({section['chunk_count']} chunks)")

    return "\n".join(lines)


def register_tools(agent: Agent) -> Agent:
    """Register all tools with the agent.

    Args:
        agent: The agent to register tools with.

    Returns:
        The agent with tools registered.
    """
    agent.tool(list_categories)
    agent.tool(search_knowledge_base)
    agent.tool(get_chunk_context)
    agent.tool(get_document_overview)
    return agent
