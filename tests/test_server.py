"""Fixed tests for the main Stash MCP Server module.

This module tests the server initialization, tool registration,
and basic server functionality.
"""

from unittest.mock import patch
from fastmcp import Client

from stash_mcp_server.server import mcp, main


async def test_server_initialization() -> None:
    """Test that the server initializes correctly.

    Verifies that the FastMCP server instance is created with
    the correct name and configuration.
    """
    assert mcp.name == "Stash MCP"
    assert mcp is not None


async def test_server_has_tools() -> None:
    """Test that the server has tools registered.

    Verifies that tools are properly registered during server
    initialization.
    """
    tools = await mcp.get_tools()
    assert len(tools) > 0, "Server should have at least one tool registered"


async def test_server_tool_names() -> None:
    """Test that expected tools are registered with correct names.

    Verifies that all core tools are present in the server.
    """
    tools = await mcp.get_tools()
    # get_tools() returns a dict mapping names to tool definitions
    if isinstance(tools, dict):
        tool_names = list(tools.keys())
    elif isinstance(tools, list):
        tool_names = [t if isinstance(t, str) else t.name for t in tools]
    else:
        tool_names = []

    expected_tools = [
        "get_performer_info",
        "get_all_performers",
        "get_all_scenes",
        "get_all_scenes_from_performer",
        "health_check",
        "advanced_performer_analysis",
        "batch_performer_insights",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, (
            f"Tool '{expected_tool}' should be registered"
        )


async def test_server_has_prompts() -> None:
    """Test that the server has prompts registered.

    Verifies that prompts are properly registered during server
    initialization.
    """
    prompts = await mcp.get_prompts()
    assert len(prompts) > 0, (
        "Server should have at least one prompt registered"
    )


async def test_server_prompt_names() -> None:
    """Test that expected prompts are registered.

    Verifies that all core prompts are present in the server.
    """
    prompts = await mcp.get_prompts()
    # get_prompts() returns a dict mapping names to prompt definitions
    if isinstance(prompts, dict):
        prompt_names = list(prompts.keys())
    elif isinstance(prompts, list):
        prompt_names = [p if isinstance(p, str) else p.name for p in prompts]
    else:
        prompt_names = []

    expected_prompts = [
        "analyze-performer",
        "library-insights",
        "recommend-scenes",
        "discover-performers",
    ]

    for expected_prompt in expected_prompts:
        assert expected_prompt in prompt_names, (
            f"Prompt '{expected_prompt}' should be registered"
        )


async def test_server_client_connection() -> None:
    """Test that a client can connect to the server.

    Verifies that the in-memory transport works correctly and
    the client can establish a connection.
    """
    async with Client(mcp) as client:
        # Test that client is connected
        result = await client.ping()
        assert result is True, "Client should be able to ping server"


async def test_server_list_tools_via_client() -> None:
    """Test that tools can be listed through a client connection.

    Verifies that the MCP protocol correctly exposes available tools.
    """
    async with Client(mcp) as client:
        tools_response = await client.list_tools()
        assert len(tools_response) > 0, (
            "Client should receive list of available tools"
        )


async def test_server_list_prompts_via_client() -> None:
    """Test that prompts can be listed through a client connection.

    Verifies that the MCP protocol correctly exposes available prompts.
    """
    async with Client(mcp) as client:
        prompts_response = await client.list_prompts()
        assert len(prompts_response) > 0, (
            "Client should receive list of available prompts"
        )


def test_main_function_with_mocked_connection() -> None:
    """Test the main function executes without errors.

    Verifies that the main function initializes and configures
    the server correctly.
    """
    with patch('stash_mcp_server.server.connect_to_stash') as mock_connect, \
            patch('stash_mcp_server.server.mcp.run') as mock_run:
        # Note: We can't actually run the server since it blocks,
        # but we can test that main() sets it up correctly
        main()

        # Verify that connection was attempted
        mock_connect.assert_called_once()

        # Verify that the server was configured to run
        mock_run.assert_called_once_with(transport="stdio")
