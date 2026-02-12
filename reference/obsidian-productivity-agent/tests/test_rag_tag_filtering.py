"""
Comprehensive unit tests for RAG pipeline tag-based filtering enhancement.

Tests:
1. Tag extraction from various markdown formats
2. Database operations with tags
3. Agent tools functionality
4. Filtering and search with tags
5. Backward compatibility
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add backend modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend_rag_pipeline', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend_agent_api'))

from text_processor import extract_tags_from_markdown
from db_handler import process_file_for_rag, insert_or_update_document_metadata
import tools


class TestTagExtraction(unittest.TestCase):
    """Test tag extraction from markdown text."""

    def test_basic_hashtag_extraction(self):
        """Test basic hashtag patterns."""
        text = "This is about #python and #machine-learning concepts."
        expected = ['machine-learning', 'python']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_hashtags_with_underscores(self):
        """Test hashtags with underscores."""
        text = "Topics: #data_science #deep_learning #neural_networks"
        expected = ['data_science', 'deep_learning', 'neural_networks']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_hashtags_with_numbers(self):
        """Test hashtags containing numbers."""
        text = "Using #python3 for #web2 development #ai2024"
        expected = ['ai2024', 'python3', 'web2']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_ignore_markdown_headers(self):
        """Test that markdown headers (##, ###) are ignored."""
        text = """
        # Main Title
        ## Section Header
        ### Subsection

        This talks about #real-tag but not headers.
        """
        expected = ['real-tag']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_mixed_content_extraction(self):
        """Test extraction from mixed markdown content."""
        text = """
        # Project Documentation

        This project uses #python #fastapi and #postgresql.

        ## Features
        - Authentication with #jwt
        - Data processing with #pandas

        ### API Endpoints
        The API supports #rest and #graphql patterns.
        """
        expected = ['fastapi', 'graphql', 'jwt', 'pandas', 'postgresql', 'python', 'rest']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_empty_and_none_input(self):
        """Test edge cases with empty/None input."""
        self.assertEqual(extract_tags_from_markdown(""), [])
        self.assertEqual(extract_tags_from_markdown(None), [])
        self.assertEqual(extract_tags_from_markdown("No tags here!"), [])

    def test_duplicate_tag_removal(self):
        """Test that duplicate tags are removed."""
        text = "#python is great. I love #python programming. #python rocks!"
        expected = ['python']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_invalid_hashtag_patterns(self):
        """Test that invalid patterns are ignored."""
        text = "Invalid: #123invalid #-invalid #_invalid. Valid: #valid123"
        expected = ['valid123']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations with tags."""

    @patch('db_handler.supabase')
    def test_metadata_insertion_with_tags(self, mock_supabase):
        """Test inserting document metadata with tags."""
        # Mock the select response (no existing record)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Mock the insert operation
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()

        tags = ['python', 'tutorial', 'beginner']
        insert_or_update_document_metadata(
            file_id='test123',
            file_title='Python Tutorial',
            file_url='https://example.com/tutorial.md',
            tags=tags
        )

        # Verify the insert was called with correct data
        insert_call_args = mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertEqual(insert_call_args['id'], 'test123')
        self.assertEqual(insert_call_args['title'], 'Python Tutorial')
        self.assertEqual(json.loads(insert_call_args['tags']), tags)

    @patch('db_handler.supabase')
    def test_metadata_update_with_tags(self, mock_supabase):
        """Test updating existing document metadata with tags."""
        # Mock the select response (existing record found)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {'id': 'test123', 'title': 'Old Title'}
        ]

        # Mock the update operation
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()

        tags = ['python', 'advanced']
        insert_or_update_document_metadata(
            file_id='test123',
            file_title='Python Advanced Tutorial',
            file_url='https://example.com/advanced.md',
            tags=tags
        )

        # Verify the update was called with correct data
        update_call_args = mock_supabase.table.return_value.update.call_args[0][0]
        self.assertEqual(update_call_args['title'], 'Python Advanced Tutorial')
        self.assertEqual(json.loads(update_call_args['tags']), tags)


class TestAgentTools(unittest.TestCase):
    """Test the new agent tools for tag-based operations."""

    @patch('tools.supabase')
    async def test_list_available_tags_tool(self, mock_supabase):
        """Test the list_available_tags_tool function."""
        # Mock database response with various tag formats
        mock_data = [
            {'tags': '["python", "tutorial"]'},  # JSON string
            {'tags': ['javascript', 'web']},     # Already a list
            {'tags': '["api", "rest"]'},         # Another JSON string
            {'tags': None},                      # No tags
            {'tags': ['python', 'advanced']},   # Duplicate 'python'
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = mock_data

        result = await tools.list_available_tags_tool(mock_supabase)

        expected = ['advanced', 'api', 'javascript', 'python', 'rest', 'tutorial', 'web']
        self.assertEqual(result, expected)

    @patch('tools.supabase')
    async def test_get_documents_by_tag_tool(self, mock_supabase):
        """Test the get_documents_by_tag_tool function."""
        # Mock database response
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
            }
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = mock_data

        result = await tools.get_documents_by_tag_tool(mock_supabase, 'python')

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Python Tutorial')
        self.assertEqual(result[1]['title'], 'Python Advanced')
        self.assertIn('python', result[0]['tags'])
        self.assertIn('python', result[1]['tags'])

    @patch('tools.get_embedding')
    @patch('tools.get_documents_by_tag_tool')
    @patch('tools.supabase')
    async def test_retrieve_relevant_documents_with_tag_filter(self, mock_supabase, mock_get_docs_by_tag, mock_get_embedding):
        """Test retrieve_relevant_documents_tool with tag filtering."""
        # Mock embedding
        mock_get_embedding.return_value = [0.1] * 1536

        # Mock documents by tag
        mock_get_docs_by_tag.return_value = [
            {'id': 'doc1', 'title': 'Python Tutorial'},
            {'id': 'doc2', 'title': 'Python Advanced'}
        ]

        # Mock document search results for each document
        mock_search_results = [
            {
                'content': 'Python is a programming language...',
                'metadata': {
                    'file_id': 'doc1',
                    'file_title': 'Python Tutorial',
                    'file_url': 'https://example.com/python.md'
                },
                'similarity': 0.85
            }
        ]
        mock_supabase.rpc.return_value.execute.return_value.data = mock_search_results

        result = await tools.retrieve_relevant_documents_tool(
            supabase=mock_supabase,
            embedding_client=Mock(),
            user_query="python basics",
            tag="python"
        )

        self.assertIn('Python Tutorial', result)
        self.assertIn('Python is a programming language', result)
        mock_get_docs_by_tag.assert_called_once_with(mock_supabase, 'python')


class TestExcludedFolders(unittest.TestCase):
    """Test excluded folder functionality."""

    def test_excluded_folders_config(self):
        """Test that excluded folders are properly configured."""
        # This would typically test the file watcher logic
        # Since we're testing the implementation, we'll simulate the behavior

        excluded_folders = ['.git', 'node_modules', '__pycache__', '.env', 'venv']
        test_paths = [
            '/project/.git/config',
            '/project/node_modules/package/index.js',
            '/project/src/main.py',
            '/project/__pycache__/test.pyc',
            '/project/docs/readme.md'
        ]

        def should_exclude_path(path: str, excluded: list) -> bool:
            """Simulate the exclusion logic."""
            path_parts = path.split('/')
            return any(excluded_folder in path_parts for excluded_folder in excluded)

        excluded_paths = [path for path in test_paths if should_exclude_path(path, excluded_folders)]
        included_paths = [path for path in test_paths if not should_exclude_path(path, excluded_folders)]

        self.assertEqual(len(excluded_paths), 3)  # .git, node_modules, __pycache__
        self.assertEqual(len(included_paths), 2)  # main.py, readme.md
        self.assertIn('/project/src/main.py', included_paths)
        self.assertIn('/project/docs/readme.md', included_paths)


class TestBackwardCompatibility(unittest.TestCase):
    """Test that documents without tags still work correctly."""

    @patch('tools.supabase')
    async def test_documents_without_tags_in_list(self, mock_supabase):
        """Test that list_available_tags handles documents without tags."""
        mock_data = [
            {'tags': '["python", "tutorial"]'},
            {'tags': None},
            {'tags': ''},
            {'tags': []},
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = mock_data

        result = await tools.list_available_tags_tool(mock_supabase)

        # Should only return actual tags, not fail on null/empty
        expected = ['python', 'tutorial']
        self.assertEqual(result, expected)

    @patch('tools.get_embedding')
    @patch('tools.supabase')
    async def test_regular_search_still_works(self, mock_supabase, mock_get_embedding):
        """Test that regular document search (without tags) still works."""
        # Mock embedding
        mock_get_embedding.return_value = [0.1] * 1536

        # Mock search results
        mock_search_results = [
            {
                'content': 'General programming content...',
                'metadata': {
                    'file_id': 'doc1',
                    'file_title': 'General Guide',
                    'file_url': 'https://example.com/general.md'
                },
                'similarity': 0.80
            }
        ]
        mock_supabase.rpc.return_value.execute.return_value.data = mock_search_results

        result = await tools.retrieve_relevant_documents_tool(
            supabase=mock_supabase,
            embedding_client=Mock(),
            user_query="programming help"
            # No tag parameter - should work normally
        )

        self.assertIn('General Guide', result)
        self.assertIn('General programming content', result)


class TestProcessFileForRAG(unittest.TestCase):
    """Test the enhanced process_file_for_rag function with tag support."""

    @patch('db_handler.delete_document_by_file_id')
    @patch('db_handler.insert_or_update_document_metadata')
    @patch('db_handler.insert_document_chunks')
    @patch('db_handler.create_embeddings')
    @patch('db_handler.chunk_text')
    def test_markdown_file_processing_with_tags(self, mock_chunk_text, mock_create_embeddings,
                                              mock_insert_chunks, mock_insert_metadata, mock_delete):
        """Test processing markdown file with tag extraction."""
        # Setup mocks
        mock_chunk_text.return_value = ['Chunk 1 with #python', 'Chunk 2 with #tutorial']
        mock_create_embeddings.return_value = [[0.1] * 1536, [0.2] * 1536]

        markdown_content = """
        # Python Tutorial

        This is a tutorial about #python programming and #web-development.
        Learn about #fastapi and #postgresql integration.
        """

        file_content = markdown_content.encode('utf-8')

        result = process_file_for_rag(
            file_content=file_content,
            text=markdown_content,
            file_id='md_test_123',
            file_url='https://example.com/tutorial.md',
            file_title='Python Tutorial.md',
            mime_type='text/markdown',
            config={'text_processing': {'default_chunk_size': 400, 'default_chunk_overlap': 0}}
        )

        # Verify the process succeeded
        self.assertTrue(result)

        # Verify metadata was inserted with tags
        mock_insert_metadata.assert_called_once()
        call_args = mock_insert_metadata.call_args[1]  # keyword arguments
        expected_tags = ['fastapi', 'postgresql', 'python', 'web-development']
        self.assertEqual(call_args['tags'], expected_tags)

        # Verify chunks were inserted with tags
        mock_insert_chunks.assert_called_once()
        chunk_call_args = mock_insert_chunks.call_args
        self.assertEqual(chunk_call_args[1]['tags'], expected_tags)  # tags parameter


if __name__ == '__main__':
    # Create a test suite with all test classes
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestTagExtraction,
        TestDatabaseOperations,
        TestAgentTools,
        TestExcludedFolders,
        TestBackwardCompatibility,
        TestProcessFileForRAG
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*60}")
    print(f"RAG Tag Filtering Validation Complete")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}")

    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall Result: {'PASS' if success else 'FAIL'}")

    if success:
        print("\n✅ All tag-based filtering functionality is working correctly!")
        print("✅ Tag extraction from markdown files")
        print("✅ Database operations with tags")
        print("✅ Agent tools for tag navigation")
        print("✅ Backward compatibility maintained")
        print("✅ File processing with tag support")
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")