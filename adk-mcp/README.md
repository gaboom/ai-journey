# ADK Agent with Multiple Stdio MCP Toolsets

This project demonstrates a powerful pattern for building a Google Agent Development Kit (ADK) agent that dynamically loads its tools from multiple, independent, local processes communicating over standard input/output (stdio).

## Core Concept

The agent defined in `agent.py` is configured to use three separate `MCPToolset` instances, each powered by a different stdio-based command:

1.  **Profile Toolset (Python)**: Launches a local Python script (`mcp_profile.py`) to provide a custom `get_user_token` tool. This demonstrates how to integrate custom, project-specific tools written in Python.

2.  **Filesystem Toolset (Node.js/npx)**: Uses `npx` to run the public `@modelcontextprotocol/server-filesystem` package. This instantly gives the agent the ability to read, write, and list files in its working directory.

3.  **Wikipedia Toolset (Node.js/npx)**: Uses `npx` to run the public `Rudra-ravi/wikipedia-mcp` package. This provides the agent with tools to search Wikipedia and retrieve article content.

This architecture allows for a highly modular and extensible agent. The ADK's `StdioServerParameters` handles the lifecycle of each tool subprocess, making the setup clean and declarative.

## Files

- **`agent.py`**: The complete agent definition, which declaratively combines the three toolsets.
- **`mcp_profile.py`**: A simple, stdio-based MCP server with a single `get_user_token` tool.
- **`requirements.txt`**: Python dependencies for the agent.

## How to Run

### 1. Setup
Ensure you have the necessary prerequisites installed:
- Python and the packages in `requirements.txt`
- Node.js and `npx`
- Google Cloud SDK for authentication

```bash
# Navigate to this directory
cd adk-mcp

# It is recommended to use a virtual environment.
# Install Python dependencies
pip install -r requirements.txt

# Log in for Application Default Credentials (if not already done)
gcloud auth application-default login
```

### 2. Run the Agent
Because the agent uses `StdioToolset` for all its tools, you do not need to start any servers manually. The ADK will launch all three tool processes automatically.

From the `adk-mcp` directory, simply run:
```bash
adk run .
```

When the `User:` prompt appears, you can ask questions that leverage any of the loaded tools.

**Examples:**
- **Profile Tool:** `What is the token for user Bob?`
- **Filesystem Tool:** `Read the contents of the file named agent.py`
- **Wikipedia Tool:** `Search Wikipedia for "Large Language Model"`
