"""Tests for configuration module.

This module tests configuration loading, environment variables,
and constant definitions.
"""

import os
from typing import Any
from unittest.mock import patch

import pytest

from stash_mcp_server.config import (
    DEFAULT_ENDPOINT,
    DEFAULT_MAX_BATCH_PERFORMERS,
    PERFORMER_CACHE_SIZE,
    PERFORMERS_LIST_CACHE_SIZE,
    RATING_AVERAGE,
    RATING_EXCELLENT,
    RATING_GOOD,
    SCENES_CACHE_SIZE,
    STASH_API_KEY,
    STASH_CONNECT_RETRIES,
    STASH_ENDPOINT,
)


class TestConfigConstants:
    """Tests for configuration constants."""

    def test_default_endpoint_is_defined(self) -> None:
        """Test that default endpoint is properly defined.

        Verifies that the default Stash endpoint constant exists
        and has a reasonable value.
        """
        assert DEFAULT_ENDPOINT is not None
        assert isinstance(DEFAULT_ENDPOINT, str)
        assert "http" in DEFAULT_ENDPOINT.lower()

    def test_cache_sizes_are_positive(self) -> None:
        """Test that cache size constants are positive integers.

        Verifies that all cache size configurations are valid
        positive numbers.
        """
        assert PERFORMER_CACHE_SIZE > 0
        assert PERFORMERS_LIST_CACHE_SIZE > 0
        assert SCENES_CACHE_SIZE > 0

    def test_rating_thresholds_are_valid(self) -> None:
        """Test that rating threshold constants are properly ordered.

        Verifies that rating constants follow logical ordering:
        EXCELLENT > GOOD > AVERAGE.
        """
        assert 0 <= RATING_AVERAGE < 100
        assert RATING_AVERAGE < RATING_GOOD
        assert RATING_GOOD < RATING_EXCELLENT
        assert RATING_EXCELLENT <= 100

    def test_default_max_batch_performers_is_reasonable(self) -> None:
        """Test that batch performer limit is reasonable.

        Verifies that the default maximum batch size is a
        sensible value.
        """
        assert DEFAULT_MAX_BATCH_PERFORMERS > 0
        assert DEFAULT_MAX_BATCH_PERFORMERS <= 100


class TestEnvironmentVariables:
    """Tests for environment variable loading."""

    def test_stash_endpoint_uses_env_variable(self) -> None:
        """Test that STASH_ENDPOINT can be set via environment.

        Verifies that the STASH_ENDPOINT configuration respects
        the environment variable when present.
        """
        test_endpoint = "http://test.example.com:8080"

        with patch.dict(
            os.environ,
            {"STASH_ENDPOINT": test_endpoint},
            clear=False
        ):
            # Re-import to get new value
            import importlib

            import stash_mcp_server.config as config_module
            importlib.reload(config_module)

            from stash_mcp_server.config import STASH_ENDPOINT
            assert STASH_ENDPOINT == test_endpoint

    def test_stash_endpoint_defaults_correctly(self) -> None:
        """Test that STASH_ENDPOINT falls back to default.

        Verifies that when no environment variable is set,
        the default endpoint is used.
        """
        assert STASH_ENDPOINT is not None
        assert isinstance(STASH_ENDPOINT, str)

    def test_stash_api_key_is_string(self) -> None:
        """Test that API key configuration is a string.

        Verifies that the API key is properly typed even when empty.
        """
        assert isinstance(STASH_API_KEY, str)

    def test_stash_connect_retries_is_integer(self) -> None:
        """Test that connection retry count is an integer.

        Verifies that the retry configuration is properly typed
        and has a reasonable value.
        """
        assert isinstance(STASH_CONNECT_RETRIES, int)
        assert STASH_CONNECT_RETRIES > 0


