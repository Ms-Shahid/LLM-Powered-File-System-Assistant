"""
Test suite for LLM File Assistant

Tests the integration of OpenAI GPT-4o-mini with fs_tools functions.
Note: These tests require a valid OPENAI_API_KEY environment variable.
"""

import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from llm_file_assistant import LLMFileAssistant, tool_call


class TestLLMFileAssistant(unittest.TestCase):
    """Test suite for LLMFileAssistant class"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.environ.get("OPENAI_API_KEY", "test_key")
        # Mock the OpenAI client for testing without making actual API calls
        self.mock_client = Mock()

    def test_assistant_initialization_with_api_key(self):
        """Test LLMFileAssistant initialization with explicit API key"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            self.assertEqual(assistant.api_key, "test_key")
            self.assertEqual(assistant.model, "gpt-4o-mini")

    def test_assistant_initialization_from_env(self):
        """Test LLMFileAssistant initialization from environment variable"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
            with patch('llm_file_assistant.OpenAI') as mock_openai:
                assistant = LLMFileAssistant()
                self.assertEqual(assistant.api_key, "env_key")

    def test_assistant_initialization_no_key(self):
        """Test LLMFileAssistant raises error when no API key available"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            with self.assertRaises(ValueError) as context:
                LLMFileAssistant()
            self.assertIn("OPENAI_API_KEY", str(context.exception))

    def test_tools_definition_exists(self):
        """Test that tools are properly defined"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            tools = assistant.tools

            # Check we have 4 tools
            self.assertEqual(len(tools), 4)

            # Extract tool names
            tool_names = [tool["function"]["name"] for tool in tools]
            expected_tools = ["read_file", "list_files", "write_file", "search_in_file"]

            # Verify all expected tools are present
            for expected_tool in expected_tools:
                self.assertIn(expected_tool, tool_names)

    def test_tools_have_descriptions(self):
        """Test that all tools have descriptions"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            tools = assistant.tools

            for tool in tools:
                self.assertIn("description", tool["function"])
                self.assertTrue(len(tool["function"]["description"]) > 0)

    def test_tools_have_parameters(self):
        """Test that all tools have proper parameter definitions"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            tools = assistant.tools

            for tool in tools:
                params = tool["function"]["parameters"]
                self.assertEqual(params["type"], "object")
                self.assertIn("properties", params)
                self.assertIn("required", params)

    def test_read_file_tool_definition(self):
        """Test read_file tool definition"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            read_file_tool = next(
                (t for t in assistant.tools if t["function"]["name"] == "read_file"),
                None
            )

            self.assertIsNotNone(read_file_tool)
            params = read_file_tool["function"]["parameters"]
            self.assertIn("filepath", params["properties"])
            self.assertIn("filepath", params["required"])

    def test_list_files_tool_definition(self):
        """Test list_files tool definition"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            list_files_tool = next(
                (t for t in assistant.tools if t["function"]["name"] == "list_files"),
                None
            )

            self.assertIsNotNone(list_files_tool)
            params = list_files_tool["function"]["parameters"]
            self.assertIn("directory", params["properties"])
            self.assertIn("extension", params["properties"])
            self.assertIn("directory", params["required"])

    def test_write_file_tool_definition(self):
        """Test write_file tool definition"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            write_file_tool = next(
                (t for t in assistant.tools if t["function"]["name"] == "write_file"),
                None
            )

            self.assertIsNotNone(write_file_tool)
            params = write_file_tool["function"]["parameters"]
            self.assertIn("filepath", params["properties"])
            self.assertIn("content", params["properties"])
            self.assertEqual(set(params["required"]), {"filepath", "content"})

    def test_search_in_file_tool_definition(self):
        """Test search_in_file tool definition"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            search_tool = next(
                (t for t in assistant.tools if t["function"]["name"] == "search_in_file"),
                None
            )

            self.assertIsNotNone(search_tool)
            params = search_tool["function"]["parameters"]
            self.assertIn("filepath", params["properties"])
            self.assertIn("keyword", params["properties"])
            self.assertEqual(set(params["required"]), {"filepath", "keyword"})

    @patch('llm_file_assistant.read_file')
    def test_execute_tool_read_file(self, mock_read):
        """Test executing read_file tool"""
        mock_read.return_value = {"content": "test content", "filepath": "/test/file.txt"}

        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            result = assistant._execute_tool("read_file", {"filepath": "/test/file.txt"})

            mock_read.assert_called_once_with("/test/file.txt")
            self.assertEqual(result["content"], "test content")

    @patch('llm_file_assistant.list_files')
    def test_execute_tool_list_files(self, mock_list):
        """Test executing list_files tool"""
        mock_list.return_value = ["file1.txt", "file2.txt"]

        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            result = assistant._execute_tool(
                "list_files",
                {"directory": "/test", "extension": ".txt"}
            )

            mock_list.assert_called_once_with("/test", ".txt")
            self.assertEqual(result, ["file1.txt", "file2.txt"])

    @patch('llm_file_assistant.write_file')
    def test_execute_tool_write_file(self, mock_write):
        """Test executing write_file tool"""
        mock_write.return_value = {"success": True}

        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            result = assistant._execute_tool(
                "write_file",
                {"filepath": "/test/file.txt", "content": "test"}
            )

            mock_write.assert_called_once_with("/test/file.txt", "test")
            self.assertTrue(result["success"])

    @patch('llm_file_assistant.search_in_file')
    def test_execute_tool_search_in_file(self, mock_search):
        """Test executing search_in_file tool"""
        mock_search.return_value = {"found": True, "context": "test context"}

        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            result = assistant._execute_tool(
                "search_in_file",
                {"filepath": "/test/file.txt", "keyword": "test"}
            )

            mock_search.assert_called_once_with("/test/file.txt", "test")
            self.assertTrue(result["found"])

    def test_execute_tool_unknown(self):
        """Test executing unknown tool returns error"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")
            result = assistant._execute_tool("unknown_tool", {})

            self.assertIn("error", result)
            self.assertIn("Unknown tool", result["error"])

    def test_standalone_tool_call_function(self):
        """Test standalone tool_call function"""
        with patch('llm_file_assistant.LLMFileAssistant') as mock_assistant_class:
            mock_instance = Mock()
            mock_instance.tool_call.return_value = "Test response"
            mock_assistant_class.return_value = mock_instance

            result = tool_call("Test query")

            self.assertEqual(result, "Test response")
            mock_instance.tool_call.assert_called_once_with("Test query")

    def test_tool_call_error_handling(self):
        """Test tool_call function error handling"""
        with patch('llm_file_assistant.LLMFileAssistant') as mock_assistant_class:
            mock_assistant_class.side_effect = ValueError("API key not found")

            result = tool_call("Test query")

            self.assertIn("Error", result)
            self.assertIn("API key", result)


