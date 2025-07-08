import sys
import os
import logging
import anyio
import json
from mcp import types

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [CLIENT] - %(message)s',
)
log = logging.getLogger()
# --- End Logging Setup ---

async def main():
    """
    Launches the mcp_profile.py server and interacts with it using anyio,
    with manual JSON encoding to bypass the SessionMessage issue.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "mcp_profile.py")
    server_command = [sys.executable, server_path]
    log.info(f"Launching server with command: {' '.join(server_command)}")

    try:
        async with await anyio.open_process(server_command) as process:
            log.info("Server process started.")

            # A proper MCP session involves an initialize message first.
            init_request = {"jsonrpc": "2.0", "method": "initialize", "params": {"mcp_version": "1.0"}, "id": "init"}
            list_tools_request = {"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": "list-1"}
            tool_request = {
                "jsonrpc": "2.0",
                "method": "tool",
                "params": {"tool_name": "get_user_token", "arguments": {"user": "Alice"}},
                "id": "tool-1"
            }

            async def send_message(message):
                """Helper to frame and send a single message."""
                message_bytes = json.dumps(message).encode('utf-8')
                header = f"Content-Length: {len(message_bytes)}\r\n\r\n".encode('utf-8')
                log.info(f"Sending: {message}")
                await process.stdin.send(header + message_bytes)

            # Send all messages in sequence
            await send_message(init_request)
            await send_message(list_tools_request)
            await send_message(tool_request)

            # Close stdin to signal that we are done sending data. This is critical.
            await process.stdin.aclose()

            # Read the response
            log.info("Reading response from server...")
            response_bytes = await process.stdout.receive()
            
            # A real client would parse the Content-Length header properly.
            # For this test, we assume the full response is in one chunk after the header.
            try:
                header_str, json_str = response_bytes.decode('utf-8').split('\r\n\r\n', 1)
                response_data = json.loads(json_str)

                print("\n" + "="*30)
                log.info("--- Received MCP Response ---")
                
                # The tool response is the second message. A real client would check the ID.
                content = response_data.get("result", {}).get("content", [{}])[0].get("text", "N/A")
                print(f"✅ Success! Server Response: {content}")
                log.info(f"Full message: {json.dumps(response_data, indent=2)}")
                print("="*30 + "\n")

            except (ValueError, IndexError) as e:
                log.error(f"Failed to parse server response: {e}")
                log.error(f"Raw response: {response_bytes.decode('utf-8')}")

    except Exception as e:
        log.error(f"An error occurred in the client: {e}", exc_info=True)

    log.info("Client finished.")


if __name__ == "__main__":
    # Use anyio.run to execute the main async function
    anyio.run(main)