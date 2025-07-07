from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

# 1. Define a simple tool function
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    print(f"--- Tool 'add' is executing with {a} and {b} ---")
    return a + b

# 2. Create LlamaIndex Tool and LLM
add_tool = FunctionTool.from_defaults(fn=add)

# Use the native Ollama LLM
llm = Ollama(model="llama3.2", request_timeout=120.0)

# 3. Create the Agent
# This is the modern, non-deprecated way to create a ReAct agent
agent = ReActAgent.from_tools(
    tools=[add_tool],
    llm=llm,
    verbose=True
)

# 4. Run the Agent
def main():
    """Main function to run the LlamaIndex agent."""
    print("Running LlamaIndex agent with native Ollama integration...")
    try:
        response = agent.chat("What is 5 + 7?")
        print("\n--- Final Response ---")
        print(str(response))
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()


