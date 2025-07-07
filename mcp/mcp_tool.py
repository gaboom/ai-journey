"""
This module contains the generic MCPTool class, which acts as a
LangChain wrapper for a single function on an MCP server.
"""
import logging
from typing import Type

from pydantic import BaseModel
from langchain_core.tools import BaseTool
from mcp import ClientSession, types

log = logging.getLogger(__name__)

class MCPTool(BaseTool):
    """A custom LangChain tool that executes a function on an MCP server."""
    
    session: ClientSession
    name: str
    description: str
    args_schema: Type[BaseModel]

    class Config:
        """Pydantic config to allow arbitrary types like ClientSession."""
        arbitrary_types_allowed = True

    def _run(self, *args, **kwargs):
        """MCP tools are async, so we don't implement the sync version."""
        raise NotImplementedError("MCPTool does not support synchronous execution.")

    async def _arun(self, *args, **kwargs):
        """
        The asynchronous execution method that LangChain's AgentExecutor will call.
        """
        log.info(f"LangChain agent is executing MCP tool '{self.name}' with args: {kwargs}")
        try:
            tool_result = await self.session.call_tool(self.name, kwargs)
            
            if tool_result.isError:
                log.error(f"MCP tool '{self.name}' returned an error: {tool_result.content}")
                return f"Error from tool '{self.name}': {tool_result.content}"

            if tool_result.content:
                response_text = " ".join(
                    item.text for item in tool_result.content if isinstance(item, types.TextContent)
                )
                log.info(f"Received response from '{self.name}': '{response_text}'")
                return response_text
            
            log.warning(f"MCP tool '{self.name}' executed but returned no content.")
            return "Tool executed successfully but returned no content."
        except Exception as e:
            log.error(f"An unexpected error occurred while running tool '{self.name}': {e}", exc_info=True)
            return f"An unexpected error occurred: {e}"
