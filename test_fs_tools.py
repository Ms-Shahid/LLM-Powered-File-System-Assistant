import unittest
import os
import sys
import tempfile
import shutil
from fs_tools import read_file, list_files, write_file, search_in_file


class TestFileOperations(unittest.TestCase):
    """Test suite for file operations"""

    def setUp(self):
        """Set up test fixtures before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.sample_dir = os.path.join(
            os.path.dirname(__file__), "sample_files"
        )

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # ============ READ_FILE TESTS ============
    def test_read_file_success(self):
        """Test reading an existing file successfully"""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        content = "Hello, World!"
        with open(test_file, "w") as f:
            f.write(content)

        # Read the file
        result = read_file(test_file)
        self.assertIsNotNone(result)
        self.assertIn(content, str(result))

    def test_read_file_from_sample(self):
        """Test reading from sample files"""
        resume_file = os.path.join(self.sample_dir, "resume.txt")
        if os.path.exists(resume_file):
            result = read_file(resume_file)
            self.assertIsNotNone(result)
            self.assertTrue(len(str(result)) > 0)

    def test_read_file_empty_file(self):
        """Test reading an empty file"""
        test_file = os.path.join(self.test_dir, "empty.txt")
        with open(test_file, "w") as f:
            f.write("")

        result = read_file(test_file)
        self.assertIsNotNone(result)

    def test_read_file_nonexistent(self):
        """Test reading a file that doesn't exist"""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        result = read_file(nonexistent)
        self.assertIsNone(result)

    def test_read_file_multiline_content(self):
        """Test reading file with multiple lines"""
        test_file = os.path.join(self.test_dir, "multiline.txt")
        content = "Line 1\nLine 2\nLine 3\n"
        with open(test_file, "w") as f:
            f.write(content)

        result = read_file(test_file)
        self.assertIsNotNone(result)

    # ============ LIST_FILES TESTS ============
    def test_list_files_all_files(self):
        """Test listing all files in a directory"""
        # Create test files
        open(os.path.join(self.test_dir, "file1.txt"), "w").close()
        open(os.path.join(self.test_dir, "file2.txt"), "w").close()
        open(os.path.join(self.test_dir, "file3.pdf"), "w").close()

        result = list_files(self.test_dir)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    def test_list_files_with_extension_filter(self):
        """Test listing files with specific extension"""
        # Create test files
        open(os.path.join(self.test_dir, "file1.txt"), "w").close()
        open(os.path.join(self.test_dir, "file2.txt"), "w").close()
        open(os.path.join(self.test_dir, "file3.pdf"), "w").close()

        result = list_files(self.test_dir, ".txt")
        self.assertIsNotNone(result)
        if result:
            for file in result:
                self.assertTrue(file.endswith(".txt"))

    def test_list_files_empty_directory(self):
        """Test listing files in empty directory"""
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir)

        result = list_files(empty_dir)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    def test_list_files_nonexistent_directory(self):
        """Test listing files in nonexistent directory"""
        nonexistent = os.path.join(self.test_dir, "nonexistent")
        result = list_files(nonexistent)
        self.assertEqual(result, [])

    def test_list_files_sample_directory(self):
        """Test listing files from sample directory"""
        if os.path.exists(self.sample_dir):
            result = list_files(self.sample_dir)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)

    def test_list_files_with_mixed_extensions(self):
        """Test listing with various file extensions"""
        open(os.path.join(self.test_dir, "doc.txt"), "w").close()
        open(os.path.join(self.test_dir, "data.csv"), "w").close()
        open(os.path.join(self.test_dir, "image.jpg"), "w").close()

        result_txt = list_files(self.test_dir, ".txt")
        result_csv = list_files(self.test_dir, ".csv")

        if result_txt:
            self.assertTrue(any("txt" in f for f in result_txt))

    # ============ WRITE_FILE TESTS ============
    def test_write_file_success(self):
        """Test writing to a new file"""
        test_file = os.path.join(self.test_dir, "new_file.txt")
        content = "Test content"

        result = write_file(test_file, content)
        self.assertIsNotNone(result)
        self.assertTrue(result.get("success"))
        self.assertTrue(os.path.exists(test_file))

    def test_write_file_creates_directories(self):
        """Test that write_file creates missing directories"""
        nested_path = os.path.join(
            self.test_dir, "nested", "deep", "path", "file.txt"
        )
        content = "Nested content"

        result = write_file(nested_path, content)
        self.assertTrue(result.get("success"))
        self.assertTrue(os.path.exists(nested_path))

    def test_write_file_overwrite_existing(self):
        """Test overwriting an existing file"""
        test_file = os.path.join(self.test_dir, "existing.txt")
        
        # Write initial content
        write_file(test_file, "Original content")
        
        # Overwrite with new content
        new_content = "New content"
        result = write_file(test_file, new_content)
        
        self.assertTrue(result.get("success"))
        with open(test_file, "r") as f:
            actual_content = f.read()
        self.assertEqual(actual_content, new_content)

    def test_write_file_empty_content(self):
        """Test writing empty content to a file"""
        test_file = os.path.join(self.test_dir, "empty_write.txt")
        result = write_file(test_file, "")
        
        self.assertTrue(result.get("success"))
        self.assertTrue(os.path.exists(test_file))

    def test_write_file_large_content(self):
        """Test writing large content to a file"""
        test_file = os.path.join(self.test_dir, "large.txt")
        large_content = "x" * 100000  # 100KB of data

        result = write_file(test_file, large_content)
        self.assertTrue(result.get("success"))

    def test_write_file_special_characters(self):
        """Test writing content with special characters"""
        test_file = os.path.join(self.test_dir, "special.txt")
        content = "Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?\n"

        result = write_file(test_file, content)
        self.assertTrue(result.get("success"))

    def test_write_file_unicode_content(self):
        """Test writing unicode content"""
        test_file = os.path.join(self.test_dir, "unicode.txt")
        content = "Unicode: 你好世界 🚀 Ñoño"

        result = write_file(test_file, content)
        self.assertTrue(result.get("success"))

    # ============ SEARCH_IN_FILE TESTS ============
    def test_search_in_file_found(self):
        """Test searching for a keyword that exists"""
        test_file = os.path.join(self.test_dir, "search_test.txt")
        content = "The quick brown fox jumps over the lazy dog"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "brown")
        self.assertIsNotNone(result)
        self.assertTrue(result.get("found"))
        self.assertIn("context", result)

    def test_search_in_file_not_found(self):
        """Test searching for a keyword that doesn't exist"""
        test_file = os.path.join(self.test_dir, "search_test.txt")
        content = "The quick brown fox jumps over the lazy dog"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "elephant")
        self.assertIsNotNone(result)
        self.assertFalse(result.get("found"))

    def test_search_in_file_case_insensitive(self):
        """Test case-insensitive search"""
        test_file = os.path.join(self.test_dir, "search_case.txt")
        content = "The Python Programming Language"
        with open(test_file, "w") as f:
            f.write(content)

        # Search with different case
        result = search_in_file(test_file, "python")
        self.assertTrue(result.get("found"))

    def test_search_in_file_with_context(self):
        """Test that context is returned with search"""
        test_file = os.path.join(self.test_dir, "context_test.txt")
        content = "Before keyword After"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "keyword")
        self.assertTrue(result.get("found"))
        self.assertIn("context", result)
        # Context should include the keyword
        self.assertIn("keyword", result.get("context", "").lower())

    def test_search_in_file_at_start(self):
        """Test searching for keyword at the start of file"""
        test_file = os.path.join(self.test_dir, "search_start.txt")
        content = "Start of the content"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "Start")
        self.assertTrue(result.get("found"))

    def test_search_in_file_at_end(self):
        """Test searching for keyword at the end of file"""
        test_file = os.path.join(self.test_dir, "search_end.txt")
        content = "The content ends here"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "here")
        self.assertTrue(result.get("found"))

    def test_search_in_file_nonexistent(self):
        """Test searching in a nonexistent file"""
        nonexistent = os.path.join(self.test_dir, "nonexistent_search.txt")
        result = search_in_file(nonexistent, "keyword")
        self.assertFalse(result.get("found"))

    def test_search_in_file_with_sample_files(self):
        """Test searching in actual sample files"""
        resume_file = os.path.join(self.sample_dir, "resume.txt")
        if os.path.exists(resume_file):
            result = search_in_file(resume_file, "engineer")
            self.assertIsNotNone(result)

    def test_search_in_file_multiline_context(self):
        """Test search with context spanning multiple characters"""
        test_file = os.path.join(self.test_dir, "multiline_context.txt")
        content = "Line 1\nLine 2 with target word\nLine 3"
        with open(test_file, "w") as f:
            f.write(content)

        result = search_in_file(test_file, "target")
        self.assertTrue(result.get("found"))
        context = result.get("context", "")
        self.assertIn("target", context.lower())


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
