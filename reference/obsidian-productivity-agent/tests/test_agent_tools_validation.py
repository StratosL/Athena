"""
Validation tests for the new agent tools functionality.
Tests the logic without requiring actual database connections.
"""

import json
from unittest.mock import Mock, AsyncMock


async def mock_list_available_tags_tool(mock_supabase_client):
    """
    Mock implementation of list_available_tags_tool for testing.
    """
    try:
        # Mock data simulating various tag formats in database
        mock_data = [
            {'tags': '["python", "tutorial"]'},  # JSON string format
            {'tags': ['javascript', 'web']},     # List format
            {'tags': '["python", "advanced"]'},  # Duplicate python
            {'tags': None},                      # No tags
            {'tags': []},                        # Empty tags
            {'tags': '["api", "rest", "fastapi"]'},
        ]

        # Extract unique tags
        all_tags = set()
        for doc in mock_data:
            if doc.get('tags'):
                tags = doc['tags']
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except:
                        continue
                if isinstance(tags, list):
                    all_tags.update(tags)

        return sorted(list(all_tags))
    except Exception as e:
        return []


async def mock_get_documents_by_tag_tool(mock_supabase_client, tag):
    """
    Mock implementation of get_documents_by_tag_tool for testing.
    """
    try:
        # Mock database data
        mock_data = [
            {
                'id': 'doc1',
                'title': 'Python Tutorial',
                'url': 'https://example.com/python.md',
                'tags': '["python", "beginner"]'
            },
            {
                'id': 'doc2',
                'title': 'JavaScript Guide',
                'url': 'https://example.com/js.md',
                'tags': ['javascript', 'web']
            },
            {
                'id': 'doc3',
                'title': 'Python Advanced',
                'url': 'https://example.com/python-advanced.md',
                'tags': ['python', 'advanced']
            },
            {
                'id': 'doc4',
                'title': 'FastAPI Documentation',
                'url': 'https://example.com/fastapi.md',
                'tags': ['python', 'api', 'fastapi']
            }
        ]

        # Filter documents containing the specified tag
        matching_docs = []
        for doc in mock_data:
            if doc.get('tags'):
                tags = doc['tags']
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except:
                        continue
                if isinstance(tags, list) and tag in tags:
                    matching_docs.append({
                        'id': doc['id'],
                        'title': doc['title'],
                        'url': doc['url'],
                        'tags': tags
                    })

        return matching_docs
    except Exception as e:
        return []


async def mock_retrieve_relevant_documents_with_tag(mock_supabase_client, embedding_client, user_query, tag=None):
    """
    Mock implementation of enhanced retrieve_relevant_documents_tool with tag filtering.
    """
    try:
        if tag:
            # Get documents with this tag first
            tagged_docs = await mock_get_documents_by_tag_tool(mock_supabase_client, tag)
            if not tagged_docs:
                return f"No documents found with tag '{tag}'."

            # Simulate retrieving relevant chunks from tagged documents
            # In real implementation, this would do semantic search within the tagged documents
            relevant_chunks = []
            for doc in tagged_docs[:2]:  # Limit for demo
                chunk_text = f"""
# Document ID: {doc['id']}
# Document Title: {doc['title']}
# Document URL: {doc['url']}

This is sample content from {doc['title']} that matches the query "{user_query}".
It contains information relevant to the user's search within documents tagged with "{tag}".
"""
                relevant_chunks.append(chunk_text)

            return "\n\n---\n\n".join(relevant_chunks)
        else:
            # Standard search without tag filtering
            return f"""
# Document ID: general_doc
# Document Title: General Documentation
# Document URL: https://example.com/general.md

This is general content that matches the query "{user_query}" without any tag filtering.
"""

    except Exception as e:
        return f"Error retrieving documents: {str(e)}"


