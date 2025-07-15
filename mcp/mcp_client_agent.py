"""
Defines a reusable MCPClientAgent for interacting with MCP servers.
This version uses separate connection manager classes for stdio and http.
"""
import asyncio
from datetime import timedelta
from functools import partial
import traceback
from contextlib import _AsyncGeneratorContextManager
from typing import List, Dict, Any, Union, Optional, Protocol

from mcp.shared.session import ProgressFnT
from pydantic import BaseModel
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client, GetSessionIdCallback
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.shared.message import SessionMessage
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from openai.types.responses.function_tool_param import FunctionToolParam

# --- Server Configuration Types ---

class HttpServerParameters(BaseModel): # for some reason the mcp guys did not define this type
    url: str
    headers: dict[str, str] | None = None
    timeout: float | timedelta = 30
    sse_read_timeout: float | timedelta = 60 * 5
    terminate_on_close: bool = True

McpServerParameters = Union[StdioServerParameters, HttpServerParameters]

McpClientAsync = Union[
    _AsyncGeneratorContextManager[
        tuple[
            MemoryObjectReceiveStream[SessionMessage | Exception],
            MemoryObjectSendStream[SessionMessage],
        ]
    ],  # stdio
    _AsyncGeneratorContextManager[
        tuple[
            MemoryObjectReceiveStream[SessionMessage | Exception],
            MemoryObjectSendStream[SessionMessage],
            GetSessionIdCallback,
        ]
    ],  # sse
]

ToolFunctionArguments = Dict[str, Any]
ToolFunctionResult = types.CallToolResult
class ToolFunctionCall(Protocol):
    """A protocol for a callable that executes a tool, matching the signature of `McpClientAgent.call_tool`."""
    def __call__(
        self,
        arguments: ToolFunctionArguments,
        read_timeout_seconds: Optional[timedelta] = None,
        progress_callback: Optional[ProgressFnT] = None,
    ) -> ToolFunctionResult:
        ...

# --- Connection Manager Classes ---

class McpClientSession:
    """
    A client agent that connects to an MCP server, handles sessions.
    """
    def __init__(self, server_params: McpServerParameters):
        self._server_params: McpServerParameters = server_params
        self._client: Optional[McpClientAsync] = None
        self._session: Optional[ClientSession] = None

    async def __aenter__(self) -> ClientSession:
        if isinstance(self._server_params, StdioServerParameters):
            client = stdio_client(server=self._server_params)
            self._client = client
            read, write = await client.__aenter__()
        elif isinstance(self._server_params, HttpServerParameters):
            client = streamablehttp_client(**self._server_params.model_dump())
            self._client = client
            read, write, _ = await client.__aenter__()
        else:
            raise TypeError(f"Unsupported connection type {self._server_params}")
            
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

# --- Main Agent Class ---

class McpClientAgent:
    """
    A client agent that connects to an MCP server, discovers its tools,
    and provides methods to access them.
    """
    def __init__(self, server_params: McpServerParameters):
        self._server_params = server_params
        self._tools: List[FunctionToolParam] = []

    async def _discover_tools(self, session: ClientSession) -> None:
        await session.initialize()
        tool_response = await session.list_tools()
        for tool in tool_response.tools:
            params = tool.inputSchema.copy()
            params.pop("$schema", None)  # Remove the unsupported $schema key
            self._tools.append(FunctionToolParam(
                type="function",
                name=tool.name,
                description=tool.description, # TODO: append tool.outputSchema etc?
                parameters=params,
                strict=False,
            ))
    
    async def _get_tools(self) -> List[FunctionToolParam]:
        self._tools = []
        async with McpClientSession(self._server_params) as session:
            await self._discover_tools(session)
        return self._tools

    def get_tools(self) -> List[FunctionToolParam]:
        """Returns all discovered tools in OpenAI's function format."""
        return asyncio.run(self._get_tools())

    async def _call_tool(self, name: str, arguments: ToolFunctionArguments, read_timeout_seconds: timedelta | None = None, progress_callback: ProgressFnT | None = None) -> ToolFunctionResult: 
        async with McpClientSession(self._server_params) as session:
                await session.initialize()
                return await session.call_tool(name, arguments, read_timeout_seconds, progress_callback)

    def call_tool(self, name: str, arguments: ToolFunctionArguments, read_timeout_seconds: timedelta | None = None, progress_callback: ProgressFnT | None = None) -> ToolFunctionResult:
        """Calls a tool by name with the given arguments."""
        return asyncio.run(self._call_tool(name, arguments, read_timeout_seconds, progress_callback))
    
    def get_function(self, name: str) -> ToolFunctionCall:
        """Returns a function that calls a tool by name with the given arguments."""
        return partial(self.call_tool, name)

    def get_functions(self) -> Dict[str, ToolFunctionCall]:
        # TODO: use typing.ParamSpec to make this more flexible
        """
        Returns a mapping from each tool's name to a lambda function that calls the tool with the given arguments.
        """
        return {
            tool["name"]: self.get_function(tool["name"])
            for tool in self._tools
        }
# --- Example Usage ---

def main():
    """
    Demonstrates how to use the MCPClientAgent with a remote HTTP server.
    """
    print("--- MCPClientAgent HTTP Demo ---")
    
    try:
        agent = McpClientAgent(HttpServerParameters(
            url="http://localhost:9999/mcp"
            )) # http
        agent = McpClientAgent(StdioServerParameters(
            command="npx",
            args=["-y", "@professional-wiki/mediawiki-mcp-server@latest"],
        )) # stdio
        
        print("\n[Demo] Client created. Fetching tools...")
        agent_tools = agent.get_tools()
        print(f"\n[Demo] OpenAI-formatted tools:\n{agent_tools}")
        
        print("\n[Demo] Attempting to call tool 'get-page'...")
        tool_call_result = agent.call_tool("get-page", {"title": "Set_Sail", "content": "withSource"})
        print(f"\n[Demo] Tool call result:\n{tool_call_result}")

        print("\n[Demo] Attempting to call function 'get-page'...")
        function = agent.get_functions()['get-page']
        function_call_result = function(
            {"title": "Set_Sail", "content": "withSource"}
        )
        print(f"\n[Demo] Function call result:\n{function_call_result}")

    except Exception as e:
        print(f"\n[Demo] An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
