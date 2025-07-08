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

            # Manually create and encode the JSON-RPC message
            request = {
                "jsonrpc": "2.0",
                "method": "tool",
                "params": {
                    "tool_name": "get_user_token",
                    "arguments": {"user": "Alice"}
                },
                "id": "test-1"
            }
            
            # The server expects a specific framing format: Content-Length header then the message
            message_bytes = json.dumps(request).encode('utf-8')
            header = f"Content-Length: {len(message_bytes)}\r\n\r\n".encode('utf-8')
            
            log.info(f"Sending raw JSON-RPC message: {request}")
            await process.stdin.send(header + message_bytes)

            # Read the response
            response_header = await process.stdout.receive_some(1024)
            if b'Content-Length' in response_header:
                # A real implementation would parse the length properly
                response_body_bytes = await process.stdout.receive()
                response_data = json.loads(response_body_bytes)

                print("\n" + "="*30)
                log.info("--- Received MCP Response ---")
                content = response_data.get("result", {}).get("content", [{}])[0].get("text", "N/A")
                print(f"✅ Success! Server Response: {content}")
                log.info(f"Full message: {json.dumps(response_data, indent=2)}")
                print("="*30 + "\n")
            else:
                log.warning("Did not receive a valid Content-Length header.")
                log.warning(f"Raw response: {response_header.decode()}")


    except Exception as e:
        log.error(f"An error occurred in the client: {e}", exc_info=True)

    log.info("Client finished.")


if __name__ == "__main__":
    anyio.run(main)