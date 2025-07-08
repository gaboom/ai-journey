# mcp_profile.py
import logging
from mcp.server.fastmcp import FastMCP

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
        return f"User {user} has secret token XCMP0618"

    return server

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    # The .run() method listens on stdio by default
    server.run(transport="stdio")