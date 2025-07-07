import asyncio
import os
import json
import logging
from openai import AsyncOpenAI
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
log = logging.getLogger()
# --- End Logging Setup ---

# Initialize the OpenAI client
openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define the get_profile function as a tool for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "Gets a profile message for a given name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the person."},
                },
                "required": ["name"],
            },
        },
    }
]

async def call_mcp_tool(session: ClientSession, function_name: str, function_args: dict) -> str:
    """
    Calls a tool on the MCP server and aggregates the streaming response.
    """
    log.info(f"LLM decided to call tool: '{function_name}' with args: {function_args}")
    
    profile_parts = []
    try:
        # Await the result from the tool call
        tool_result = await session.call_tool(function_name, function_args)
        log.info(f"Received tool result object: {tool_result}")

        # The result's 'content' is a list of content objects.
        if tool_result.content:
            for content_item in tool_result.content:
                log.info(f"  > Processing content item: {content_item} (type: {type(content_item)})")
                if isinstance(content_item, types.TextContent):
                    profile_parts.append(content_item.text)
                elif isinstance(content_item, str):
                    profile_parts.append(content_item)
                else:
                    log.warning(f"  > Received unexpected content type: {type(content_item)}")
        else:
            log.warning("Tool call returned no content.")

    except Exception as e:
        log.error(f"An error occurred during the MCP tool call: {e}", exc_info=True)
        # Re-raise the exception to allow the main loop to see it
        raise

    function_response = " ".join(profile_parts)
    log.info(f"Assembled response from MCP server: \"{function_response}\"")
    return function_response

async def run_conversation(session: ClientSession, user_prompt: str):
    """
    Orchestrates the interaction between the user, the LLM, and the MCP tool.
    """
    log.info(f"--- New Conversation ---")
    log.info(f"User question: \"{user_prompt}\"")
    messages = [{"role": "user", "content": user_prompt}]

    try:
        # First API call to the LLM
        response = await openai_client.chat.completions.create(
            model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute the tool call
            function_response = await call_mcp_tool(session, function_name, function_args)

            messages.append(
                {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": function_response}
            )

            # Second API call to the LLM with the tool's result
            log.info("Sending tool result back to LLM for final answer...")
            second_response = await openai_client.chat.completions.create(
                model="gpt-4o", messages=messages
            )
            final_answer = second_response.choices[0].message.content
            log.info(f"Final Answer: {final_answer}")
        else:
            final_answer = response_message.content
            log.info(f"LLM answered directly: {final_answer}")

    except Exception as e:
        log.error(f"An error occurred during the conversation flow: {e}", exc_info=True)


async def main():
    """
    Connects to the MCP server and runs the conversation orchestrator.
    """
    server_url = "http://localhost:8181/mcp/"
    log.info(f"Attempting to connect to MCP server at {server_url}...")

    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            log.info("HTTP client connected. Creating session...")
            async with ClientSession(read, write) as session:
                await session.initialize()
                log.info("MCP session initialized successfully.")

                user_question = "Based on the profile of Alan Turing, what could be his profession currently?"
                await run_conversation(session, user_question)

    except ConnectionRefusedError:
        log.error(f"Connection to MCP server at {server_url} was refused. Is server.py running?")
    except Exception as e:
        # This will now catch errors from the TaskGroup and log them
        log.error(f"An unexpected error occurred in the main task group: {e}", exc_info=True)


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        log.error("The OPENAI_API_KEY environment variable is not set. Please set it before running.")
    else:
        asyncio.run(main())