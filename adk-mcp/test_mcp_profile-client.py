import sys
import os
import logging
import anyio
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [CLIENT] - %(message)s',
)
log = logging.getLogger()
# --- End Logging Setup ---

async def main():
    """
    Tests the mcp_profile.py server by launching it as a subprocess
    using the officially documented stdio_client with StdioServerParameters.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "mcp_profile.py")
    log.info(f"Target server script: {server_path}")

    # 1. Define the server parameters using the correct class
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path]
    )

    log.info(f"Connecting to server with command: '{server_params.command} {' '.join(server_params.args)}'")

    try:
        # 2. Use stdio_client with the server parameters object
        async with stdio_client(server_params) as (read, write):
            # 3. Establish the high-level session
            async with ClientSession(read, write) as session:
                await session.initialize()
                log.info("MCP session initialized successfully.")

                # Optional: List tools to verify connection
                list_tools_response = await session.list_tools()
                tool_names = [t.name for t in list_tools_response.tools]
                log.info(f"Discovered tools: {tool_names}")
                assert "get_user_token" in tool_names

                # 4. Call the tool
                tool_args = {"user": "Alice"}
                log.info(f"Calling tool 'get_user_token' with args: {tool_args}")
                tool_result = await session.call_tool("get_user_token", tool_args)

                # 5. Print and verify the result
                print("\n" + "="*30)
                log.info("--- Received MCP Response ---")
                if tool_result.content and isinstance(tool_result.content[0], types.TextContent):
                    response_text = tool_result.content[0].text
                    print(f"Success! Server Response: {response_text}")
                    assert "XCMP0618" in response_text
                elif tool_result.isError:
                    print(f"❌ Error! Server returned an error: {tool_result.content}")
                else:
                    print(f"❓ Server returned an unexpected response: {tool_result}")
                print("="*30 + "\n")

    except Exception as e:
        log.error(f"An error occurred in the client: {e}", exc_info=True)
        raise

    log.info("Client finished successfully.")


if __name__ == "__main__":
    anyio.run(main)
