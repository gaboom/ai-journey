from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Define Tools
@tool
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

# 2. Create the Agent
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Use ChatOpenAI and point it to the local Ollama endpoint
llm = ChatOpenAI(
    model="llama3.2",
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
    temperature=0,
)

tools = [add]
agent = create_tool_calling_agent(llm, tools, prompt)

# 3. Create the Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 4. Run the Agent
def main():
    """Main function to run the LangChain agent."""
    print("Running LangChain agent with OpenAI-compatible endpoint...")
    try:
        response = agent_executor.invoke({"input": "What is 5 + 7?"})
        print("\n--- Final Response ---")
        print(response.get("output"))
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
