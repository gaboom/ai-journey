import sys
import os
import logging
import anyio
import json
import re
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
    Launches the mcp_profile.py server and interacts with it using a compliant,
    sequential request/response flow, while also capturing stderr for debugging.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "mcp_profile.py")
    server_command = [sys.executable, server_path]
    log.info(f"Launching server with command: {' '.join(server_command)}")

    try:
        async with await anyio.open_process(server_command) as process:
            log.info("Server process started.")

            # --- Helper Functions ---
            read_buffer = b''

            async def send_message(message):
                """Helper to send a single line of JSON."""
                message_to_send = json.dumps(message, separators=(',', ':')) + '\n'
                message_bytes = message_to_send.encode('utf-8')
                log.info(f"--> SENDING (raw): {repr(message_bytes)}")
                await process.stdin.send(message_bytes)

            async def read_message():
                """Reads and parses one line of JSON from stdout."""
                nonlocal read_buffer
                while b'\n' not in read_buffer:
                    read_buffer += await process.stdout.receive()
                
                line_bytes, _, read_buffer = read_buffer.partition(b'\n')
                line_str = line_bytes.decode('utf-8').strip()

                if not line_str:
                    return await read_message() # Skip empty lines
                
                log.info(f"--> RECEIVED (raw): {repr(line_str)}")
                msg = json.loads(line_str)
                return msg

            async def log_stderr():
                """Monitors the server's stderr stream and logs any output."""
                async for line in process.stderr:
                    log.warning(f"[SERVER-STDERR] {line.decode('utf-8').strip()}")

            # --- Main Execution Logic ---
            async with anyio.create_task_group() as tg:
                tg.start_soon(log_stderr) # Start the stderr logger in the background

                # 1. Initialize
                init_request = {
                    "jsonrpc": "2.0", "method": "initialize", "id": "init00",
                    "params": {
                        "protocolVersion": "1.0",
                        "clientInfo": {"name": "test-rpc-client", "version": "1.0.0"},
                        "capabilities": {}
                    }
                }
                await send_message(init_request)
                init_response = await read_message()
                assert init_response.get("id") == "init00" and "result" in init_response, "Initialization failed"
                log.info("Initialization successful.")

                # 2. Send Initialized Notification (as per MCP spec)
                initialized_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
                await send_message(initialized_notification)
                log.info("Sent 'initialized' notification.")

                # 3. List Tools
                list_tools_request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": "list-1"}
                await send_message(list_tools_request)
                list_tools_response = await read_message()
                assert list_tools_response.get("id") == "list-1" and "result" in list_tools_response, "List tools failed"
                tool_names = [t['name'] for t in list_tools_response.get("result", {}).get("tools", [])]
                assert "get_user_token" in tool_names, "Tool 'get_user_token' not found"
                log.info("Tool discovery successful.")

                # 3. Call Tool
                tool_request = {
                    "jsonrpc": "2.0", "method": "tools/call", "id": "tool-1",
                    "params": {"name": "get_user_token", "arguments": {"user": "Alice"}}
                }
                await send_message(tool_request)
                tool_response = await read_message()
                assert tool_response.get("id") == "tool-1" and "result" in tool_response, "Tool call failed"
                content = tool_response.get("result", {}).get("content", [{}])[0].get("text", "")
                
                print("\n" + "="*30)
                log.info("--- Final Verification ---")
                print(f"Success! Server Response: {content}")
                assert content.startswith("User Alice has secret token ")
                token = content.split(" ")[-1]
                assert len(token) == 8 and token.isalnum() and re.match(r'ALIC\d{4}', token)
                print("Token format verified.")
                print("="*30 + "\n")

                # 4. Close stdin to allow the server process to exit cleanly
                await process.stdin.aclose()

    except Exception as e:
        log.error(f"An error occurred in the client: {e}", exc_info=True)

    log.info("Client finished.")


if __name__ == "__main__":
    anyio.run(main)