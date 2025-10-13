"""Shared pytest fixtures for Stash MCP Server tests.

This module provides reusable fixtures for testing the Stash MCP server,
including mock Stash interfaces, sample data, and server configurations.
"""

from typing import TYPE_CHECKING, Any, Dict, List
from unittest.mock import Mock

import pytest
from stashapi.stashapp import StashInterface

from stash_mcp_server.server import mcp

if TYPE_CHECKING:
    from fastmcp import FastMCP


@pytest.fixture
def mock_stash_interface() -> Mock:
    """Create a mock StashInterface for testing.

    Returns
    -------
    Mock
        Mocked StashInterface with common methods.
    """
    mock = Mock(spec=StashInterface)
    mock._server_url = "http://localhost:9999"
    return mock


@pytest.fixture
def sample_performer() -> Dict[str, Any]:
    """Provide sample performer data for testing.

    Returns
    -------
    Dict[str, Any]
        Sample performer dictionary with common fields.
    """
    return {
        "id": "123",
        "name": "Test Performer",
        "country": "USA",
        "ethnicity": "Caucasian",
        "eye_color": "Blue",
        "hair_color": "Blonde",
        "height_cm": 170,
        "weight": 65,
        "measurements": "34-24-36",
        "tattoos": ["arm", "back"],
        "piercings": ["navel"],
        "favorite": True,
    }


@pytest.fixture
def sample_scene() -> Dict[str, Any]:
    """Provide sample scene data for testing.

    Returns
    -------
    Dict[str, Any]
        Sample scene dictionary with common fields.
    """
    return {
        "id": "456",
        "title": "Test Scene",
        "rating100": 85,
        "organized": True,
        "tags": [
            {"id": "1", "name": "tag1"},
            {"id": "2", "name": "tag2"},
        ],
        "performers": [
            {"id": "123", "name": "Test Performer"}
        ],
    }


@pytest.fixture
def sample_scenes_list(sample_scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Provide list of sample scenes for testing.

    Parameters
    ----------
    sample_scene : Dict[str, Any]
        Base scene fixture.

    Returns
    -------
    List[Dict[str, Any]]
        List of scene dictionaries with varied ratings.
    """
    scenes = []
    for i in range(5):
        scene = sample_scene.copy()
        scene["id"] = str(456 + i)
        scene["title"] = f"Test Scene {i + 1}"
        scene["rating100"] = 60 + (i * 10)
        scenes.append(scene)
    return scenes


@pytest.fixture
def sample_performers_list(
    sample_performer: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Provide list of sample performers for testing.

    Parameters
    ----------
    sample_performer : Dict[str, Any]
        Base performer fixture.

    Returns
    -------
    List[Dict[str, Any]]
        List of performer dictionaries.
    """
    performers = []
    for i in range(3):
        performer = sample_performer.copy()
        performer["id"] = str(123 + i)
        performer["name"] = f"Test Performer {i + 1}"
        performers.append(performer)
    return performers


@pytest.fixture
def test_server() -> "FastMCP":
    """Provide the FastMCP server instance for testing.

    Returns
    -------
    FastMCP
        The configured MCP server instance.
    """
    return mcp
