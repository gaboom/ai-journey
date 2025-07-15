"""
Defines a reusable MCPClientAgent for interacting with MCP servers.
This version uses separate connection manager classes for stdio and http.
"""
import asyncio
import traceback
from contextlib import _AsyncGeneratorContextManager
from typing import List, Dict, Any, Union, Optional, Callable

from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client, GetSessionIdCallback
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.shared.message import SessionMessage
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from openai.types.responses.function_tool_param import FunctionToolParam

# --- Server Configuration Types ---

McpServerParameters = Union[StdioServerParameters, str]
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
McpToolParameters = Dict[str, Any]
McpToolResponse = types.CallToolResult
McpToolCall = Callable[[McpToolParameters], McpToolResponse]


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
        elif isinstance(self._server_params, str):
            client = streamablehttp_client(url=self._server_params) # TODO implement additional parameters, maybe a dict not a str
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

    async def _call_tool(self, name: str, arguments: McpToolParameters) -> McpToolResponse: 
        async with McpClientSession(self._server_params) as session:
                await session.initialize()
                return await session.call_tool(name, arguments) # TODO timeout etc. parameters

    def call_tool(self, name: str, arguments: McpToolParameters) -> McpToolResponse:
        """Calls a tool by name with the given arguments."""
        return asyncio.run(self._call_tool(name, arguments))
    
    def get_function(self, name: str) -> McpToolCall:
        """Returns a function that calls a tool by name with the given arguments."""
        return (lambda args: self.call_tool(name, args))

    def get_functions(self) -> Dict[str, McpToolCall]:
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
        agent = McpClientAgent("http://localhost:9999/mcp") # http
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
        function_call_result = agent.get_functions()['get-page']({"title": "Set_Sail", "content": "withSource"})
        print(f"\n[Demo] Function call result:\n{function_call_result}")

    except Exception as e:
        print(f"\n[Demo] An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
