# PoC for Exploring LLM Tools with Ollama

This project serves as a proof-of-concept for exploring agentic tool usage with a locally running Ollama model (`llama3.2`). It provides two parallel implementations using popular Python libraries: LangChain and LlamaIndex.

## Key Files

- `langchain.py`: Demonstrates how to create a tool-calling agent using **LangChain**. It connects to Ollama's OpenAI-compatible API endpoint.
- `llamaindex.py`: Demonstrates how to create a tool-calling agent using **LlamaIndex**. It uses the native `llama-index-llms-ollama` integration for a direct connection.
- `requirements.txt`: Contains the necessary Python dependencies for both implementations.

## Setup

1.  **Ollama Installation**: Ensure you have [Ollama](https://ollama.com/) installed and running locally.
2.  **Pull the Model**: Download the required model by running:
    ```bash
    ollama pull llama3.2
    ```
3.  **Virtual Environment**: It is highly recommended to use a Python virtual environment.
    ```bash
    # Create the virtual environment
    python -m venv .venv

    # Activate it (Windows PowerShell)
    .venv\Scripts\Activate.ps1

    # Activate it (Linux/macOS)
    # source .venv/bin/activate
    ```
4.  **Install Dependencies**: Install the required packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Once the setup is complete, you can run either of the proof-of-concept scripts:

**To run the LangChain example:**
```bash
python langchain.py
```

**To run the LlamaIndex example:**
```bash
python llamaindex.py
```

Both scripts will execute a simple agent that uses an `add` tool to calculate the sum of two numbers and will print the verbose output of the agent's reasoning process.
