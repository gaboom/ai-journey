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