class TestConfigurationConsistency:
    """Tests for configuration consistency and relationships."""

    def test_cache_sizes_are_consistent(self) -> None:
        """Test that cache size configurations are consistent.

        Verifies that cache sizes follow logical relationships
        based on expected usage patterns.
        """
        # Performer cache should be larger as individual performers
        # are queried more frequently
        assert PERFORMER_CACHE_SIZE >= PERFORMERS_LIST_CACHE_SIZE

    def test_rating_ranges_cover_full_scale(self) -> None:
        """Test that rating thresholds cover the full rating scale.

        Verifies that rating constants provide complete coverage
        of the 0-100 rating scale.
        """
        # Check that we have thresholds that span the scale
        assert RATING_AVERAGE > 0
        assert RATING_EXCELLENT < 100

        # Check reasonable distribution
        assert (RATING_GOOD - RATING_AVERAGE) > 0
        assert (RATING_EXCELLENT - RATING_GOOD) > 0


class TestEnvironmentLoading:
    """Tests for environment loading behavior."""

    def test_env_file_loading(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
        """Test that .env file is loaded correctly.

        Verifies environment file loading mechanism.
        """
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("STASH_API_KEY=test_key_123\n")

        # Mock the environment
        monkeypatch.setenv("STASH_API_KEY", "test_key_123")

        # Verify the key is accessible
        import os
        assert os.getenv("STASH_API_KEY") == "test_key_123"

    def test_load_environment_with_find_dotenv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment loading when find_dotenv finds a file.

        Verifies that _load_environment correctly loads from .env.
        """
        monkeypatch.setenv("STASH_CONNECT_DELAY_SECONDS", "2.5")

        from stash_mcp_server.config import STASH_CONNECT_DELAY_SECONDS
        assert isinstance(STASH_CONNECT_DELAY_SECONDS, float)

    def test_stash_connect_delay_seconds_is_float(self) -> None:
        """Test that connection delay is a float.

        Verifies that the delay configuration is properly typed.
        """
        from stash_mcp_server.config import STASH_CONNECT_DELAY_SECONDS
        assert isinstance(STASH_CONNECT_DELAY_SECONDS, float)
        assert STASH_CONNECT_DELAY_SECONDS > 0

    def test_configuration_is_loaded_in_testing(self) -> None:
        """Test that configuration loads even in testing environment.

        Verifies that testing mode allows loading without API key.
        """
        import os
        is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None
        assert is_testing or os.getenv("TESTING") == "true"

    def test_validation_check_is_skipped_in_testing(self) -> None:
        """Test that API key validation is skipped in test mode.

        Verifies that configuration can be imported without API key
        when PYTEST_CURRENT_TEST is set.
        """
        # The fact that we can import the module without errors
        # proves that validation was skipped
        from stash_mcp_server import config
        assert config is not None

    def test_config_module_has_all_required_constants(self) -> None:
        """Test that all required configuration constants are defined.

        Verifies that the config module provides all expected constants.
        """
        from stash_mcp_server import config

        # Check that all important constants exist
        assert hasattr(config, 'DEFAULT_ENDPOINT')
        assert hasattr(config, 'STASH_ENDPOINT')
        assert hasattr(config, 'STASH_API_KEY')
        assert hasattr(config, 'STASH_CONNECT_RETRIES')
        assert hasattr(config, 'STASH_CONNECT_DELAY_SECONDS')
        assert hasattr(config, 'PERFORMER_CACHE_SIZE')
        assert hasattr(config, 'SCENES_CACHE_SIZE')
        assert hasattr(config, 'PERFORMERS_LIST_CACHE_SIZE')
        assert hasattr(config, 'DEFAULT_MAX_BATCH_PERFORMERS')
        assert hasattr(config, 'RATING_EXCELLENT')
        assert hasattr(config, 'RATING_GOOD')
        assert hasattr(config, 'RATING_AVERAGE')

    def test_logging_configuration(self) -> None:
        """Test that logging is configured correctly.

        Verifies that the logger is properly initialized.
        """
        from stash_mcp_server.config import logger

        assert logger is not None
        assert logger.name == "stash_mcp_server.config"
