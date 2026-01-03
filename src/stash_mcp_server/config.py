"""Configuration module for Stash MCP Server.

This module centralizes all configuration settings, environment variables,
and application constants.
"""

import logging
import os
from typing import Final

from dotenv import find_dotenv, load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger: logging.Logger = logging.getLogger(__name__)


def _load_environment() -> None:
    """Load environment variables from .env file.

    Prefers a .env in the current working directory. If not found,
    falls back to the .env bundled next to the package file.
    """
    dot_env_path = find_dotenv(usecwd=True)
    if dot_env_path:
        load_dotenv(dot_env_path)
        logger.info("Loaded environment from: %s", dot_env_path)
    else:
        # Fallback: .env next to this file's parent directory
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.env'
        )
        load_dotenv(env_path)
        logger.info("Loaded environment from fallback: %s", env_path)


# Load environment variables
_load_environment()


# Stash Connection Configuration
DEFAULT_ENDPOINT: Final[str] = "http://localhost:9999"
STASH_ENDPOINT: Final[str] = os.getenv("STASH_ENDPOINT", DEFAULT_ENDPOINT)
STASH_API_KEY: Final[str] = os.getenv("STASH_API_KEY", "")
STASH_CONNECT_RETRIES: Final[int] = int(
    os.getenv("STASH_CONNECT_RETRIES", "3")
)
STASH_CONNECT_DELAY_SECONDS: Final[float] = float(
    os.getenv("STASH_CONNECT_DELAY_SECONDS", "1.5")
)

# Filtering Configuration
FAVORITES_ONLY: Final[bool] = os.getenv("FAVORITES", "true").lower() == "true"

# Cache Configuration
PERFORMER_CACHE_SIZE: Final[int] = 256
SCENES_CACHE_SIZE: Final[int] = 64
PERFORMERS_LIST_CACHE_SIZE: Final[int] = 64

# Batch Processing Configuration
DEFAULT_MAX_BATCH_PERFORMERS: Final[int] = 10

# Rating Thresholds
RATING_EXCELLENT: Final[int] = 90
RATING_GOOD: Final[int] = 70
RATING_AVERAGE: Final[int] = 50

# Validation (skip in test environments)
_is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("TESTING") == "true"

if not STASH_API_KEY and not _is_testing:
    raise ValueError(
        "STASH_API_KEY is not set in the .env file. "
        "Please add STASH_API_KEY to your .env file."
    )

if not _is_testing:
    logger.info("Configuration loaded successfully")
    logger.info("Stash endpoint: %s", STASH_ENDPOINT)
