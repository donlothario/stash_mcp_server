"""Stash MCP Server - Main entry point.

This module serves as the main entry point for the Stash MCP Server,
coordinating the initialization and execution of the FastMCP server
with all registered tools and prompts.
"""

import logging

from fastmcp import FastMCP

from .connection import connect_to_stash
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools

logger: logging.Logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="Stash MCP")

# Register all tools, prompts, and resources
register_tools(mcp)
register_prompts(mcp)
register_resources(mcp)


def main() -> None:
    """Run the MCP server.

    Notes
    -----
    Default transport is stdio for local MCP integration. Uncomment the
    HTTP line for network serving inside a container environment.
    """
    # Attempt an early connection (non-fatal - tools will retry if needed)
    connect_to_stash()

    # Choose transport mode
    # For container/network deployment:
    # mcp.run(transport="http", host="0.0.0.0", port=9001)

    # For local stdio integration:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
