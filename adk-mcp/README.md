# ADK MCP Agent Examples

This project demonstrates two ways of using the Google Agent Development Kit (ADK) with local Model-Context-Protocol (MCP) servers.

## Core Concepts

This directory contains two distinct examples:

1.  **Wikipedia Agent (HTTP MCP Server)**: This agent (`agent.py`) connects to a locally running Python script, `wikipedia_mcp_server.py`, over HTTP. The ADK's `MCPToolset` automatically discovers the tools exposed by the server and makes them available to the LLM. This architecture separates the agent's logic from the tool implementation.

2.  **Profile Server (Stdio MCP)**: The `mcp_profile.py` script is a simple, standalone MCP server that communicates over standard input/output (stdio) instead of HTTP. It demonstrates a lightweight way to provide tools to a local process without needing a network server.

**Note:** The `wikipedia_client.py` in this directory is a placeholder with mock functions.

## Files

- **`agent.py`**: Defines the ADK agent, configured to use the HTTP-based `MCPToolset`.
- **`wikipedia_mcp_server.py`**: An MCP server that provides mock tools for interacting with Wikipedia.
- **`wikipedia_client.py`**: A *mock* client used by the Wikipedia server.
- **`mcp_profile.py`**: A simple, stdio-based MCP server with a single `get_user_token` tool.
- **`requirements.txt`**: Python dependencies for all components in this directory.

## How to Run

### 1. Setup
It is recommended to use a virtual environment.

```bash
# Navigate to this directory
cd adk-mcp

# Create and activate a virtual environment
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/macOS
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Log in for Application Default Credentials (if not already done)
gcloud auth application-default login
```

---

### Example 1: Run the Wikipedia Agent (HTTP)

#### A. Start the Wikipedia MCP Server
In one terminal, start the tool server from this directory (`adk-mcp`):
```bash
python wikipedia_mcp_server.py
```

#### B. Run the Agent
In a second terminal, use the `adk` command-line tool to run the agent.

```bash
adk run .
```

When the `User:` prompt appears, you can ask a question that uses the mock Wikipedia tools, for example:
```
User: Please search for "Artificial Intelligence" on Wikipedia.
```
---

### Example 2: Run the Profile Server (Stdio)

The `mcp_profile.py` server runs over stdio. You can execute it directly and send it MCP JSON messages on stdin.

#### A. Run the Server
```bash
python mcp_profile.py
```

#### B. Send a Request
You can then manually send it an MCP request to test it. For example, paste the following JSON into the terminal where the server is running and press Enter:
```json
{
  "mcp_version": "1.0",
  "request_id": "test-1",
  "tool_name": "get_user_token",
  "arguments": {
    "user": "Alice"
  }
}
```
The server will respond with the tool's output on stdout.