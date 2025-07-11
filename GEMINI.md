# Gemini Project Context

This file contains project-specific context and memories for the Gemini agent. It is a consolidation of multiple `GEMINI.md` files from different subdirectories.

---
## Context from: mcp/GEMINI.md
---

# Gemini Project Context

This file contains project-specific context and memories for the Gemini agent.

## Project Overview

The user and I have built a comprehensive demonstration of a client-server architecture using the Model-Context-Protocol (MCP). The goal was to explore different methods for an LLM to consume external tools from a remote server.

We built three distinct clients, showcasing a progression from manual work to fully automated frameworks:
1.  A **low-level, manual orchestrator** (`client.py`) using the `openai` library directly.
2.  A **high-level LangChain agent** (`mcp_client.py`) using a custom-built, reusable `MCPToolkit` that we created to automatically discover tools.
3.  A **declarative Google Agent Development Kit (ADK) agent** (`adk-agent/`) that uses the framework's built-in `MCPToolset` for a zero-code discovery and orchestration experience.

The key achievement was comparing these different approaches and successfully implementing a clean, framework-native solution with the ADK.

## Key Files & Directories

- **`server.py`**: The MCP server providing the `get_profile` tool.
- **`client.py`**: The low-level client (manual orchestration).
- **`mcp_client.py`**: The high-level LangChain client.
- **`mcp_tool.py`**: A generic wrapper to make a single MCP function compatible with LangChain.
- **`mcp_toolkit.py`**: A self-contained toolkit that manages connection and tool discovery for LangChain.
- **`adk-agent/`**: The directory containing the Google ADK agent definition.
    - **`adk-agent/agent.py`**: The declarative agent definition file. The agent variable **must** be named `root_agent`.

## User Preferences & Memories

- **Virtual Environment:** The user's Python virtual environment for this project is located at `C:\Users\gabor.czigola\src\ai\.venv`. When running `pip` or `python`, I must use the executables from that venv.
- **File Preservation:** The user wants to keep all client implementations (`client.py`, `mcp_client.py`, etc.) for comparison. I should not delete them.
- **Architectural Goal:** The user prefers clean, reusable, and framework-compliant code. The end goal is always to find the highest-level abstraction that simplifies the problem, as demonstrated by our adoption of the ADK.
- **ADK Usage:** The ADK agent is run via the `adk run <directory>` command, not by executing the python file directly. It launches an interactive CLI and a web UI for tracing.
- **Test Input:** A good test prompt for the agents is: `"Based ONLY AND EXCLUSIVELY on the PROFILE of Sing-Ming Pei Tue de Santos III., what could be his profession today?"`

---
## Context from: mcp-profile/GEMINI.md (New)
---

## Project Overview

The `mcp-profile` project is a simple, standalone MCP server that communicates over stdio. It was created to demonstrate the basic principles of an MCP server without the complexity of HTTP.

## Key Files & Directories

- **`mcp_profile.py`**: The server script. It defines a single tool, `get_user_token`, and listens for requests on stdin.
- **`requirements.txt`**: Contains the single `mcp` dependency.

## Key Learnings & Decisions

- This server uses the `server.run()` method from the `mcp` library, which defaults to stdio communication, making it very easy to set up for local, script-based tools.

---
## Context from: adk-mcp/GEMINI.md (New)
---

## Project Overview

The `adk-mcp` project is a fork of the `adk-agent` that demonstrates an alternative way of providing tools to an ADK agent. Instead of connecting to a remote HTTP MCP server, this agent uses the `StdioToolset` to launch a local Python script (`wikipedia_mcp_server.py`) as a subprocess and communicate with it over standard input/output.

## Key Files & Directories

- **`agent.py`**: Defines the ADK agent, configured with a `StdioToolset`.
- **`wikipedia_mcp_server.py`**: A local MCP server providing Wikipedia tools. It is launched automatically by the agent.
- **`wikipedia_client.py`**: A **mock** client with placeholder methods. It does not perform real Wikipedia lookups.
- **`requirements.txt`**: Contains dependencies for this specific agent (`google-adk`, `wikipedia`).

## Key Learnings & Decisions

- This project demonstrates a powerful pattern for bundling tools directly with an agent, removing the need for a separate, networked server process. This simplifies deployment and reduces network latency.
- The original `wikipedia-mcp` code from the GitHub repository was incomplete (missing the client and a main execution block), so a mock client and a runner were created to make the example functional for demonstration purposes.

---
## Context from: tool/GEMINI.md
---

# Gemini Project State

This file summarizes the final state of the project for the Gemini agent.

## Project Overview

The user's goal was to explore and create proofs-of-concept for using LLM agent tools with a locally running Ollama model (`llama3.2`). We successfully created two parallel implementations using LangChain and LlamaIndex.

## Final File Structure

- `langchain.py`: A working POC using LangChain's `ChatOpenAI` client pointed at the local Ollama OpenAI-compatible endpoint. It uses a tool-calling agent to perform addition.
- `llamaindex.py`: A working POC using LlamaIndex's native `llama-index-llms-ollama` integration. It uses a `ReActAgent` to perform addition.
- `requirements.txt`: Contains all necessary dependencies for both `langchain` and `llama-index` implementations.
- `README.md`: Provides setup and usage instructions for a human developer.
- `.venv/`: The Python virtual environment.

## Key Learnings & Decisions

- **Initial Failures with `ollama` library:** The initial attempts using the base `ollama` Python library for tool calling were unsuccessful due to API mismatches.
- **LangChain `create_tool_calling_agent`:** This modern LangChain agent requires a model that supports the `.bind_tools()` method. The native `langchain-ollama` integration does not support this. The successful workaround was to use the `langchain-openai` package and point the `ChatOpenAI` client to Ollama's OpenAI-compatible endpoint (`http://localhost:11434/v1`).
- **LlamaIndex `OpenAIAgent`:** A similar issue occurred with LlamaIndex's `OpenAIAgent`, which made hardcoded assumptions about OpenAI models (like `context_window` size).
- **LlamaIndex Native Integration:** The most robust solution for LlamaIndex was to use the dedicated `llama-index-llms-ollama` package. This required using the `ReActAgent` as it's designed for this direct, prompt-based integration, avoiding the need for special model API features.
- **Deprecation Warnings:** We addressed several deprecation warnings, particularly in LlamaIndex, by updating to the modern `ReActAgent` class from the `llama_index.core.agent.react.workflow` module.
- **Virtual Environment:** All dependencies were installed and managed within the user-specified virtual environment at `C:\Users\gabor.czigola\src\ai\.venv`.
