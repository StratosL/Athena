"""Mock document generation for Hierarchical RAG Workshop.

This module generates realistic mock documentation for an Enterprise IT
Knowledge Base. It uses sub-agents to generate document content.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from pydantic_ai import Agent
from rich.console import Console
from rich.progress import Progress, TaskID

from .providers import get_llm_model

logger = logging.getLogger(__name__)
console = Console()


# Category taxonomy defining the knowledge base structure
CATEGORY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Infrastructure": {
        "description": "Hardware, networking, and cloud infrastructure documentation",
        "subcategories": {
            "Networking": {
                "description": "Network architecture, protocols, and configuration",
                "documents": [
                    "Network Architecture Guide",
                    "VPN Configuration",
                    "Firewall Policies"
                ]
            },
            "Cloud": {
                "description": "Cloud platform setup and migration guides",
                "documents": [
                    "AWS Setup Guide",
                    "Azure Migration Plan"
                ]
            }
        }
    },
    "Development": {
        "description": "Software development standards and practices",
        "subcategories": {
            "Python": {
                "description": "Python-specific coding practices and tooling",
                "documents": [
                    "Coding Standards",
                    "Testing Guidelines"
                ]
            },
            "API Design": {
                "description": "API architecture and design patterns",
                "documents": [
                    "REST API Design Guide",
                    "GraphQL Best Practices"
                ]
            }
        }
    },
    "Security": {
        "description": "Security compliance, policies, and incident management",
        "subcategories": {
            "Compliance": {
                "description": "Regulatory compliance frameworks and requirements",
                "documents": [
                    "GDPR Compliance Guide",
                    "SOC2 Requirements"
                ]
            },
            "Incident Response": {
                "description": "Security incident detection and response procedures",
                "documents": [
                    "Incident Response Playbook",
                    "Vulnerability Management"
                ]
            }
        }
    },
    "Operations": {
        "description": "System operations, monitoring, and deployment",
        "subcategories": {
            "Monitoring": {
                "description": "System observability and alerting configuration",
                "documents": [
                    "Observability Guide",
                    "Alerting Setup"
                ]
            },
            "Deployment": {
                "description": "CI/CD pipelines and deployment procedures",
                "documents": [
                    "CI/CD Pipeline Guide",
                    "Deployment Checklist"
                ]
            }
        }
    }
}


def slugify(text: str) -> str:
    """Convert text to URL-safe slug.

    Args:
        text: Text to convert.

    Returns:
        URL-safe slug.
    """
    return text.lower().replace(" ", "-").replace("/", "-")


# Document generation prompt template
DOCUMENT_GENERATION_PROMPT = """Generate a detailed technical documentation article.

**Document Title:** {title}
**Category:** {category}
**Subcategory:** {subcategory}
**Topic Description:** {description}

**Requirements:**
1. Use proper markdown heading hierarchy:
   - # for the document title
   - ## for major sections (4-6 sections)
   - ### for subsections (2-3 per section)

2. Include realistic technical content (800-1500 words total):
   - Specific procedures and steps
   - Configuration examples with code blocks
   - Best practices and recommendations
   - Common pitfalls and troubleshooting

3. Include where appropriate:
   - Bullet lists for requirements or steps
   - Code blocks for commands or configurations
   - Tables for comparisons or reference data

4. Write in a professional but accessible tone
5. Make content specific enough for vector search to distinguish from related documents

Generate ONLY the markdown content, no explanations or meta-commentary.
"""


async def generate_document_content(
    title: str,
    category: str,
    subcategory: str,
    description: str
) -> str:
    """Generate document content using a sub-agent.

    Args:
        title: Document title.
        category: Parent category name.
        subcategory: Subcategory name.
        description: Topic description.

    Returns:
        Generated markdown content.
    """
    # Create document generation agent
    doc_agent = Agent(
        get_llm_model(),
        system_prompt="You are a technical writer creating enterprise IT documentation."
    )

    prompt = DOCUMENT_GENERATION_PROMPT.format(
        title=title,
        category=category,
        subcategory=subcategory,
        description=description
    )

    result = await doc_agent.run(prompt)
    return result.output


async def generate_documents(docs_dir: str = "docs") -> None:
    """Generate all mock documents for the knowledge base.

    Args:
        docs_dir: Directory to save documents (default: "docs").
    """
    docs_path = Path(docs_dir)

    # Count total documents
    total_docs = sum(
        len(subcat_data["documents"])
        for cat_data in CATEGORY_TAXONOMY.values()
        for subcat_data in cat_data["subcategories"].values()
    )

    console.print(f"\n[bold blue]Generating {total_docs} mock documents...[/bold blue]\n")

    with Progress() as progress:
        task = progress.add_task("[cyan]Generating documents...", total=total_docs)

        for category, cat_data in CATEGORY_TAXONOMY.items():
            category_slug = slugify(category)
            category_desc = cat_data["description"]

            for subcategory, subcat_data in cat_data["subcategories"].items():
                subcategory_slug = slugify(subcategory)
                subcategory_desc = subcat_data["description"]

                # Create directory
                doc_dir = docs_path / category_slug / subcategory_slug
                doc_dir.mkdir(parents=True, exist_ok=True)

                for doc_title in subcat_data["documents"]:
                    doc_slug = slugify(doc_title)
                    doc_path = doc_dir / f"{doc_slug}.md"

                    # Skip if already exists
                    if doc_path.exists():
                        logger.info(f"Skipping existing: {doc_path}")
                        progress.advance(task)
                        continue

                    console.print(f"  Generating: [green]{doc_title}[/green]")

                    try:
                        # Generate content using sub-agent
                        content = await generate_document_content(
                            title=doc_title,
                            category=category,
                            subcategory=subcategory,
                            description=f"{category_desc}. {subcategory_desc}"
                        )

                        # Save document
                        doc_path.write_text(content, encoding="utf-8")
                        logger.info(f"Created: {doc_path}")

                    except Exception as e:
                        logger.error(f"Failed to generate {doc_title}: {e}")
                        # Create placeholder on error
                        doc_path.write_text(
                            f"# {doc_title}\n\nDocument generation failed. Please regenerate.",
                            encoding="utf-8"
                        )

                    progress.advance(task)

    console.print(f"\n[bold green]Generated {total_docs} documents in {docs_dir}/[/bold green]")


def get_category_taxonomy() -> Dict[str, Dict[str, Any]]:
    """Get the category taxonomy for use in ingestion.

    Returns:
        Category taxonomy dictionary.
    """
    return CATEGORY_TAXONOMY


async def main():
    """Entry point for document generation."""
    logging.basicConfig(level=logging.INFO)
    await generate_documents()


if __name__ == "__main__":
    asyncio.run(main())
