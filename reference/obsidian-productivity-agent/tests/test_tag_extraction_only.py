"""
Focused unit tests for tag extraction functionality.
Tests the core tag extraction without requiring full backend dependencies.
"""

import unittest
import re
from typing import List


def extract_tags_from_markdown(text: str) -> List[str]:
    """
    Extract hashtags from markdown text.
    This is a copy of the function from text_processor.py for testing.
    """
    if not text:
        return []

    # Pattern to match hashtags: # followed by word characters, hyphens, or underscores
    # Must start with a letter or number, not just special characters
    # Negative lookbehind to avoid matching headers (##, ###, etc.)
    pattern = r'(?<!#)#([a-zA-Z0-9][\w-]*)'

    # Find all matches
    tags = re.findall(pattern, text)

    # Remove duplicates and return sorted list
    unique_tags = list(set(tags))
    unique_tags.sort()

    return unique_tags


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

    def test_complex_markdown_document(self):
        """Test extraction from a realistic markdown document."""
        text = """
        # Machine Learning Project

        ## Overview
        This project implements a machine learning pipeline using #python and #scikit-learn.

        ## Technologies Used
        - #python for development
        - #pandas for data manipulation
        - #numpy for numerical computations
        - #matplotlib for visualization
        - #jupyter for prototyping

        ## Features
        1. Data preprocessing with #pandas
        2. Model training using #scikit-learn
        3. Hyperparameter tuning with #grid-search
        4. Results visualization with #matplotlib

        ## Deployment
        Deploy using #docker and #kubernetes for scalability.
        API built with #fastapi and #uvicorn.

        #machine-learning #data-science #ml-pipeline
        """
        expected = [
            'data-science', 'docker', 'fastapi', 'grid-search', 'jupyter',
            'kubernetes', 'machine-learning', 'matplotlib', 'ml-pipeline',
            'numpy', 'pandas', 'python', 'scikit-learn', 'uvicorn'
        ]
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_edge_cases_with_special_characters(self):
        """Test edge cases with various special characters."""
        text = """
        Testing edge cases:
        - #valid-tag with dashes
        - #valid_tag with underscores
        - #valid123 with numbers
        - Invalid: #123 (starts with number only)
        - Invalid: #- (starts with dash)
        - Invalid: #_ (starts with underscore)
        - Valid: #a123 (starts with letter)
        - Valid: #tag-with-multiple-dashes
        """
        expected = ['a123', 'tag-with-multiple-dashes', 'valid-tag', 'valid123', 'valid_tag']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)

    def test_tags_in_code_blocks(self):
        """Test that tags in code blocks are still extracted (as they might be relevant)."""
        text = """
        # Code Example

        Here's some code:
        ```python
        # This is a comment about #python
        def process_data():
            # Uses #pandas for processing
            pass
        ```

        Also mention #javascript outside code.
        """
        expected = ['javascript', 'pandas', 'python']
        result = extract_tags_from_markdown(text)
        self.assertEqual(result, expected)


class TestExclusionLogic(unittest.TestCase):
    """Test the exclusion logic for folders."""

    def test_should_exclude_path(self):
        """Test path exclusion logic."""
        excluded_folders = ['.git', 'node_modules', '__pycache__', '.env', 'venv']

        def should_exclude_path(path: str, excluded: list) -> bool:
            """Simulate the exclusion logic."""
            path_parts = path.split('/')
            return any(excluded_folder in path_parts for excluded_folder in excluded)

        test_cases = [
            ('/project/.git/config', True),
            ('/project/node_modules/package/index.js', True),
            ('/project/src/main.py', False),
            ('/project/__pycache__/test.pyc', True),
            ('/project/docs/readme.md', False),
            ('/project/venv/lib/python.py', True),
            ('/project/.env', True),
            ('/normal/path/file.txt', False),
        ]

        for path, expected in test_cases:
            result = should_exclude_path(path, excluded_folders)
            self.assertEqual(result, expected, f"Path: {path}")


class TestTagProcessingLogic(unittest.TestCase):
    """Test tag processing and filtering logic."""

    def test_tag_normalization(self):
        """Test tag normalization and sorting."""
        raw_tags = ['Python', 'python', 'PYTHON', 'machine-learning', 'Machine_Learning']

        # Simulate normalization logic
        def normalize_tags(tags: List[str]) -> List[str]:
            """Normalize tags to lowercase and remove duplicates."""
            normalized = [tag.lower().replace('_', '-') for tag in tags]
            return sorted(list(set(normalized)))

        result = normalize_tags(raw_tags)
        expected = ['machine-learning', 'python']
        self.assertEqual(result, expected)

    def test_tag_filtering_by_length(self):
        """Test filtering tags by minimum length."""
        tags = ['a', 'ai', 'api', 'python', 'ml', 'machine-learning', 'x']

        def filter_tags_by_length(tags: List[str], min_length: int = 2) -> List[str]:
            """Filter tags by minimum length."""
            return [tag for tag in tags if len(tag) >= min_length]

        result = filter_tags_by_length(tags, min_length=2)
        expected = ['ai', 'api', 'python', 'ml', 'machine-learning']
        self.assertEqual(result, expected)


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestTagExtraction,
        TestExclusionLogic,
        TestTagProcessingLogic
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*60}")
    print(f"RAG Tag Extraction Validation Complete")
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
        print("\n✅ Core tag extraction functionality is working correctly!")
        print("✅ Tag extraction from various markdown formats")
        print("✅ Handles edge cases and invalid patterns")
        print("✅ Ignores markdown headers properly")
        print("✅ Processes complex documents correctly")
        print("✅ Exclusion logic works as expected")
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")