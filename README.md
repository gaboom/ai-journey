# AI Journey

This repository documents a journey of exploration into building and interacting with Large Language Models (LLMs), from basic command-line tools to sophisticated, multi-tool agents.

## Core Areas of Exploration

### 1. Foundational LLM Interaction
- **`ochat/`**: A simple, yet powerful command-line tool for streaming conversations with local Ollama models, including support for multimodal image inputs.

### 2. Local Tool Calling with Ollama
- **`tool/`**: A proof-of-concept demonstrating how to make a local Ollama model use tools. It provides parallel implementations using both **LangChain** and **LlamaIndex**, showcasing different approaches to agentic tool use.

### 3. Model-Context-Protocol (MCP)
- **`mcp/`**: A deep dive into the Model-Context-Protocol. This directory contains:
    - A Python-based MCP server (`server.py`) that exposes tools over HTTP.
    - A low-level manual client (`client.py`) for understanding core orchestration.
    - A high-level LangChain agent (`mcp_client.py`) that uses a custom `MCPToolkit` for automatic tool discovery.

### 4. Advanced Agentic Workflows with Google ADK
- **`adk-agent/`**: Demonstrates a state-of-the-art, declarative agent using the Google Agent Development Kit (ADK). This agent connects to the HTTP-based MCP server from the `mcp/` directory, showcasing framework-native tool discovery and orchestration.
- **`adk-mcp/`**: Showcases a powerful and modular ADK agent that dynamically loads tools from multiple, independent, local processes over `stdio`. This agent combines tools written in both Python and Node.js (via `npx`), providing capabilities for user profiles, filesystem operations, and Wikipedia lookups.

## Future Projects
- **ai-bob**: A planned Raspberry Pi-based physical assistant. (See https://github.com/gaboom/ai-bob)
- **baios**: An experimental operating system for AI agents. (See https://github.com/gaboom/baios)

## Setup & Notes
- An OpenAI API Key, Google Cloud credentials, Python, Ollama, and Node.js are required to run all examples.
- The Gemini CLI (https://github.com/google-gemini/gemini-cli) was used extensively during development.