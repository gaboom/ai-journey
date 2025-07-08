"""
This file defines a Google ADK agent.

It is not meant to be executed directly. Instead, it should be run
using the ADK command-line tool. For example:

adk run .
"""
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

# 1. Instantiate the LiteLlm wrapper to connect to the local Ollama model.
#    The model string must be prefixed with "ollama_chat/"
local_llm = LiteLlm(model="ollama_chat/llama3.2")

# 2. Configure the MCPToolset to connect to the local Wikipedia MCP server.
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8080/mcp/"  # Default for FastMCP
    ),
)

# 3. Define the agent that will use the local LLM and the toolset.
#    The variable MUST be named `root_agent` for the ADK to find it.
root_agent = LlmAgent(
    model=local_llm,
    name="wikipedia_agent",
    instruction="Use the wikipedia tools to answer user questions.",
    tools=[mcp_toolset]
)
