"""
A high-level, LangChain-based client for interacting with an MCP server.

This client uses the self-contained MCPToolkit to automatically discover
and configure tools from the server, and then uses a LangChain
AgentExecutor to orchestrate the conversation.
"""
import asyncio
import os
import logging

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from mcp_toolkit import MCPToolkit

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
log = logging.getLogger()
# --- End Logging Setup ---


async def main():
    """
    Connects to the MCP server, discovers tools, and runs a query
    using a LangChain agent.
    """
    server_url = "http://localhost:8181/mcp/"
    
    try:
        # Use the MCPToolkit as an async context manager.
        # It handles the connection, session, and cleanup automatically.
        async with MCPToolkit(url=server_url) as toolkit:
            
            # 1. Discover tools automatically from the server
            mcp_tools = await toolkit.get_tools_async()
            if not mcp_tools:
                log.error("No tools discovered from the server. Exiting.")
                return

            # 2. Set up the LLM and a prompt template
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # 3. Create the LangChain agent
            agent = create_openai_tools_agent(llm, mcp_tools, prompt)

            # 4. Create the AgentExecutor that runs the conversation loop
            agent_executor = AgentExecutor(agent=agent, tools=mcp_tools, verbose=True)

            # 5. Invoke the agent with a user question
            log.info("Invoking agent with user question...")
            user_question = "Based ONLY AND EXCLUSIVELY on the PROFILE of Sing-Ming Pei Tue de Santos III., what could be his profession today?"
            
            response = await agent_executor.ainvoke({
                "input": user_question
            })

            log.info(f"\n--- Final Answer ---\n{response['output']}")

    except ConnectionRefusedError:
        log.error(f"Connection to MCP server at {server_url} was refused. Is server.py running?")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        log.error("The OPENAI_API_KEY environment variable is not set. Please set it before running.")
    else:
        asyncio.run(main())
