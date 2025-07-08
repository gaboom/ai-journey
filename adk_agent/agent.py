"""
This file defines a Google ADK agent.

It is not meant to be executed directly. Instead, it should be run
using the ADK command-line tool. For example:

adk run adk_agent in the parent directory
"""
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

# 1. Configure the MCPToolset to connect to the local MCP server.
#    The ADK will automatically discover the `get_profile` tool.
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8181/mcp/"
    ),
)

# 2. Define the agent that will use the toolset.
#    The variable MUST be named `root_agent` for the ADK to find it.
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="profile_agent",
    instruction="Use the get_profile tool to answer questions about people's professions based on their profile.",
    tools=[mcp_toolset]
)
