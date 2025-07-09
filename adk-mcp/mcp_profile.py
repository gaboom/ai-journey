# mcp_profile.py
import logging
import random
import re
from mcp.server.fastmcp import FastMCP

def _get_secret(name: any) -> str:
    """Generates a secret token based on a name."""
    # Convert to string.
    result = str(name)

    # Remove everything but [a-zA-Z0-9] and uppercase what is left.
    result = re.sub(r'[^a-zA-Z0-9]', '', result).upper()

    # Empty defaults to "NULL".
    if not result:
        result = "NULL"
    
    # base is the first four symbols
    result = result[:4]

    # pad name with random numbers (0-9) to length 8
    return result + ''.join(random.choice('0123456789') for _ in range(8 - len(result)))

def create_server() -> FastMCP:
    """Create and configure the Profile MCP server."""
    server = FastMCP(
        name="Profile",
        description="A server for retrieving user profile information.",
    )

    @server.tool()
    def get_user_token(user: str) -> str:
        """Gets a secret token for a given user."""
        logging.info(f"Tool: Getting token for user: {user}")
        secret = _get_secret(user)
        return f"User {user} has secret token {secret}"

    return server

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    # The .run() method listens on stdio by default
    server.run(transport="stdio")