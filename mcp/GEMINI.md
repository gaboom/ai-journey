# Gemini Project Context

This file contains project-specific context and memories for the Gemini agent.

## Project Overview

The user and I have built a comprehensive demonstration of a client-server architecture using the Model-Context-Protocol (MCP). The goal was to explore different methods for an LLM to consume external tools from a remote server.

We built three distinct clients, showcasing a progression from manual work to fully automated frameworks:
1.  A **low-level, manual orchestrator** (`client.py`) using the `openai` library directly.
2.  A **high-level LangChain agent** (`mcp_client.py`) using a custom-built, reusable `MCPToolkit` that we created to automatically discover tools.
3.  A **declarative Google Agent Development Kit (ADK) agent** (`adk_agent/`) that uses the framework's built-in `MCPToolset` for a zero-code discovery and orchestration experience.

The key achievement was comparing these different approaches and successfully implementing a clean, framework-native solution with the ADK.

## Key Files & Directories

- **`server.py`**: The MCP server providing the `get_profile` tool.
- **`client.py`**: The low-level client (manual orchestration).
- **`mcp_client.py`**: The high-level LangChain client.
- **`mcp_tool.py`**: A generic wrapper to make a single MCP function compatible with LangChain.
- **`mcp_toolkit.py`**: A self-contained toolkit that manages connection and tool discovery for LangChain.
- **`adk_agent/`**: The directory containing the Google ADK agent definition.
    - **`adk_agent/agent.py`**: The declarative agent definition file. The agent variable **must** be named `root_agent`.

## User Preferences & Memories

- **Virtual Environment:** The user's Python virtual environment for this project is located at `C:\Users\gabor.czigola\src\ai\.venv`. When running `pip` or `python`, I must use the executables from that venv.
- **File Preservation:** The user wants to keep all client implementations (`client.py`, `mcp_client.py`, etc.) for comparison. I should not delete them.
- **Architectural Goal:** The user prefers clean, reusable, and framework-compliant code. The end goal is always to find the highest-level abstraction that simplifies the problem, as demonstrated by our adoption of the ADK.
- **ADK Usage:** The ADK agent is run via the `adk run <directory>` command, not by executing the python file directly. It launches an interactive CLI and a web UI for tracing.
- **Test Input:** A good test prompt for the agents is: `"Based ONLY AND EXCLUSIVELY on the PROFILE of Sing-Ming Pei Tue de Santos III., what could be his profession today?"`