# Gemini Project Context: AI Journey

This document serves as a comprehensive guide and memory for the AI agent regarding the `ai` monorepo. The overall project, "AI Journey," is a collection of proofs-of-concept and applications exploring various facets of Large Language Model (LLM) development, from basic model interaction to complex, agentic workflows.

## General Conventions & Memories

-   **Virtual Environment:** All Python-based sub-projects use a single virtual environment located at `C:\Users\gabor.czigola\src\ai\.venv`.
-   **README Files:** When making changes, I must update the `README.md` in the root and any affected subdirectories.
-   **Commits:** When creating a git commit, I should use a temporary file for the message.
-   **File Preservation:** The user wants to keep all client and proof-of-concept implementations for comparison and historical context. I should not delete them unless explicitly asked.
-   **Architectural Goal:** The user prefers clean, reusable, and framework-compliant code, aiming for the highest level of abstraction that solves the problem elegantly.

---

## Sub-Project Summaries

This section details the purpose, architecture, and key learnings for each sub-project within the repository.

### 1. `ochat` - Ollama Chat CLI

-   **Project Overview:** A simple, robust command-line interface for interacting with local Ollama models. It's designed for quick, terminal-based chats and supports multimodal input.
-   **Key Files:**
    -   `ochat.py`: The main script, built with `argparse` and the `ollama` Python library.
-   **How to Run:**
    ```bash
    # Basic query
    python ochat/ochat.py "Why is the sky blue?"

    # Query with an image using a multimodal model
    python ochat/ochat.py -m llava -i path/to/image.png "What is in this picture?"
    ```
-   **Key Learnings:** Demonstrates direct, streaming interaction with Ollama, including how to handle text and image data in the `ollama` library.

### 2. `tool` - Local LLM Tool Use

-   **Project Overview:** A proof-of-concept exploring how to make a local Ollama model (`llama3.2`) use external tools. It provides two parallel implementations to compare frameworks.
-   **Key Files:**
    -   `langchain.py`: A PoC using LangChain's `ChatOpenAI` client pointed at Ollama's OpenAI-compatible endpoint.
    -   `llamaindex.py`: A PoC using LlamaIndex's native `llama-index-llms-ollama` integration with a `ReActAgent`.
-   **Key Learnings:** The most reliable method for tool use with local models is often framework-specific. For LangChain, the OpenAI-compatible endpoint was necessary, while LlamaIndex worked best with its dedicated native integration.

### 3. `mcp` - MCP Server & Clients

-   **Project Overview:** A demonstration of the Model-Context-Protocol (MCP) for tool serving. It includes a central server and multiple clients that showcase different levels of abstraction for consuming tools.
-   **Key Files:**
    -   `server.py`: The `FastMCP` server that exposes a `get_profile` tool over HTTP.
    -   `client.py`: A low-level, manual client showing the full orchestration loop.
    -   `mcp_client.py`: A high-level LangChain agent using a custom `MCPToolkit` for automatic tool discovery.
-   **Key Learnings:** This project highlights the progression from manual tool-use orchestration to automated, framework-based approaches, with the `MCPToolkit` demonstrating a reusable solution for LangChain.

### 4. `adk-agent` - Declarative Agent (Remote Tools)

-   **Project Overview:** A Google Agent Development Kit (ADK) agent that consumes tools from the remote HTTP `mcp/server.py`.
-   **Key Files:**
    -   `agent.py`: A declarative agent definition that uses the ADK's built-in `MCPToolset` to connect to the server, discovering and orchestrating tools with zero manual code.
-   **How to Run:**
    1.  Start the MCP server: `python mcp/server.py`
    2.  Run the ADK agent: `adk run adk-agent`
-   **Key Learnings:** The ADK provides a state-of-the-art, "zero-code" approach to tool integration when connecting to a standard MCP endpoint, handling all discovery and orchestration automatically.

### 5. `adk-mcp` - Declarative Agent (Local Tools)

-   **Project Overview:** An ADK agent that demonstrates loading tools from local scripts via standard input/output (stdio), removing the need for a networked server.
-   **Key Files:**
    -   `agent.py`: Defines an ADK agent with multiple `StdioServerParameters` toolsets.
    -   `mcp_profile.py`: A local Python script providing a custom tool, launched as a subprocess by the agent.
-   **How to Run:**
    ```bash
    # From the adk-mcp directory
    adk run .
    ```
-   **Key Learnings:** This pattern is powerful for bundling tools directly with an agent, simplifying deployment and reducing latency. It can dynamically load tools from different languages/packages (e.g., Python scripts, `npx` packages).

### 6. `baios` - Agentic Workflow Engine

-   **Project Overview:** "Basic AI Operating System," a proof-of-concept for a middleware platform that runs agentic workflows defined in BPMN (Business Process Model and Notation).
-   **Key Files:**
    -   `WorkflowGameGenerator.bpmn`: The workflow definition, viewable in tools like `bpmn.io`.
    -   `baios.py`: The main orchestrator that uses the `SpiffWorkflow` library to parse and execute the BPMN file.
    -   `agent_storyline.py`: A plain Python class that acts as an "agent" invoked by a task in the workflow.
-   **Key Learnings:** BPMN provides a visual, structured way to define complex agent interactions. `SpiffWorkflow` is a lightweight Python engine capable of executing these definitions and orchestrating the calls to agent-like Python objects.

### 7. `ai-bob-realtime` - Real-Time Voice App

-   **Project Overview:** A single-page web application for real-time, bidirectional voice and text conversations with OpenAI's Realtime API.
-   **Architecture:**
    -   **Frontend (`/public`):** Handles all real-time logic using native browser `RTCPeerConnection` APIs. It does **not** use the `openai` JS SDK.
    -   **Backend (`server.js`):** A minimal Node.js server with a single purpose: securely vending ephemeral API keys to the frontend to avoid exposing the permanent key.
-   **Key Learnings:** This project demonstrates the correct and secure architectural pattern for building browser-based WebRTC applications with OpenAI's Realtime API, emphasizing a "thick client" and a minimal, security-focused backend.