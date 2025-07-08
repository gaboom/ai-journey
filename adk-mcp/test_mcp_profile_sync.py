import subprocess
import json
import os
import sys
import logging
from mcp.encoding.jsonrpc import create_json_rpc_messages, parse_json_rpc_messages

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [SYNC-CLIENT] - %(message)s',
)
log = logging.getLogger()
# --- End Logging Setup ---

def main():
    """
    Launches the mcp_profile.py server and interacts with it synchronously
    using standard subprocess pipes.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "mcp_profile.py")
    server_command = [sys.executable, server_path]
    log.info(f"Launching server with command: {' '.join(server_command)}")

    # Launch the server process, ensuring we work with bytes (text=False)
    process = subprocess.Popen(
        server_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Work with bytes, not text
    )

    try:
        # 1. Define the messages to be sent
        # A valid MCP session requires an initialization message first.
        init_message = {"mcp_version": "1.0"}
        tool_call_message = {
            "request_id": "test-sync-1",
            "tool_name": "get_user_token",
            "arguments": {"user": "Alice"}
        }

        # 2. Serialize the messages into the correct byte format
        init_bytes = create_json_rpc_messages([init_message])
        tool_call_bytes = create_json_rpc_messages([tool_call_message])

        # 3. Write the bytes to the server's stdin and close it
        log.info("Sending initialization message...")
        process.stdin.write(init_bytes)
        
        log.info("Sending tool call message...")
        process.stdin.write(tool_call_bytes)

        # Close stdin to signal that we are done sending data.
        # This is crucial for the server to process the request and not hang.
        process.stdin.close()

        # 4. Read the response bytes from stdout
        log.info("Reading response from server...")
        response_bytes = process.stdout.read()
        
        # Also read stderr to catch any server-side errors
        error_output = process.stderr.read().decode()
        if error_output:
            log.error(f"Server stderr:\n{error_output}")

        # 5. Parse the response
        if response_bytes:
            messages = parse_json_rpc_messages(response_bytes)
            print("\n" + "="*30)
            log.info("--- Received MCP Response ---")
            for msg in messages:
                # The actual tool result is inside the 'content' of the second message
                if msg.get("tool_name") == "get_user_token":
                    content = msg.get("content", [{}])[0].get("text", "N/A")
                    print(f"✅ Success! Server Response: {content}")
                    log.info(f"Full message: {json.dumps(msg, indent=2)}")
            print("="*30 + "\n")
        else:
            log.warning("No response received from server stdout.")

    finally:
        log.info("Client finished. Terminating server process...")
        process.terminate()
        process.wait()
        log.info("Server process terminated.")


if __name__ == "__main__":
    main()