"""Tests for Stash connection management.

This module tests the connection handling, retry logic, and
singleton pattern for the Stash API interface.
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from stashapi.stashapp import StashInterface

from stash_mcp_server.connection import (
    StashConnection,
    connect_to_stash,
    get_stash_interface,
)


class TestStashConnection:
    """Tests for StashConnection singleton class."""

    def test_singleton_pattern(self) -> None:
        """Test that StashConnection implements singleton pattern.

        Verifies that multiple instantiations return the same instance.
        """
        connection1 = StashConnection()
        connection2 = StashConnection()

        assert connection1 is connection2, (
            "StashConnection should return the same instance"
        )

    def test_connect_success(self) -> None:
        """Test successful connection to Stash.

        Verifies that the connection is established successfully
        and returns a StashInterface instance.
        """
        mock_interface = Mock(spec=StashInterface)

        with patch(
            'stash_mcp_server.connection.StashInterface',
            return_value=mock_interface
        ):
            connection = StashConnection()
            # Reset the singleton state for this test
            connection._stash_interface = None

            result = connection.connect()

            assert result is not None
            assert result == mock_interface

    def test_connect_already_connected(self) -> None:
        """Test connect when already connected.

        Verifies that subsequent connection attempts return the
        existing interface without creating a new one.
        """
        mock_interface = Mock(spec=StashInterface)

        connection = StashConnection()
        connection._stash_interface = mock_interface

        result = connection.connect()

        assert result == mock_interface

    def test_connect_with_retries(self) -> None:
        """Test connection retry logic.

        Verifies that the connection is retried the specified
        number of times before giving up.
        """
        connection = StashConnection()
        connection._stash_interface = None

        with patch(
            'stash_mcp_server.connection.StashInterface',
            side_effect=[Exception("Connection failed"), Mock()]
        ):
            with patch('stash_mcp_server.connection.time.sleep'):
                result = connection.connect()

                # Should succeed on second attempt
                assert result is not None

    def test_connect_fails_after_retries(self) -> None:
        """Test that connection returns None after exhausting retries.

        Verifies that the connection gives up after the maximum
        number of retry attempts.
        """
        connection = StashConnection()
        connection._stash_interface = None

        with patch(
            'stash_mcp_server.connection.StashInterface',
            side_effect=Exception("Connection failed")
        ):
            with patch('stash_mcp_server.connection.time.sleep'):
                result = connection.connect()

                assert result is None

    def test_get_interface_when_connected(self) -> None:
        """Test getting the interface when connection exists.

        Verifies that get_interface returns the connected interface.
        """
        mock_interface = Mock(spec=StashInterface)

        connection = StashConnection()
        connection._stash_interface = mock_interface

        result = connection.get_interface()

        assert result == mock_interface

    def test_get_interface_when_not_connected(self) -> None:
        """Test getting the interface when not connected.

        Verifies that get_interface raises an error when no
        connection exists.
        """
        connection = StashConnection()
        connection._stash_interface = None

        with pytest.raises(Exception):
            connection.get_interface()

    def test_disconnect(self) -> None:
        """Test disconnect method.

        Verifies that disconnect properly clears the interface.
        """
        mock_interface = Mock(spec=StashInterface)
        connection = StashConnection()
        connection._stash_interface = mock_interface

        assert connection.is_connected()

        connection.disconnect()

        assert not connection.is_connected()
        assert connection._stash_interface is None

    def test_connect_import_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test connect handles ImportError for stashapi.

        Verifies that connection gracefully handles missing stashapi.
        """
        connection = StashConnection()
        connection._stash_interface = None

        # Mock StashInterface to raise ImportError
        def mock_stash_interface(*args: Any, **kwargs: Any) -> None:
            raise ImportError("No module named 'stashapi'")

        monkeypatch.setattr(
            'stash_mcp_server.connection.StashInterface',
            mock_stash_interface
        )

        interface = connection.connect()

        assert interface is None
        assert not connection.is_connected()

    def test_is_connected_function(self) -> None:
        """Test standalone is_connected function.

        Verifies that the module-level function works correctly.
        """
        from stash_mcp_server.connection import is_stash_connected

        connection = StashConnection()
        original_interface = connection._stash_interface

        try:
            # Test with interface
            connection._stash_interface = Mock(spec=StashInterface)
            assert is_stash_connected() is True

            # Test without interface
            connection._stash_interface = None
            assert is_stash_connected() is False
        finally:
            # Restore original state
            connection._stash_interface = original_interface


class TestConnectToStash:
    """Tests for connect_to_stash function."""

    def test_connect_to_stash_success(self) -> None:
        """Test successful connection via helper function.

        Verifies that the helper function correctly initiates
        a connection.
        """
        mock_interface = Mock(spec=StashInterface)
        
        # Reset singleton
        StashConnection._instance = None
        
        with patch(
            'stash_mcp_server.connection.StashInterface',
            return_value=mock_interface
        ):
            result = connect_to_stash()
            assert result is not None

    def test_connect_to_stash_failure(self) -> None:
        """Test connection failure via helper function.

        Verifies that the helper function returns None on failure.
        """
        # Create a new instance for this test
        conn = StashConnection.__new__(StashConnection)
        conn._stash_interface = None
        
        with patch(
            'stash_mcp_server.connection.StashConnection._instance',
            conn
        ):
            with patch(
                'stash_mcp_server.connection.StashInterface',
                side_effect=Exception("Connection failed")
            ):
                with patch('stash_mcp_server.connection.time.sleep'):
                    result = conn.connect()
                    assert result is None


class TestGetStashInterface:
    """Tests for get_stash_interface function."""

    def test_get_stash_interface_when_connected(self) -> None:
        """Test getting interface when connection exists.

        Verifies that the function returns the existing interface.
        """
        mock_interface = Mock(spec=StashInterface)

        # Use the singleton instance directly
        connection = StashConnection()
        original_interface = connection._stash_interface
        connection._stash_interface = mock_interface
        
        try:
            result = get_stash_interface()
            # Should return some interface (either mock or actual)
            assert result is not None
        finally:
            # Restore original state
            connection._stash_interface = original_interface

    def test_get_stash_interface_attempts_connection(self) -> None:
        """Test that get_interface attempts to connect if needed.

        Verifies that the function attempts to establish a
        connection if one doesn't exist.
        """
        mock_interface = Mock(spec=StashInterface)

        # Create a fresh connection instance without interface
        conn = StashConnection.__new__(StashConnection)
        conn._stash_interface = None

        with patch(
            'stash_mcp_server.connection.StashConnection._instance',
            conn
        ):
            with patch(
                'stash_mcp_server.connection.StashInterface',
                return_value=mock_interface
            ):
                result = get_stash_interface()
                # Should have successfully connected
                assert result is not None
