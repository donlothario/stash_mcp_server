

import os
import time
import logging
from functools import lru_cache
from typing import Dict, List, Optional, Any

from stashapi.stashapp import StashInterface
from fastmcp import FastMCP, Context
from dotenv import load_dotenv
from urllib.parse import urlparse


# Load environment variables
load_dotenv()

#############################################
# Configuration
#############################################
DEFAULT_ENDPOINT = "http://localhost:9999"
STASH_ENDPOINT: str = os.getenv("STASH_ENDPOINT", DEFAULT_ENDPOINT)
STASH_API_KEY: str = os.getenv("STASH_API_KEY", "")
STASH_CONNECT_RETRIES: int = int(os.getenv("STASH_CONNECT_RETRIES", "3"))
STASH_CONNECT_DELAY_SECONDS: float = float(
    os.getenv("STASH_CONNECT_DELAY_SECONDS", "1.5")
)

if not STASH_API_KEY:
    raise ValueError(
        "STASH_API_KEY is not set in the .env file. Add it to .env."
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Stash interface reference (initialized lazily / with retries)
stash: Optional[StashInterface] = None


def connect_to_stash() -> Optional[StashInterface]:
    """Attempt to connect to the Stash instance with retries.

    Returns
    -------
    Optional[StashInterface]
        Connected interface or None if connection failed.
    """
    global stash
    if stash is not None:
        return stash
    last_err: Optional[Exception] = None
    for attempt in range(1, STASH_CONNECT_RETRIES + 1):
        try:
            logger.info(
                "Connecting to Stash (attempt %d/%d) at %s...",
                attempt,
                STASH_CONNECT_RETRIES,
                STASH_ENDPOINT,
            )
            parsed = urlparse(STASH_ENDPOINT)
            stash_local = StashInterface({
                "scheme": parsed.scheme or "http",
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 9999,
                "logger": None,
                "apikey": STASH_API_KEY,
            })
            stash = stash_local
            logger.info("Connected to Stash at %s", STASH_ENDPOINT)
            return stash
        except ImportError:
            logger.error(
                "stashapi library not installed. Install with: "
                "pip install stashapi"
            )
            return None
        except Exception as err:  # broad catch acceptable for retry loop
            last_err = err
            logger.warning("Connection attempt %d failed: %s", attempt, err)
            if attempt < STASH_CONNECT_RETRIES:
                time.sleep(STASH_CONNECT_DELAY_SECONDS)
    logger.error("Failed to connect to Stash after %d attempts: %s",
                 STASH_CONNECT_RETRIES, last_err)
    return None


def _ensure_stash() -> StashInterface:
    """Ensure stash interface is available or raise runtime error."""
    if connect_to_stash() is None:
        raise RuntimeError("Stash connection not available.")
    assert stash is not None  # for type checkers
    return stash


#############################################
# GraphQL Fragment Definitions (centralized)
#############################################
FRAGMENTS: Dict[str, str] = {
    "performer": (
        """
        id
        name
        country
        details
        ethnicity
        eye_color
        hair_color
        height_cm
        measurements
        piercings
        tattoos
        tags { name }
        weight
        """.strip()
    ),
    "scene": (
        """
        id
        title
        details
        rating100
        performers { name rating100 tags { name } }
        tags { name }
        """.strip()
    ),
}

mcp = FastMCP(name="Stash MCP")


@lru_cache(maxsize=256)
def _cached_get_performer_info(performer_name: str) -> Dict:
    """Internal cached implementation for performer info.

    This function is separated from the MCP tool wrapper because applying
    `@lru_cache` directly to a function also decorated with `@mcp.tool()` wraps
    it in a functools cache wrapper object that Pydantic (used internally by
    fastmcp) cannot derive a schema from, causing
    `PydanticSchemaGenerationError`. By splitting the concerns, we preserve
    caching without exposing the wrapper to fastmcp.
    """
    try:
        si = _ensure_stash()
        performer = si.find_performer(
            performer_name, fragment=FRAGMENTS["performer"]
        )
        if performer:
            logger.info(
                "Found performer '%s' (id=%s)",
                performer.get("name"),
                performer.get("id"),
            )
        else:
            logger.info("Performer '%s' not found", performer_name)
        return performer or {}
    except Exception as e:  # broad: safe fall back
        logger.error(
            "Error _cached_get_performer_info('%s'): %s", performer_name, e
        )
        return {}


@mcp.tool(
    name="get_performer_info",
    description="Return detailed information for a single performer",
    annotations={
        "title": "Get Performer Information",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def get_performer_info(performer_name: str) -> Dict:
    """Return detailed information for a single performer (cached).

    Parameters
    ----------
    performer_name : str
        Exact name of the performer.

    Returns
    -------
    Dict
        Performer metadata (empty dict if not found / error).
    """
    return _cached_get_performer_info(performer_name)


@lru_cache(maxsize=32)
def _cached_get_all_scenes(
    organized_only: bool = True,
    exclude_tags: Optional[str] = None,
    include_tags: Optional[str] = None,
    min_rating: Optional[int] = 0,
    max_rating: Optional[int] = 100
) -> List[Dict]:
    """Internal cached implementation for getting all scenes with filters.

    Parameters
    ----------
    organized_only : bool, default True
        If True, only return organized scenes.
    exclude_tags : Optional[str], default None
        Comma-separated list of tag names to exclude from results.
    include_tags : Optional[str], default None
        Comma-separated list of tag names that must be present.
    min_rating : Optional[int], default None
        Minimum rating (0-100) for scenes.
    max_rating : Optional[int], default None
        Maximum rating (0-100) for scenes.

    Returns
    -------
    List[Dict]
        List of scene objects matching the filters.
    """
    try:
        si = _ensure_stash()
        filters: Dict = {}

        if organized_only:
            filters["organized"] = True

        # Add tag count filter to ensure scenes have tags
        filters["tag_count"] = {"value": 0, "modifier": "GREATER_THAN"}

        # Handle tag exclusions
        if exclude_tags:
            exclude_tag_list = [tag.strip() for tag in exclude_tags.split(",")]
            # For multiple excludes, we need to exclude each tag
            for tag_name in exclude_tag_list:
                tag_id = si.find_tag(tag_name).get("id")
                if "tags" not in filters:
                    filters["tags"] = {
                        "modifier": "EXCLUDES",
                        "value": [tag_id]
                    }
                else:
                    # If we already have tags filter, handle multiple excludes
                    if isinstance(filters["tags"]["value"], list):
                        filters["tags"]["value"].append(tag_id)
                    else:
                        filters["tags"]["value"] = [
                            filters["tags"]["value"], tag_id
                        ]

        # Handle tag inclusions
        if include_tags:
            include_tag_list = [tag.strip() for tag in include_tags.split(",")]
            # For includes, all tags should be present
            if "tags" in filters:
                logger.warning(
                    "Cannot combine include and exclude tag filters, "
                    "include filter will take precedence"
                )
            filters["tags"] = {
                "modifier": "INCLUDES",
                "value": [si.find_tag(tag).get("id") for tag
                            in include_tag_list]
            }

        # Handle rating filters
        if min_rating is not None or max_rating is not None:
            if min_rating is not None and max_rating is not None:
                filters["rating100"] = {
                    "modifier": "BETWEEN",
                    "value": min_rating,
                    "value2": max_rating
                }
            elif min_rating is not None:
                filters["rating100"] = {
                    "modifier": "GREATER_THAN",
                    "value": min_rating - 1  # Adjust for inclusive behavior
                }
            elif max_rating is not None:
                filters["rating100"] = {
                    "modifier": "LESS_THAN",
                    "value": max_rating + 1  # Adjust for inclusive behavior
                }

        # Define fragment for scene data
        fragment_query = FRAGMENTS["scene"]

        scenes = si.find_scenes(f=filters, fragment=fragment_query)

        # Create filter description for logging
        filter_desc_parts = []
        if organized_only:
            filter_desc_parts.append("organized only")
        if exclude_tags:
            filter_desc_parts.append(f"excluding tags: {exclude_tags}")
        if include_tags:
            filter_desc_parts.append(f"including tags: {include_tags}")
        if min_rating is not None:
            filter_desc_parts.append(f"min rating: {min_rating}")
        if max_rating is not None:
            filter_desc_parts.append(f"max rating: {max_rating}")

        filter_desc = (
            f" ({', '.join(filter_desc_parts)})"
            if filter_desc_parts else ""
        )
        logger.info("Found %d scenes%s", len(scenes), filter_desc)

        return scenes

    except Exception as e:
        logger.error("Error in _cached_get_all_scenes: %s", e)
        return []


@lru_cache(maxsize=64)
def _cached_get_all_performers(
    favorites_only: bool = True,
    country: Optional[str] = None,
    country_modifier: str = "EQUALS",
    ethnicity: Optional[str] = None,
    ethnicity_modifier: str = "EQUALS",
    eye_color: Optional[str] = None,
    eye_color_modifier: str = "EQUALS",
    hair_color: Optional[str] = None,
    hair_color_modifier: str = "EQUALS",
    height_cm: Optional[int] = None,
    height_cm_modifier: str = "EQUALS",
    height_cm_value2: Optional[int] = None,
    measurements: Optional[str] = None,
    measurements_modifier: str = "EQUALS",
    piercings: Optional[str] = None,
    piercings_modifier: str = "INCLUDES",
    tattoos: Optional[str] = None,
    tattoos_modifier: str = "INCLUDES",
    weight: Optional[int] = None,
    weight_modifier: str = "EQUALS",
    weight_value2: Optional[int] = None,
) -> List[Dict]:
    """Internal cached implementation for listing performers with filters.

    Parameters
    ----------
    favorites_only : bool, default True
        If True limit to favorite performers.
    country : Optional[str], default None
        Filter by country.
    country_modifier : str, default "EQUALS"
        Modifier for country filter (EQUALS, NOT_EQUALS, etc.).
    ethnicity : Optional[str], default None
        Filter by ethnicity.
    ethnicity_modifier : str, default "EQUALS"
        Modifier for ethnicity filter.
    eye_color : Optional[str], default None
        Filter by eye color.
    eye_color_modifier : str, default "EQUALS"
        Modifier for eye color filter.
    hair_color : Optional[str], default None
        Filter by hair color.
    hair_color_modifier : str, default "EQUALS"
        Modifier for hair color filter.
    height_cm : Optional[int], default None
        Filter by height in centimeters.
    height_cm_modifier : str, default "EQUALS"
        Modifier for height filter (EQUALS, GREATER_THAN, LESS_THAN, BETWEEN).
    height_cm_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN height filters.
    measurements : Optional[str], default None
        Filter by measurements.
    measurements_modifier : str, default "EQUALS"
        Modifier for measurements filter.
    piercings : Optional[str], default None
        Filter by piercings.
    piercings_modifier : str, default "EQUALS"
        Modifier for piercings filter.
    tattoos : Optional[str], default None
        Filter by tattoos.
    tattoos_modifier : str, default "EQUALS"
        Modifier for tattoos filter.
    weight : Optional[int], default None
        Filter by weight.
    weight_modifier : str, default "EQUALS"
        Modifier for weight filter (EQUALS, GREATER_THAN, LESS_THAN, BETWEEN).
    weight_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN weight filters.
    """
    try:
        si = _ensure_stash()
        filters: Dict = {}

        if favorites_only:
            filters["filter_favorites"] = True

        # Helper function to add filter with proper structure
        def add_filter(field_name: str, value: Any, modifier: str,
                       value2: Any = None):
            if value is not None:
                filter_dict = {"value": value, "modifier": modifier}
                if (value2 is not None and
                        modifier in ["BETWEEN", "NOT_BETWEEN"]):
                    filter_dict["value2"] = value2
                filters[field_name] = filter_dict

        # Add all the filters
        add_filter("country", country, country_modifier)
        add_filter("ethnicity", ethnicity, ethnicity_modifier)
        add_filter("eye_color", eye_color, eye_color_modifier)
        add_filter("hair_color", hair_color, hair_color_modifier)
        add_filter("height_cm", height_cm, height_cm_modifier,
                   height_cm_value2)
        add_filter("measurements", measurements, measurements_modifier)
        add_filter("piercings", piercings, piercings_modifier)
        add_filter("tattoos", tattoos, tattoos_modifier)
        add_filter("weight", weight, weight_modifier, weight_value2)

        performers = si.find_performers(
            f=filters,
            fragment=FRAGMENTS["performer"],
        )

        # Create filter description for logging
        active_filters = []
        if favorites_only:
            active_filters.append("favorites")
        fields = ["country", "ethnicity", "eye_color", "hair_color",
                  "height_cm", "measurements", "piercings", "tattoos",
                  "weight"]
        for field in fields:
            if locals()[field] is not None:
                active_filters.append(field)

        filter_desc = ""
        if active_filters:
            filter_desc = f" (filters: {', '.join(active_filters)})"

        logger.info(
            "Found %d performer(s)%s",
            len(performers),
            filter_desc,
        )
        return performers
    except Exception as e:
        logger.error(
            "Error _cached_get_all_performers: %s", e
        )
        return []


@mcp.tool(
    name="get_all_performers",
    description="Return a list of performers with advanced filtering options",
    annotations={
        "title": "Get All Performers",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def get_all_performers(
    favorites_only: bool = True,
    country: Optional[str] = None,
    country_modifier: str = "EQUALS",
    ethnicity: Optional[str] = None,
    ethnicity_modifier: str = "EQUALS",
    eye_color: Optional[str] = None,
    eye_color_modifier: str = "EQUALS",
    hair_color: Optional[str] = None,
    hair_color_modifier: str = "EQUALS",
    height_cm: Optional[int] = None,
    height_cm_modifier: str = "EQUALS",
    height_cm_value2: Optional[int] = None,
    measurements: Optional[str] = None,
    measurements_modifier: str = "EQUALS",
    piercings: Optional[str] = None,
    tattoos: Optional[str] = None,
    weight: Optional[int] = None,
    weight_modifier: str = "EQUALS",
    weight_value2: Optional[int] = None,
) -> List[Dict]:
    """Return a list of performers with advanced filtering options.

    Parameters
    ----------
    favorites_only : bool, default True
        If True limit to favorite performers.
    country : Optional[str], default None
        Filter by country.
    country_modifier : str, default "EQUALS"
        Modifier for country filter (EQUALS, NOT_EQUALS).
    ethnicity : Optional[str], default None
        Filter by ethnicity.
    ethnicity_modifier : str, default "EQUALS"
        Modifier for ethnicity filter (EQUALS, NOT_EQUALS).
    eye_color : Optional[str], default None
        Filter by eye color.
    eye_color_modifier : str, default "EQUALS"
        Modifier for eye color filter (EQUALS, NOT_EQUALS).
    hair_color : Optional[str], default None
        Filter by hair color.
    hair_color_modifier : str, default "EQUALS"
        Modifier for hair color filter (EQUALS, NOT_EQUALS).
    height_cm : Optional[int], default None
        Filter by height in centimeters.
    height_cm_modifier : str, default "EQUALS"
        Modifier for height filter (EQUALS, GREATER_THAN, LESS_THAN, BETWEEN).
    height_cm_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN height filters.
    measurements : Optional[str], default None
        Filter by measurements.
    measurements_modifier : str, default "EQUALS"
        Modifier for measurements filter (EQUALS, NOT_EQUALS).
    piercings : Optional[str], default None
        Filter by piercings.
    tattoos : Optional[str], default None
        Filter by tattoos.
    weight : Optional[int], default None
        Filter by weight.
    weight_modifier : str, default "EQUALS"
        Modifier for weight filter (EQUALS, GREATER_THAN, LESS_THAN, BETWEEN).
    weight_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN weight filters.

    Returns
    -------
    List[Dict]
        Performer objects (empty list on error).
    """
    return _cached_get_all_performers(
        favorites_only=favorites_only,
        country=country,
        country_modifier=country_modifier,
        ethnicity=ethnicity,
        ethnicity_modifier=ethnicity_modifier,
        eye_color=eye_color,
        eye_color_modifier=eye_color_modifier,
        hair_color=hair_color,
        hair_color_modifier=hair_color_modifier,
        height_cm=height_cm,
        height_cm_modifier=height_cm_modifier,
        height_cm_value2=height_cm_value2,
        measurements=measurements,
        measurements_modifier=measurements_modifier,
        piercings=piercings,
        tattoos=tattoos,
        weight=weight,
        weight_modifier=weight_modifier,
        weight_value2=weight_value2,
    )


@mcp.tool(
    name="get_all_scenes",
    description="Return all scenes from Stash with advanced filtering options",
    annotations={
        "title": "Get All Scenes",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def get_all_scenes(
    organized_only: bool = True,
    exclude_tags: Optional[str] = None,
    include_tags: Optional[str] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None
) -> List[Dict]:
    """Return all scenes from Stash with advanced filtering options.

    Parameters
    ----------
    organized_only : bool, default True
        If True, only return organized scenes.
    exclude_tags : Optional[str], default None
        Comma-separated list of tag names to exclude from results.
        Example: "Tag1,Tag2,Tag3"
    include_tags : Optional[str], default None
        Comma-separated list of tag names that must be present in scenes.
        Example: "Required1,Required2". Cannot be combined with exclude_tags.
    min_rating : Optional[int], default None
        Minimum rating (0-100) for scenes to include.
    max_rating : Optional[int], default None
        Maximum rating (0-100) for scenes to include.

    Returns
    -------
    List[Dict]
        Scene objects matching the specified filters. Empty list on error.
        Each scene contains: id, title, details, rating100, performers, tags.

    Examples
    --------
    - get_all_scenes() - All organized scenes
    - get_all_scenes(exclude_tags="Compilation,Behind The Scenes")
      - Exclude compilation and BTS scenes
    - get_all_scenes(include_tags="Anal,Hardcore", min_rating=80)
      - Only anal hardcore scenes rated 80+
    - get_all_scenes(organized_only=False, max_rating=50)
      - Include unorganized scenes with rating ≤50

    Notes
    -----
    - exclude_tags and include_tags cannot be used together
    - Tag names are case-sensitive and should match exactly
    - Rating filters are inclusive (min_rating=80 includes rating=80)
    """
    return _cached_get_all_scenes(
        organized_only=organized_only,
        exclude_tags=exclude_tags,
        include_tags=include_tags,
        min_rating=min_rating,
        max_rating=max_rating
    )


@mcp.tool(
    name="get_all_scenes_from_performer",
    description="Return all scenes for a given performer",
    annotations={
        "title": "Get All Scenes from Performer",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def get_all_scenes_from_performer(
    performer_name: str,
    organized_only: bool = True,
) -> List[Dict]:
    """Return all scenes for a given performer.

    Parameters
    ----------
    performer_name : str
        Exact name for which scenes are searched (EQUALS match).
    organized_only : bool, default True
        If True restrict to organized scenes.

    Returns
    -------
    List[Dict]
        Scene objects (empty list on error).
    """
    try:
        si = _ensure_stash()
        filters: Dict = {
            "performers_filter": {
                "name": {"value": performer_name, "modifier": "EQUALS"}
            }
        }
        if organized_only:
            filters["organized"] = True
        scenes = si.find_scenes(
            f=filters,
            fragment=FRAGMENTS["scene"],
        )
        logger.info(
            "Found %d scene(s) for '%s'%s", len(scenes), performer_name,
            " (organized only)" if organized_only else ""
        )
        return scenes
    except Exception as e:
        logger.error(
            "Error get_all_scenes_from_performer('%s'): %s", performer_name, e
        )
        return []


@mcp.tool(
    name="health_check",
    description="Return basic health/connectivity information for the MCP "
                "server",
    annotations={
        "title": "Health Check",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def health_check() -> Dict:
    """Return basic health / connectivity information for the MCP server.

    Returns
    -------
    Dict
        Diagnostic data: connection status, host, port, cached counts.
    """
    connected = connect_to_stash() is not None
    # Access internal cache wrappers for accurate statistics
    performer_cache_info = (
        _cached_get_performer_info.cache_info()  # type: ignore
    )
    all_perf_cache_info = (
        _cached_get_all_performers.cache_info()  # type: ignore
    )
    all_scenes_cache_info = (
        _cached_get_all_scenes.cache_info()  # type: ignore
    )
    return {
        "connected": connected,
        "endpoint": STASH_ENDPOINT,
        "performer_cache": {
            "hits": performer_cache_info.hits,
            "misses": performer_cache_info.misses,
            "currsize": performer_cache_info.currsize,
            "maxsize": performer_cache_info.maxsize,
        },
        "all_performers_cache": {
            "hits": all_perf_cache_info.hits,
            "misses": all_perf_cache_info.misses,
            "currsize": all_perf_cache_info.currsize,
            "maxsize": all_perf_cache_info.maxsize,
        },
        "all_scenes_cache": {
            "hits": all_scenes_cache_info.hits,
            "misses": all_scenes_cache_info.misses,
            "currsize": all_scenes_cache_info.currsize,
            "maxsize": all_scenes_cache_info.maxsize,
        },
    }

#############################################
# Tools with Enhanced Context Handling
#############################################


@mcp.tool(
    name="advanced_performer_analysis",
    description="Advanced performer analysis with progress reporting and "
                "contextual logging",
    annotations={
        "title": "Advanced Performer Analysis",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def advanced_performer_analysis(
    performer_name: str,
    ctx: Context,
    include_similar: bool = True,
    deep_scene_analysis: bool = False
) -> Dict:
    """Advanced performer analysis with progress reporting.

    Parameters
    ----------
    performer_name : str
        Name of the performer to analyze
    ctx : Context
        MCP context for logging and progress
    include_similar : bool, default True
        Whether to include similar performer analysis
    deep_scene_analysis : bool, default False
        Whether to perform deep analysis of all scenes

    Returns
    -------
    Dict
        Complete performer analysis
    """
    await ctx.info(f"Starting advanced analysis for: {performer_name}")
    await ctx.report_progress(0, 100)

    try:
        # Phase 1: Basic performer information
        await ctx.info("Getting basic performer information...")
        performer_info = _cached_get_performer_info(performer_name)
        if not performer_info:
            await ctx.error(f"Performer '{performer_name}' not found")
            return {"error": f"Performer '{performer_name}' not found"}

        await ctx.report_progress(20, 100)

        # Phase 2: Scene analysis
        await ctx.info("Analyzing performer scenes...")
        scenes = []
        try:
            si = _ensure_stash()
            filters = {
                "performers_filter": {
                    "name": {"value": performer_name, "modifier": "EQUALS"}
                }
            }
            scenes = si.find_scenes(f=filters, fragment=FRAGMENTS["scene"])
        except Exception as e:
            await ctx.warning(f"Error getting scenes: {e}")

        await ctx.report_progress(40, 100)

        # Statistical analysis of scenes
        scene_stats = {
            "total_scenes": len(scenes),
            "average_rating": 0,
            "top_rated_scenes": [],
            "all_tags": [],
            "tag_frequency": {}
        }

        if scenes:
            ratings = [s.get("rating100", 0)
                       for s in scenes if s.get("rating100") is not None]
            scene_stats["average_rating"] = sum(
                ratings) / len(ratings) if ratings else 0

            # Filter scenes with valid rating and > 80
            top_rated = []
            for s in scenes:
                rating = s.get("rating100")
                if rating is not None and rating > 80:
                    top_rated.append(s)

            scene_stats["top_rated_scenes"] = sorted(
                top_rated,
                key=lambda x: x.get("rating100", 0),
                reverse=True
            )[:5]

            # Tag analysis
            for scene in scenes:
                if scene.get("tags"):
                    for tag in scene["tags"]:
                        tag_name = tag.get("name", "")
                        scene_stats["all_tags"].append(tag_name)
                        tag_freq = scene_stats["tag_frequency"]
                        tag_freq[tag_name] = tag_freq.get(tag_name, 0) + 1

        await ctx.report_progress(60, 100)

        # Phase 3: Similar performers (if requested)
        similar_performers = []
        if include_similar:
            await ctx.info("Searching for similar performers...")
            try:
                # Search by similar physical characteristics
                filters = {}
                if performer_info.get("country"):
                    filters["country"] = performer_info["country"]
                if performer_info.get("ethnicity"):
                    filters["ethnicity"] = performer_info["ethnicity"]

                all_performers = _cached_get_all_performers(
                    favorites_only=False,
                    **filters
                )

                # Filter out current performer and take first 5
                similar_performers = [
                    p for p in all_performers
                    if p.get("name", "").lower() != performer_name.lower()
                ][:5]

            except Exception as e:
                await ctx.warning(f"Error searching similar performers: {e}")

        await ctx.report_progress(80, 100)

        # Phase 4: Deep scene analysis (if requested)
        detailed_scene_analysis = {}
        if deep_scene_analysis and scenes:
            await ctx.info("Performing deep scene analysis...")
            # Implement more detailed analysis here
            # For now, additional basic analysis

            def count_by_rating(min_rating, max_rating=None):
                """Helper to count scenes by rating."""
                count = 0
                for scene in scenes:
                    rating = scene.get("rating100")
                    if rating is not None:
                        if max_rating is None:
                            # For cases like "excellent" (> 90)
                            if rating > min_rating:
                                count += 1
                        elif min_rating == 0:
                            # For cases like "below_average" (< 50)
                            if rating < max_rating:
                                count += 1
                        else:
                            # For ranges like "good" (70-90)
                            if min_rating <= rating <= max_rating:
                                count += 1
                return count

            detailed_scene_analysis = {
                "scenes_by_rating": {
                    "excellent": count_by_rating(90),  # > 90
                    "good": count_by_rating(70, 90),   # 70-90
                    "average": count_by_rating(50, 69),  # 50-69
                    "below_average": count_by_rating(0, 50)  # < 50
                },
                "scenes_per_year": {},  # Could be implemented with data
                "most_common_tags": sorted(
                    scene_stats["tag_frequency"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }

        await ctx.report_progress(100, 100)
        await ctx.info(f"Analysis completed for {performer_name}")

        # Build final response
        result = {
            "performer_info": performer_info,
            "scene_statistics": scene_stats,
            "analysis_metadata": {
                "analysis_timestamp": time.time(),
                "total_processing_time": "< 1 minute",
                "include_similar": include_similar,
                "deep_analysis": deep_scene_analysis
            }
        }

        if include_similar:
            result["similar_performers"] = similar_performers

        if deep_scene_analysis:
            result["detailed_scene_analysis"] = detailed_scene_analysis

        return result

    except Exception as e:
        await ctx.error(f"Error during analysis: {e}")
        return {"error": f"Error during analysis: {e}"}


@mcp.tool(
    name="batch_performer_insights",
    description="Generates insights for multiple performers with detailed "
                "progress",
    annotations={
        "title": "Batch Performer Insights",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def batch_performer_insights(
    performer_names: List[str],
    ctx: Context,
    max_performers: int = 10
) -> Dict:
    """Generates insights for multiple performers with progress reporting.

    Parameters
    ----------
    performer_names : List[str]
        List of performer names to analyze
    ctx : Context
        MCP context for logging and progress
    max_performers : int, default 10
        Maximum number of performers to process

    Returns
    -------
    Dict
        Aggregated insights from all performers
    """
    await ctx.info(f"Starting batch analysis of {len(performer_names)} "
                   f"performers")

    # Limit number of performers for performance
    if len(performer_names) > max_performers:
        await ctx.warning(f"Limiting analysis to {max_performers} performers "
                          f"(from {len(performer_names)} requested)")
        performer_names = performer_names[:max_performers]

    total_performers = len(performer_names)
    processed_performers = []
    failed_performers = []

    for i, performer_name in enumerate(performer_names):
        progress = int((i / total_performers) * 100)
        await ctx.report_progress(progress, 100)
        await ctx.info(f"Processing performer {i+1}/{total_performers}: "
                       f"{performer_name}")

        try:
            performer_info = _cached_get_performer_info(performer_name)
            if performer_info:
                # Get basic scene count
                scenes = []
                try:
                    si = _ensure_stash()
                    filters = {
                        "performers_filter": {
                            "name": {"value": performer_name,
                                     "modifier": "EQUALS"}
                        }
                    }
                    scenes = si.find_scenes(
                        f=filters, fragment=FRAGMENTS["scene"])
                except Exception:
                    pass  # Continue without scenes if error

                # Calculate average rating only from scenes with rating
                valid_ratings = [
                    s.get("rating100", 0) for s in scenes
                    if s.get("rating100") is not None
                ]
                avg_rating = (
                    sum(valid_ratings) / len(valid_ratings)
                    if valid_ratings else 0
                )

                processed_performers.append({
                    "name": performer_name,
                    "info": performer_info,
                    "scene_count": len(scenes),
                    "average_rating": avg_rating
                })
            else:
                failed_performers.append(performer_name)

        except Exception as e:
            await ctx.warning(f"Error processing {performer_name}: {e}")
            failed_performers.append(performer_name)

    await ctx.report_progress(100, 100)
    await ctx.info(f"Analysis completed. Processed: "
                   f"{len(processed_performers)}, Failed: "
                   f"{len(failed_performers)}")

    # Generate aggregated insights
    if processed_performers:
        countries = [p["info"].get("country") for p in processed_performers
                     if p["info"].get("country")]
        ethnicities = [p["info"].get("ethnicity") for p in processed_performers
                       if p["info"].get("ethnicity")]

        insights = {
            "summary": {
                "total_processed": len(processed_performers),
                "total_failed": len(failed_performers),
                "average_scenes_per_performer": (
                    sum(p["scene_count"] for p in processed_performers) /
                    len(processed_performers)
                ),
                "average_rating_across_all": (
                    sum(p["average_rating"] for p in processed_performers) /
                    len(processed_performers)
                )
            },
            "demographics": {
                "countries": list(set(countries)),
                "country_distribution": {
                    country: countries.count(country)
                    for country in set(countries)
                },
                "ethnicities": list(set(ethnicities)),
                "ethnicity_distribution": {
                    ethnicity: ethnicities.count(ethnicity)
                    for ethnicity in set(ethnicities)
                }
            },
            "performers": processed_performers,
            "failed_performers": failed_performers
        }
    else:
        insights = {
            "summary": {
                "total_processed": 0,
                "total_failed": len(failed_performers)
            },
            "failed_performers": failed_performers
        }

    return insights


#############################################
# Analysis Prompts
#############################################

@mcp.prompt(
    name="analyze-performer",
    description="Generates a complete analysis of a performer including "
                "statistics, popular scenes, frequent tags and similar "
                "recommendations"
)
def analyze_performer_prompt(performer_name: str) -> str:
    """Prompt for complete performer analysis.

    Parameters
    ----------
    performer_name : str
        Name of the performer to analyze

    Returns
    -------
    str
        Formatted prompt for performer analysis
    """
    return f"""Completely analyze the performer '{performer_name}' using the \
available Stash MCP server tools.

REQUIRED ANALYSIS:

1. **Basic Performer Information:**
   - Use `get_performer_info('{performer_name}')` to get demographic data
   - Include: country, ethnicity, physical characteristics, measurements, \
tattoos, piercings

2. **Scene Analysis:**
   - Use `get_all_scenes_from_performer('{performer_name}')` to get all \
their scenes
   - Calculate statistics: total number of scenes, average rating, date range
   - Identify top-rated scenes (rating > 80)

3. **Tag Analysis:**
   - Extract all unique tags from their scenes
   - Identify most frequent tags (top 10)
   - Categorize tags by type (genre, position, characteristics, etc.)

4. **Similar Performers:**
   - Use `get_all_performers()` with filters based on the performer's \
physical characteristics
   - Find performers with similar characteristics (country, ethnicity, \
physical measurements)
   - Suggest up to 5 similar performers

5. **Recommendations:**
   - Suggest standout scenes to watch first
   - Identify gaps in the collection (popular tags that are missing)
   - Recommend related searches

OUTPUT FORMAT:
- Use markdown to format the response
- Include clear numerical statistics
- Provide actionable insights
- Highlight interesting or unusual findings"""


@mcp.prompt(
    name="library-insights",
    description="Generates insights about the library: trends, metadata gaps, "
                "organization recommendations"
)
def library_insights_prompt() -> str:
    """Prompt for generating general library insights.

    Returns
    -------
    str
        Formatted prompt for library analysis
    """
    return """Analyze the complete Stash library and provide strategic \
insights using the available MCP tools.

REQUIRED ANALYSIS:

1. **Library Overview:**
   - Use `health_check()` to get connectivity and cache statistics
   - Use `get_all_performers(favorites_only=False)` to get performer \
statistics
   - Calculate: total performers, geographic distribution, ethnic diversity

2. **Favorites Analysis:**
   - Compare `get_all_performers(favorites_only=True)` vs \
`get_all_performers(favorites_only=False)`
   - Calculate percentage of favorites
   - Identify patterns in favorite performers (common characteristics)

3. **Content Analysis:**
   - For a sample of favorite performers, analyze their scenes
   - Identify most popular genres/tags
   - Calculate rating statistics

4. **Gap Detection:**
   - Identify underrepresented countries/ethnicities
   - Find physical characteristic ranges with few performers
   - Suggest areas to expand the collection

5. **Organization Recommendations:**
   - Suggest consistent tagging strategies
   - Identify performers that might need more attention
   - Propose useful filters for content discovery

6. **System Optimization:**
   - Analyze cache efficiency
   - Suggest performance improvements based on usage patterns

OUTPUT FORMAT:
- Use markdown with clear sections
- Include specific statistics and percentages
- Provide actionable recommendations
- Highlight improvement opportunities"""


#############################################
# Recommendation Prompts
#############################################

@mcp.prompt(
    name="recommend-scenes",
    description="Based on user preferences, recommends specific scenes with "
                "explanation of why each recommendation"
)
def recommend_scenes_prompt(preferences: str) -> str:
    """Prompt for personalized scene recommendations.

    Parameters
    ----------
    preferences : str
        User preferences (tags, characteristics, etc.)

    Returns
    -------
    str
        Formatted prompt for scene recommendations
    """
    return f"""Generate personalized scene recommendations based on the \
following user preferences: "{preferences}"

RECOMMENDATION PROCESS:

1. **Preference Analysis:**
   - Extract key keywords from preferences: "{preferences}"
   - Identify preferred physical characteristics
   - Detect tags/genres of interest
   - Determine if there are geographic/ethnic preferences

2. **Search for Relevant Performers:**
   - Use `get_all_performers()` with appropriate filters based on preferences
   - If specific physical characteristics are mentioned, use them as filters
   - Prioritize favorite performers if no specific criteria

3. **Scene Analysis by Performer:**
   - For each relevant performer, use `get_all_scenes_from_performer()`
   - Filter scenes with high ratings (rating > 75)
   - Identify scenes that match preferred tags

4. **Scoring System:**
   - Rate each scene based on:
     * Match with preferences (40%)
     * Scene rating (30%)
     * Performer popularity (20%)
     * Variety to avoid monotony (10%)

5. **Final Selection:**
   - Select top 10 recommended scenes
   - Ensure diversity in selection
   - Include a mix of safe favorites and new discoveries

OUTPUT FORMAT:
For each recommended scene include:
- **Scene Title**
- **Performer(s)**: Names and brief description
- **Rating**: Numerical rating
- **Why it's recommended**: Specific explanation of how it matches preferences
- **Relevant tags**: Tags that match interests
- **Match level**: Percentage match with preferences

ADDITIONAL INSTRUCTIONS:
- Order by relevance (highest match first)
- If few exact matches, suggest similar alternatives
- Include a "Discoveries" section with unexpected but potentially interesting \
options"""


@mcp.prompt(
    name="discover-performers",
    description="Discover performers based on specific user criteria"
)
def discover_performers_prompt(criteria: str) -> str:
    """Prompt for performer discovery.

    Parameters
    ----------
    criteria : str
        User search criteria

    Returns
    -------
    str
        Formatted prompt for performer discovery
    """
    return f"""Discover performers that match the following criteria: \
"{criteria}"

DISCOVERY PROCESS:

1. **Criteria Interpretation:**
   - Analyze criteria: "{criteria}"
   - Identify applicable filters:
     * Physical characteristics (height, weight, measurements)
     * Demographics (country, ethnicity)
     * Distinctive features (tattoos, piercings)
     * Content preferences (common tags)

2. **Stratified Search:**
   - **Level 1**: Exact search with all criteria
   - **Level 2**: Relaxed search (main criteria)
   - **Level 3**: Exploratory search (similar criteria)

3. **Analysis of Each Found Performer:**
   - Use `get_performer_info()` for detailed data
   - Use `get_all_scenes_from_performer()` to evaluate content
   - Calculate quality metrics: number of scenes, average rating

4. **Result Categorization:**
   - **Perfect Matches**: Meet all criteria
   - **Strong Matches**: Meet main criteria
   - **Interesting Discoveries**: Partial criteria but high potential
   - **Suggested Alternatives**: Similar but with interesting variations

5. **Diversity Analysis:**
   - Ensure variety in selection
   - Avoid results that are too similar
   - Include options from different backgrounds if appropriate

OUTPUT FORMAT:
For each performer include:
- **Performer Name**
- **Demographics**: Country, ethnicity, age (if available)
- **Physical Characteristics**: Height, weight, measurements, distinctive \
features
- **Content Statistics**: Number of scenes, average rating
- **Criteria Match**: Specific explanation of how they meet criteria
- **Highlights**: What makes this performer unique
- **Recommendation Level**: High/Medium/Exploratory

ADDITIONAL SECTIONS:
- **Executive Summary**: Top 3 recommendations with justification
- **Search Statistics**: How many performers evaluated, filters applied
- **Refinement Suggestions**: How to adjust criteria for better results"""


def main() -> None:
    """Run the MCP server.

    Notes
    -----
    Default transport is stdio for local MCP integration. Uncomment the
    HTTP line for network serving inside a container environment.
    """
    # Attempt an early connection (non-fatal - tools will retry if needed)
    connect_to_stash()
    # mcp.run(transport="http", host="0.0.0.0", port=9001)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