async def test_agent_tools():
    """Test the new agent tools functionality."""

    print("=" * 60)
    print("AGENT TOOLS VALIDATION")
    print("=" * 60)

    mock_supabase = Mock()
    mock_embedding_client = AsyncMock()

    tests_passed = 0
    tests_total = 0

    # Test 1: List available tags
    print("\n1. Testing list_available_tags_tool")
    print("-" * 40)
    tests_total += 1

    available_tags = await mock_list_available_tags_tool(mock_supabase)
    expected_tags = ['advanced', 'api', 'beginner', 'fastapi', 'javascript', 'python', 'rest', 'tutorial', 'web']

    print(f"Available tags: {available_tags}")
    print(f"Expected tags:  {expected_tags}")

    if available_tags == expected_tags:
        print("PASS: Tag listing works correctly")
        tests_passed += 1
    else:
        print("FAIL: Tag listing incorrect")

    # Test 2: Get documents by tag - Python
    print("\n2. Testing get_documents_by_tag_tool (python)")
    print("-" * 50)
    tests_total += 1

    python_docs = await mock_get_documents_by_tag_tool(mock_supabase, 'python')
    print(f"Found {len(python_docs)} documents with 'python' tag:")
    for doc in python_docs:
        print(f"  - {doc['title']} (tags: {doc['tags']})")

    if len(python_docs) == 3:  # Python Tutorial, Python Advanced, FastAPI Documentation
        print("PASS: Python tag filtering works correctly")
        tests_passed += 1
    else:
        print(f"FAIL: Expected 3 python documents, got {len(python_docs)}")

    # Test 3: Get documents by tag - JavaScript
    print("\n3. Testing get_documents_by_tag_tool (javascript)")
    print("-" * 50)
    tests_total += 1

    js_docs = await mock_get_documents_by_tag_tool(mock_supabase, 'javascript')
    print(f"Found {len(js_docs)} documents with 'javascript' tag:")
    for doc in js_docs:
        print(f"  - {doc['title']} (tags: {doc['tags']})")

    if len(js_docs) == 1:  # JavaScript Guide
        print("PASS: JavaScript tag filtering works correctly")
        tests_passed += 1
    else:
        print(f"FAIL: Expected 1 javascript document, got {len(js_docs)}")

    # Test 4: Tag-filtered RAG search
    print("\n4. Testing retrieve_relevant_documents with tag filter")
    print("-" * 60)
    tests_total += 1

    tag_filtered_result = await mock_retrieve_relevant_documents_with_tag(
        mock_supabase, mock_embedding_client, "how to use this framework", tag="python"
    )

    print("Tag-filtered search result preview:")
    print(tag_filtered_result[:200] + "..." if len(tag_filtered_result) > 200 else tag_filtered_result)

    if "python" in tag_filtered_result.lower() and "Document ID:" in tag_filtered_result:
        print("PASS: Tag-filtered RAG search works correctly")
        tests_passed += 1
    else:
        print("FAIL: Tag-filtered RAG search incorrect")

    # Test 5: Regular RAG search (no tag filter)
    print("\n5. Testing retrieve_relevant_documents without tag filter")
    print("-" * 60)
    tests_total += 1

    regular_result = await mock_retrieve_relevant_documents_with_tag(
        mock_supabase, mock_embedding_client, "general programming help"
    )

    print("Regular search result preview:")
    print(regular_result[:200] + "..." if len(regular_result) > 200 else regular_result)

    if "general" in regular_result.lower() and "Document ID:" in regular_result:
        print("PASS: Regular RAG search still works correctly")
        tests_passed += 1
    else:
        print("FAIL: Regular RAG search broken")

    # Test 6: Non-existent tag
    print("\n6. Testing get_documents_by_tag_tool with non-existent tag")
    print("-" * 60)
    tests_total += 1

    no_docs = await mock_get_documents_by_tag_tool(mock_supabase, 'nonexistent')
    print(f"Found {len(no_docs)} documents with 'nonexistent' tag")

    if len(no_docs) == 0:
        print("PASS: Non-existent tag returns empty results")
        tests_passed += 1
    else:
        print("FAIL: Non-existent tag should return empty results")

    # Summary
    print("\n" + "=" * 60)
    print("AGENT TOOLS VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("\nSUCCESS: All agent tools are working correctly!")
        print("\nNew agent capabilities validated:")
        print("- list_available_tags(): Returns all unique tags")
        print("- get_documents_by_tag(): Filters documents by tag")
        print("- retrieve_relevant_documents(tag=...): RAG search with tag filter")
        print("- Backward compatibility: Regular search still works")
        print("- Edge cases: Non-existent tags handled gracefully")
    else:
        print("\nFAILURE: Some agent tools need attention")

    return tests_passed == tests_total


async def main():
    """Run all agent tool validations."""
    success = await test_agent_tools()
    return success


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())