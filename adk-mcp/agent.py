"""
This file defines a Google ADK agent.

It is not meant to be executed directly. Instead, it should be run
using the ADK command-line tool. For example:

adk run .
"""
import sys
import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams

# 1. Instantiate the LiteLlm wrapper to connect to the local Ollama model.
#    The model string must be prefixed with "ollama_chat/"
local_llm = LiteLlm(model="ollama_chat/llama3.2")

# 2. Configure a toolset to launch the mcp_profile.py script via stdio.
profile_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=["mcp_profile.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
)

# 3. Configure a toolset to launch the npx filesystem server.
#    This exposes the current working directory to the agent.
filesystem_toolset = MCPToolset(
    connection_params=StdioConnectionParams(timeout=12, server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()]
    )),
    tool_filter=["list_directory", "read_file"]
)

# 4. Configure a toolset to launch the npx Wikipedia server.
wikipedia_toolset = MCPToolset(
    connection_params=StdioConnectionParams(timeout=60, server_params=StdioServerParameters(
        command="npx",
        args=["-y", "@professional-wiki/mediawiki-mcp-server@latest"]
    ))
)

# 5. Define the agent that will use the local LLM and all toolsets.
#    The variable MUST be named `root_agent` for the ADK to find it.
root_agent = LlmAgent(
#    model=local_llm,
    model="gemini-2.5-flash",
    name="mcp_stdio_agent",
    instruction="Good luck.",
    tools=[profile_toolset, filesystem_toolset, wikipedia_toolset]
)