class TestToolIntegration(unittest.TestCase):
    """Integration tests for tool definitions and execution flow"""

    def test_all_tools_callable(self):
        """Test that all defined tools can be called"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")

            # Verify all tools can be passed to OpenAI
            with patch.object(assistant.client.chat.completions, 'create') as mock_create:
                mock_create.return_value = Mock(
                    choices=[Mock(finish_reason="end_turn", message=Mock(content="Response"))]
                )

                assistant.tool_call("Test query")

                # Verify create was called with tools
                call_kwargs = mock_create.call_args[1]
                self.assertIn("tools", call_kwargs)
                self.assertEqual(len(call_kwargs["tools"]), 4)

    def test_system_prompt_quality(self):
        """Test that system prompt guides the LLM appropriately"""
        with patch('llm_file_assistant.OpenAI') as mock_openai:
            assistant = LLMFileAssistant(api_key="test_key")

            with patch.object(assistant.client.chat.completions, 'create') as mock_create:
                mock_create.return_value = Mock(
                    choices=[Mock(finish_reason="end_turn", message=Mock(content="Response"))]
                )

                assistant.tool_call("Test query")

                # Verify system prompt is present
                call_kwargs = mock_create.call_args[1]
                messages = call_kwargs["messages"]
                system_message = messages[0]

                self.assertEqual(system_message["role"], "system")
                self.assertIn("file", system_message["content"].lower())
                self.assertIn("assistant", system_message["content"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
