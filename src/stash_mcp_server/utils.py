"""Utility functions for Stash MCP Server.

This module contains helper functions for filter construction,
error handling, and common operations.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from .connection import get_stash_interface

logger: logging.Logger = logging.getLogger(__name__)


def add_filter(
    filters: Dict[str, Any],
    field_name: str,
    value: Any,
    modifier: str = "EQUALS",
    value2: Optional[Any] = None
) -> None:
    """Add a filter to the filters dictionary.

    Parameters
    ----------
    filters : Dict[str, Any]
        Dictionary to add the filter to.
    field_name : str
        Name of the field to filter.
    value : Any
        Value to filter by.
    modifier : str, default "EQUALS"
        Filter modifier (EQUALS, GREATER_THAN, LESS_THAN, BETWEEN, etc.).
    value2 : Optional[Any], default None
        Second value for BETWEEN/NOT_BETWEEN modifiers.
    """
    if value is not None:
        filter_dict = {"value": value, "modifier": modifier}
        if value2 is not None and modifier in ["BETWEEN", "NOT_BETWEEN"]:
            filter_dict["value2"] = value2
        filters[field_name] = filter_dict


def build_tag_filter(
    include_tags: Optional[str] = None,
    exclude_tags: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Build tag filter for Stash queries.

    Parameters
    ----------
    include_tags : Optional[str], default None
        Comma-separated list of tag names to include.
    exclude_tags : Optional[str], default None
        Comma-separated list of tag names to exclude.

    Returns
    -------
    Optional[Dict[str, Any]]
        Tag filter dictionary or None if no tags specified.

    Notes
    -----
    Include and exclude cannot be used together. Include takes precedence.
    """
    if not include_tags and not exclude_tags:
        return None

    stash = get_stash_interface()

    if include_tags:
        if exclude_tags:
            logger.warning(
                "Cannot combine include and exclude tag filters. "
                "Include filter will take precedence."
            )
        tag_list = [tag.strip() for tag in include_tags.split(",")]
        tag_ids = [stash.find_tag(tag).get("id") for tag in tag_list]
        return {"modifier": "INCLUDES", "value": tag_ids}

    if exclude_tags:
        tag_list = [tag.strip() for tag in exclude_tags.split(",")]
        tag_ids = [stash.find_tag(tag).get("id") for tag in tag_list]
        return {"modifier": "EXCLUDES", "value": tag_ids}

    return None


def build_rating_filter(
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Build rating filter for Stash queries.

    Parameters
    ----------
    min_rating : Optional[int], default None
        Minimum rating value (inclusive).
    max_rating : Optional[int], default None
        Maximum rating value (inclusive).

    Returns
    -------
    Optional[Dict[str, Any]]
        Rating filter dictionary or None if no ratings specified.
    """
    if min_rating is None and max_rating is None:
        return None

    if min_rating is not None and max_rating is not None:
        return {
            "modifier": "BETWEEN",
            "value": min_rating,
            "value2": max_rating
        }

    if min_rating is not None:
        return {
            "modifier": "GREATER_THAN",
            "value": min_rating - 1  # Adjust for inclusive behavior
        }

    if max_rating is not None:
        return {
            "modifier": "LESS_THAN",
            "value": max_rating + 1  # Adjust for inclusive behavior
        }

    return None


def calculate_average_rating(scenes: List[Dict[str, Any]]) -> float:
    """Calculate average rating from a list of scenes.

    Parameters
    ----------
    scenes : List[Dict[str, Any]]
        List of scene dictionaries.

    Returns
    -------
    float
        Average rating or 0.0 if no valid ratings found.
    """
    ratings = [
        s.get("rating100", 0) for s in scenes
        if s.get("rating100") is not None
    ]
    return sum(ratings) / len(ratings) if ratings else 0.0


def count_scenes_by_rating(
    scenes: List[Dict[str, Any]],
    min_rating: int,
    max_rating: Optional[int] = None
) -> int:
    """Count scenes within a rating range.

    Parameters
    ----------
    scenes : List[Dict[str, Any]]
        List of scene dictionaries.
    min_rating : int
        Minimum rating (exclusive if max_rating is None).
    max_rating : Optional[int], default None
        Maximum rating (inclusive). If None, counts scenes > min_rating.

    Returns
    -------
    int
        Number of scenes matching the rating criteria.
    """
    count = 0
    for scene in scenes:
        rating = scene.get("rating100")
        if rating is not None:
            if max_rating is None:
                if rating > min_rating:
                    count += 1
            elif min_rating == 0:
                if rating < max_rating:
                    count += 1
            else:
                if min_rating <= rating <= max_rating:
                    count += 1
    return count


def extract_tag_frequency(scenes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Extract tag frequency from a list of scenes.

    Parameters
    ----------
    scenes : List[Dict[str, Any]]
        List of scene dictionaries.

    Returns
    -------
    Dict[str, int]
        Dictionary mapping tag names to their occurrence count.
    """
    tag_frequency: Dict[str, int] = {}

    for scene in scenes:
        if scene.get("tags"):
            for tag in scene["tags"]:
                tag_name = tag.get("name", "")
                tag_frequency[tag_name] = tag_frequency.get(tag_name, 0) + 1

    return tag_frequency


def handle_stash_errors(
    default_return: Any = None
) -> Callable[..., Any]:
    """Decorator to handle common Stash API errors.

    Parameters
    ----------
    default_return : Any, default None
        Value to return if an error occurs.

    Returns
    -------
    Callable[..., Any]
        Decorator function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "Error in %s: %s",
                    func.__name__,
                    str(e)
                )
                return default_return
        return wrapper
    return decorator


def format_filter_description(
    organized_only: bool = False,
    include_tags: Optional[str] = None,
    exclude_tags: Optional[str] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    **kwargs: Any
) -> str:
    """Format a human-readable description of active filters.

    Parameters
    ----------
    organized_only : bool, default False
        Whether filtering for organized content only.
    include_tags : Optional[str], default None
        Comma-separated tag names to include.
    exclude_tags : Optional[str], default None
        Comma-separated tag names to exclude.
    min_rating : Optional[int], default None
        Minimum rating filter.
    max_rating : Optional[int], default None
        Maximum rating filter.
    **kwargs : Any
        Additional filter parameters.

    Returns
    -------
    str
        Human-readable filter description.
    """
    parts = []

    if organized_only:
        parts.append("organized only")

    if include_tags:
        parts.append(f"including tags: {include_tags}")

    if exclude_tags:
        parts.append(f"excluding tags: {exclude_tags}")

    if min_rating is not None:
        parts.append(f"min rating: {min_rating}")

    if max_rating is not None:
        parts.append(f"max rating: {max_rating}")

    # Add any additional filters
    for key, value in kwargs.items():
        if value is not None and key not in ['self', 'filters']:
            parts.append(f"{key}: {value}")

    return f" ({', '.join(parts)})" if parts else ""
