"""Stash connection management module.

This module handles the connection to the Stash instance with retry logic
and provides a singleton interface for accessing the Stash API.
"""

import logging
import time
from typing import Optional
from urllib.parse import urlparse

from stashapi.stashapp import StashInterface

from .config import (
    STASH_API_KEY,
    STASH_CONNECT_DELAY_SECONDS,
    STASH_CONNECT_RETRIES,
    STASH_ENDPOINT,
)

logger: logging.Logger = logging.getLogger(__name__)


class StashConnection:
    """Singleton class for managing Stash API connection.

    This class ensures only one connection instance exists and provides
    retry logic for connection attempts.
    """

    _instance: Optional['StashConnection'] = None
    _stash_interface: Optional[StashInterface] = None

    def __new__(cls) -> 'StashConnection':
        """Ensure only one instance of StashConnection exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Optional[StashInterface]:
        """Attempt to connect to the Stash instance with retries.

        Returns
        -------
        Optional[StashInterface]
            Connected interface or None if connection failed.
        """
        if self._stash_interface is not None:
            return self._stash_interface

        last_error: Optional[Exception] = None

        for attempt in range(1, STASH_CONNECT_RETRIES + 1):
            try:
                logger.info(
                    "Connecting to Stash (attempt %d/%d) at %s...",
                    attempt,
                    STASH_CONNECT_RETRIES,
                    STASH_ENDPOINT,
                )

                parsed = urlparse(STASH_ENDPOINT)
                self._stash_interface = StashInterface({
                    "scheme": parsed.scheme or "http",
                    "host": parsed.hostname or "localhost",
                    "port": parsed.port or 9999,
                    "logger": None,
                    "apikey": STASH_API_KEY,
                })

                logger.info("Connected to Stash at %s", STASH_ENDPOINT)
                return self._stash_interface

            except ImportError:
                logger.error(
                    "stashapi library not installed. "
                    "Install with: pip install stashapi"
                )
                return None

            except Exception as err:
                last_error = err
                logger.warning(
                    "Connection attempt %d failed: %s", attempt, err
                )
                if attempt < STASH_CONNECT_RETRIES:
                    time.sleep(STASH_CONNECT_DELAY_SECONDS)

        logger.error(
            "Failed to connect to Stash after %d attempts: %s",
            STASH_CONNECT_RETRIES,
            last_error
        )
        return None

    def get_interface(self) -> StashInterface:
        """Get the Stash interface, connecting if necessary.

        Returns
        -------
        StashInterface
            The connected Stash interface.

        Raises
        ------
        RuntimeError
            If connection to Stash cannot be established.
        """
        if self.connect() is None:
            raise RuntimeError(
                "Stash connection not available. "
                "Check your configuration and network connection."
            )
        assert self._stash_interface is not None
        return self._stash_interface

    def is_connected(self) -> bool:
        """Check if currently connected to Stash.

        Returns
        -------
        bool
            True if connected, False otherwise.
        """
        return self._stash_interface is not None

    def disconnect(self) -> None:
        """Disconnect from Stash and reset the connection."""
        self._stash_interface = None
        logger.info("Disconnected from Stash")


# Singleton instance for easy access
_connection = StashConnection()


def get_stash_interface() -> StashInterface:
    """Get the global Stash interface instance.

    This is a convenience function that returns the singleton
    StashInterface instance.

    Returns
    -------
    StashInterface
        The connected Stash interface.

    Raises
    ------
    RuntimeError
        If connection to Stash cannot be established.
    """
    return _connection.get_interface()


def connect_to_stash() -> Optional[StashInterface]:
    """Attempt to connect to Stash (legacy compatibility function).

    Returns
    -------
    Optional[StashInterface]
        Connected interface or None if connection failed.
    """
    return _connection.connect()


def is_stash_connected() -> bool:
    """Check if connected to Stash.

    Returns
    -------
    bool
        True if connected, False otherwise.
    """
    return _connection.is_connected()
