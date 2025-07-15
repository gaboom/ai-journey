"""
A command-line tool to interact with OpenAI models using the new responses API,
including support for remote tools like MCP.

Usage:
    python mcp/chat.py

Requirements:
    - openai: The official OpenAI Python library.
    - OPENAI_API_KEY: An environment variable containing your OpenAI API key.
"""
import base64
import json
import os
from pickle import FALSE
import sys
import traceback
from typing import List, Optional, Sequence, Union

from mcp import StdioServerParameters, types
import openai
from openai.types.responses import Response, ResponseInputItemParam, ResponseInputParam, WebSearchToolParam
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from openai.types.responses.response_input_param import FunctionCallOutput, ImageGenerationCall
from openai.types.responses.tool_param import Mcp, ToolParam, ImageGeneration

from mcp_client_agent import HttpServerParameters, McpClientAgent, ToolFunctionCall, ToolFunctionArguments, ToolFunctionResult

class Agent:
    """
    An agent that uses the OpenAI responses API to interact with the user
    and handle tool calls.
    """
    def __init__(self) -> None:
        # --- Configuration ---
        self.MODEL: str = "gpt-4.1" 
        self.INSTRUCTIONS: str = "You are an agent of delight. Use the tools provided."
        self.TOOLS: List[ToolParam] = []
        self.FUNCTIONS: dict[str, ToolFunctionCall] = {}

        # --- Tool Definitions ---

        # Remote Mcp Tool(s)
        # models supporting Mcp-s discover and append tools on the backend (!)
        # does not support stdio nor localhost servers
        # we do not need to manage functions nor invocations!
        REMOTE_TOOLS: List[Mcp] = [{
            "type": "mcp",
            "server_label": "remote-deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": "never",
        }]
        self.TOOLS.extend(REMOTE_TOOLS)
        
        # Conversation ending function :)
        TERMINATOR_FUNCTION_NAME: str = "bye"
        TERMINATOR_TOOLS: List[FunctionToolParam] = [{
            "type": "function",
            "name": TERMINATOR_FUNCTION_NAME,
            "description": "Call this function to end the conversation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True,
        }]
        self.TOOLS.extend(TERMINATOR_TOOLS)
        self.FUNCTIONS[TERMINATOR_FUNCTION_NAME] = self.terminate

        # Local Mcp Tool(s) (stdio, sse, streamable-http)
        # McpClientAgent manually discovers and appends tools,
        # must manage functions and invocations manually on the client (!)
        local_mcp_agent = McpClientAgent(StdioServerParameters(
            command="npx",
            args=["-y", "@professional-wiki/mediawiki-mcp-server@latest"],
            env=None,
        )) # stdio
        # MCP_TRANSPORT=http PORT=9999 npx -y @professional-wiki/mediawiki-mcp-server@latest
        local_mcp_agent = McpClientAgent(HttpServerParameters(url="http://localhost:9999/mcp")) # http
        LOCAL_STDIO_TOOLS:List[FunctionToolParam] = local_mcp_agent.get_tools()
        self.TOOLS.extend(LOCAL_STDIO_TOOLS)
        self.FUNCTIONS.update(local_mcp_agent.get_functions())

        web_search = WebSearchToolParam(
            type="web_search_preview",
        )
        self.TOOLS.append(web_search)

        image_generation = ImageGeneration(
            type="image_generation",
            output_format="png",
        )
        self.TOOLS.append(image_generation)

        # --- State ---
        self.RUNNING: bool = False
        self.client: openai.OpenAI = self._initialize_client()
        self.last_response_id: Optional[str] = None

    def _initialize_client(self) -> openai.OpenAI:
        """Checks for API key and initializes the OpenAI client."""
        if not os.environ.get("OPENAI_API_KEY"):
            sys.stderr.write("Error: OPENAI_API_KEY environment variable not set.\n")
            sys.exit(1)
        try:
            return openai.OpenAI()
        except Exception as e:
            sys.stderr.write(f"Error initializing OpenAI client: {e}\n")
            sys.exit(1)

    def _create_response(self, input: Union[str, ResponseInputParam]):
        """Utility method to create a response from the OpenAI client given user input."""
        return self.client.responses.create(
            model=self.MODEL,
            tools=self.TOOLS,
            input=input,
            instructions=self.INSTRUCTIONS,
            previous_response_id=self.last_response_id
        )

    def _handle_function_result(self, functionCall: ResponseFunctionToolCall, result: ToolFunctionResult) -> FunctionCallOutput:
        """Handles a function result from the model's response."""
        return FunctionCallOutput(
            type="function_call_output",
            call_id=functionCall.call_id,
            output=str(result)
        )

    def _handle_function_call(self, functionCall: ResponseFunctionToolCall) -> FunctionCallOutput:
        """Handles a function call from the model's response."""
        function: ToolFunctionCall = self.FUNCTIONS[functionCall.name]
        result = function(json.loads(functionCall.arguments))
        print(f"[system] function='{functionCall}' result='{result}'", flush=True)
        return self._handle_function_result(functionCall, result)

    def _handle_image_generation(self, id:str, image: str) -> None:
        print(f"[system] image='{id}.png'", flush=True)
        with open(f"{id}.png", "wb") as f:
            f.write(base64.b64decode(image))

    def _handle_response(self, response: Response):
        """Utility method to handle the response object: prints output_text and handles function calls."""
        if hasattr(response, 'id') and response.id:
            self.last_response_id = response.id

        if hasattr(response, 'output_text') and response.output_text:
            print(f"[agent] {response.output_text}", flush=True)

        function_results: List[ResponseInputItemParam] = []
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if getattr(item, 'type', None) == 'image_generation_call':
                    self._handle_image_generation(getattr(item, 'id'), getattr(item, 'result'))
                if getattr(item, 'type', None) == 'function_call':
                    function_call = ResponseFunctionToolCall.model_validate(item)
                    function_results.append(self._handle_function_call(function_call))
        if function_results:
            response = self._create_response(function_results)
            self._handle_response(response) # recursion for the win

    def terminate(self, *_, **__) -> ToolFunctionResult:
            self.RUNNING = False
            return ToolFunctionResult(
                content=[types.TextContent(type="text", text="Conversation shall end.")],
                structuredContent=None,
                isError=False
            )

    def run(self) -> None:
        """Runs the main conversation loop."""
        self.RUNNING = True
        self.last_response_id = None
        print(f"[system] model='{self.MODEL}' instructions='{self.INSTRUCTIONS}' tools='{self.TOOLS}'.")
        
        while self.RUNNING:
            try:
                print(f"[user] ", end="", flush=True)
                user_input = input()

                # Get Response using the new API
                try:
                    response = self._create_response(user_input)
                    self._handle_response(response)

                except openai.APIError as e:
                    sys.stderr.write(f"OpenAI API Error: {e}\n")
                    sys.stderr.write(f"Traceback:\n{traceback.format_exc()}\n")
                except Exception as e:
                    sys.stderr.write(f"An unexpected error occurred: {e}\n")
                    sys.stderr.write(f"Traceback:\n{traceback.format_exc()}\n")

            except (KeyboardInterrupt, EOFError):
                self.RUNNING = False
        
        print("", flush=True)

def main() -> None:
    """
    Main function to instantiate and run the agent.
    """
    agent = Agent()
    agent.run()

if __name__ == "__main__":
    main()
