"""
This module contains the MCPToolkit, a self-contained class for
connecting to an MCP server and discovering its tools for use with LangChain.
"""
import logging
from typing import List

from pydantic import Field, create_model
from langchain_core.tools import BaseTool, BaseToolkit
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp_tool import MCPTool

log = logging.getLogger(__name__)

class MCPToolkit(BaseToolkit):
    """
    A self-contained LangChain Toolkit for discovering and using tools
    from an MCP server. This class manages the connection and session.
    """
    url: str
    _session_cm = None # To hold the session's context manager

    class Config:
        arbitrary_types_allowed = True

    async def __aenter__(self):
        """Async context manager to connect and initialize the session."""
        log.info(f"Toolkit connecting to MCP server at {self.url}...")
        self._http_client_cm = streamablehttp_client(self.url)
        read, write, _ = await self._http_client_cm.__aenter__()
        
        # Create the session and enter its context to start background tasks
        self._session_cm = ClientSession(read, write)
        self._session = await self._session_cm.__aenter__()
        
        await self._session.initialize()
        log.info("MCP session initialized successfully.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager to clean up the connection."""
        if self._session_cm:
            await self._session_cm.__aexit__(exc_type, exc_val, exc_tb)
        if self._http_client_cm:
            await self._http_client_cm.__aexit__(exc_type, exc_val, exc_tb)
        log.info("MCP session closed.")

    def get_tools(self) -> List[BaseTool]:
        """The standard LangChain interface for getting the tools in the toolkit."""
        raise NotImplementedError("Use 'await get_tools_async()' for this toolkit.")

    async def get_tools_async(self) -> List[BaseTool]:
        """
        Discovers tools from the initialized MCP session and returns them
        as a list of LangChain-compatible Tool objects.
        """
        if not self._session:
            raise RuntimeError("Toolkit not connected. Use 'async with MCPToolkit(...)'.")

        log.info("Discovering tools from MCP server...")
        tools = []
        try:
            list_tools_result = await self._session.list_tools()
            server_tools = list_tools_result.tools
            log.info(f"Found {len(server_tools)} tools on the server.")

            for tool_info in server_tools:
                log.info(f"  - Creating LangChain tool for: '{tool_info.name}'")
                
                fields = {}
                if tool_info.inputSchema and 'properties' in tool_info.inputSchema:
                    for param_name, param_details in tool_info.inputSchema['properties'].items():
                        description = param_details.get('description', '')
                        fields[param_name] = (str, Field(description=description))

                dynamic_args_schema = create_model(f"{tool_info.name}Args", **fields)

                langchain_tool = MCPTool(
                    session=self._session,
                    name=tool_info.name,
                    description=tool_info.description,
                    args_schema=dynamic_args_schema,
                )
                tools.append(langchain_tool)
            
            log.info("Tool discovery complete.")
            return tools
        except Exception as e:
            log.error(f"Failed to discover tools from MCP server: {e}", exc_info=True)
            return []
