"""
LLM File Assistant with OpenAI Integration

Integrates fs_tools functions with OpenAI's GPT-4o-mini model using tool calling.

The LLM can intelligently call file operation tools based on user queries:
- Read files and folders
- List files with filtering
- Search for keywords in files
- Create and write files

Example queries:
- "Read all resumes in the resumes folder"
- "Find resumes mentioning Python experience"
- "Create a summary file for resume_john_doe.pdf"
- "List all PDF files in the documents folder"
"""

import os
import json
import logging
from typing import Any, Optional
from openai import OpenAI
from fs_tools import read_file, list_files, write_file, search_in_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMFileAssistant:
    """
    LLM-powered file assistant that can read, write, and search files
    using OpenAI's GPT-4o-mini model with tool calling.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM File Assistant.

        Args:
            api_key (str, optional): OpenAI API key. If not provided,
                                    reads from OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please provide an API key."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
        self.tools = self._define_tools()

    def _define_tools(self) -> list:
        """
        Define the tools available to the LLM.

        Returns:
            list: Tool definitions for the LLM.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the content of a file and return its text content and metadata",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "The full path to the file to read (e.g., /path/to/file.txt)",
                            }
                        },
                        "required": ["filepath"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List all files in a directory, optionally filtered by file extension",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "The path to the directory to list",
                            },
                            "extension": {
                                "type": "string",
                                "description": "Optional file extension to filter by (e.g., .txt, .pdf)",
                            },
                        },
                        "required": ["directory"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file, creating directories if needed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "The full path where the file should be written",
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file",
                            },
                        },
                        "required": ["filepath", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_in_file",
                    "description": "Search for a keyword in a file and return matching context",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "The path to the file to search in",
                            },
                            "keyword": {
                                "type": "string",
                                "description": "The keyword to search for (case-insensitive)",
                            },
                        },
                        "required": ["filepath", "keyword"],
                    },
                },
            },
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """
        Execute a tool function with the provided arguments.

        Args:
            tool_name (str): Name of the tool to execute
            tool_input (dict): Arguments for the tool

        Returns:
            Any: Result from the tool execution
        """
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        try:
            if tool_name == "read_file":
                return read_file(tool_input["filepath"])
            elif tool_name == "list_files":
                extension = tool_input.get("extension")
                return list_files(tool_input["directory"], extension)
            elif tool_name == "write_file":
                return write_file(tool_input["filepath"], tool_input["content"])
            elif tool_name == "search_in_file":
                return search_in_file(
                    tool_input["filepath"], tool_input["keyword"]
                )
            else:
                logger.error(f"Unknown tool: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}

    def tool_call(self, user_query: str) -> str:
        """
        Process a user query using the LLM and call appropriate tools.

        Args:
            user_query (str): The user's question or request

        Returns:
            str: The final response from the LLM
        """
        logger.info(f"Processing user query: {user_query}")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent file management assistant. "
                    "You help users read, write, search, and organize files. "
                    "Use the available tools to fulfill user requests. "
                    "Provide clear and helpful responses about file operations. "
                    "When reading files, provide a summary of the content. "
                    "When listing files, organize the results clearly."
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]

        # Initial API call to the LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
        )

        logger.info(f"Initial response finish_reason: {response.choices[0].finish_reason}")

        # Process tool calls if any
        while response.choices[0].finish_reason == "tool_calls":
            # Get the assistant's message
            assistant_message = response.choices[0].message
            messages.append({"role": "assistant", "content": assistant_message.content or ""})

            # Handle each tool call
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)

                logger.info(f"Tool call: {tool_name}")

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_input)

                tool_results.append(
                    {
                        "type": "tool",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result,
                    }
                )

            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})

            # Make another API call with tool results
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
            )

            logger.info(f"Follow-up response finish_reason: {response.choices[0].finish_reason}")

        # Extract final text response
        final_response = response.choices[0].message.content
        logger.info(f"Final response: {final_response}")

        return final_response or "No response generated."


def tool_call(user_query: str) -> str:
    """
    Standalone function to process a user query using the LLM file assistant.

    Args:
        user_query (str): The user's question or request

    Returns:
        str: The response from the LLM
    """
    try:
        assistant = LLMFileAssistant()
        return assistant.tool_call(user_query)
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"An unexpected error occurred: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Example queries
    example_queries = [
        "List all text files in the sample_files directory",
        "Read the resume.txt file from sample_files folder",
        "Search for the word 'engineer' in resume.txt and show me the context",
    ]

    for query in example_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        response = tool_call(query)
        print(f"Response: {response}\n")
