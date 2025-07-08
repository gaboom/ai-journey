# Google Agent Development Kit (ADK) MCP Client

This project demonstrates a high-level, declarative approach to building an LLM agent using the Google Agent Development Kit (ADK). The agent is designed to consume tools from an MCP (Model-Context-Protocol) server.

## Core Concept

The ADK framework simplifies agent creation by allowing developers to *declare* the agent's properties and toolsets. When provided with an MCP server endpoint, the ADK's built-in `MCPToolset` automatically discovers and integrates the available tools, handling the entire orchestration loop (reasoning, tool calling, and response generation) with no manual coding required.

This represents the state-of-the-art for rapid, convention-based agent development.

## Files

- **`agent.py`**: The complete agent definition. It simply declares the `root_agent` and points it to the MCP server running at `http://localhost:8080`.

## How to Run

### 1. Setup
This agent requires the Google Cloud SDK for authentication and the `google-adk` library. It is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/macOS
# source .venv/bin/activate

# Install the ADK library
pip install google-adk

# Install and initialize the Google Cloud SDK
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Log in for Application Default Credentials
gcloud auth application-default login
```

### 2. Start the MCP Server
This agent requires the MCP tool server to be running. In a separate terminal, navigate to the `mcp` directory and start the server:
```bash
cd ../mcp
python server.py
```

### 3. Run the ADK Agent
In another terminal, from the `adk_agent` directory, use the `adk` command-line tool to run the agent.

1.  **Run the agent interactively:**
    ```bash
    adk run .
    ```
2.  When the `User:` prompt appears, enter your question. For example:
    ```
    User: Based ONLY AND EXCLUSIVELY on the PROFILE of Sing-Ming Pei Tue de Santos III., what could be his profession today?
    ```

3.  **Follow the execution in a web browser (optional):** The `adk` tool will print a URL to a local web server (e.g., `http://127.0.0.1:8000`). You can open this URL to see a real-time, interactive graph of the agent's thought process and tool calls.
