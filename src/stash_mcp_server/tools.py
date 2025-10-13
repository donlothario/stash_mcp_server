"""MCP Tools for Stash queries and analysis.

This module contains all tool definitions for the Stash MCP server,
providing cached queries and advanced analysis capabilities.
"""

import logging
import time
from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP

from .config import (
    DEFAULT_MAX_BATCH_PERFORMERS,
    PERFORMER_CACHE_SIZE,
    PERFORMERS_LIST_CACHE_SIZE,
    RATING_AVERAGE,
    RATING_EXCELLENT,
    RATING_GOOD,
    SCENES_CACHE_SIZE,
)
from .connection import connect_to_stash, get_stash_interface
from .fragments import FRAGMENTS
from .utils import (
    add_filter,
    build_rating_filter,
    build_tag_filter,
    calculate_average_rating,
    count_scenes_by_rating,
    extract_tag_frequency,
    format_filter_description,
)

logger: logging.Logger = logging.getLogger(__name__)


# ============================================================================
# Cached Query Functions
# ============================================================================

@lru_cache(maxsize=PERFORMER_CACHE_SIZE)
def _cached_get_performer_info(performer_name: str) -> Dict:
    """Internal cached implementation for performer info.

    Parameters
    ----------
    performer_name : str
        Exact name of the performer.

    Returns
    -------
    Dict
        Performer metadata (empty dict if not found / error).
    """
    try:
        stash = get_stash_interface()
        performer = stash.find_performer(
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
    except Exception as e:
        logger.error(
            "Error _cached_get_performer_info('%s'): %s",
            performer_name,
            e
        )
        return {}


@lru_cache(maxsize=SCENES_CACHE_SIZE)
def _cached_get_all_scenes(
    organized_only: bool = True,
    exclude_tags: Optional[str] = None,
    include_tags: Optional[str] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None
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
        stash = get_stash_interface()
        filters: Dict = {}

        if organized_only:
            filters["organized"] = True

        # Add tag count filter to ensure scenes have tags
        filters["tag_count"] = {"value": 0, "modifier": "GREATER_THAN"}

        # Build and add tag filter
        tag_filter = build_tag_filter(include_tags, exclude_tags)
        if tag_filter:
            filters["tags"] = tag_filter

        # Build and add rating filter
        rating_filter = build_rating_filter(min_rating, max_rating)
        if rating_filter:
            filters["rating100"] = rating_filter

        scenes = stash.find_scenes(f=filters, fragment=FRAGMENTS["scene"])

        filter_desc = format_filter_description(
            organized_only=organized_only,
            exclude_tags=exclude_tags,
            include_tags=include_tags,
            min_rating=min_rating,
            max_rating=max_rating
        )
        logger.info("Found %d scenes%s", len(scenes), filter_desc)

        return scenes  # type: ignore[no-any-return]

    except Exception as e:
        logger.error("Error in _cached_get_all_scenes: %s", e)
        return []


@lru_cache(maxsize=PERFORMERS_LIST_CACHE_SIZE)
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
    tattoos: Optional[str] = None,
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
        Modifier for country filter.
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
        Modifier for height filter.
    height_cm_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN height filters.
    measurements : Optional[str], default None
        Filter by measurements.
    measurements_modifier : str, default "EQUALS"
        Modifier for measurements filter.
    piercings : Optional[str], default None
        Filter by piercings.
    tattoos : Optional[str], default None
        Filter by tattoos.
    weight : Optional[int], default None
        Filter by weight.
    weight_modifier : str, default "EQUALS"
        Modifier for weight filter.
    weight_value2 : Optional[int], default None
        Second value for BETWEEN/NOT_BETWEEN weight filters.

    Returns
    -------
    List[Dict]
        Performer objects (empty list on error).
    """
    try:
        stash = get_stash_interface()
        filters: Dict = {}

        if favorites_only:
            filters["filter_favorites"] = True

        # Add all filters using the helper function
        add_filter(filters, "country", country, country_modifier)
        add_filter(filters, "ethnicity", ethnicity, ethnicity_modifier)
        add_filter(filters, "eye_color", eye_color, eye_color_modifier)
        add_filter(filters, "hair_color", hair_color, hair_color_modifier)
        add_filter(
            filters, "height_cm", height_cm, height_cm_modifier,
            height_cm_value2
        )
        add_filter(
            filters, "measurements", measurements, measurements_modifier
        )
        add_filter(filters, "piercings", piercings, "INCLUDES")
        add_filter(filters, "tattoos", tattoos, "INCLUDES")
        add_filter(filters, "weight", weight, weight_modifier, weight_value2)

        performers = stash.find_performers(
            f=filters,
            fragment=FRAGMENTS["performer"],
        )

        # Create filter description for logging
        active_filters = []
        if favorites_only:
            active_filters.append("favorites")

        filter_fields = [
            "country", "ethnicity", "eye_color", "hair_color",
            "height_cm", "measurements", "piercings", "tattoos", "weight"
        ]
        for field in filter_fields:
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
        logger.error("Error _cached_get_all_performers: %s", e)
        return []


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp: FastMCP) -> None:
    """Register all tools with the MCP server.

    Parameters
    ----------
    mcp : FastMCP
        The FastMCP instance to register tools with.
    """

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

    @mcp.tool(
        name="get_all_performers",
        description=(
            "Return a list of performers with advanced filtering options"
        ),
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

        See _cached_get_all_performers for full parameter documentation.
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
        description=(
            "Return all scenes from Stash with advanced filtering options"
        ),
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

        See _cached_get_all_scenes for full parameter documentation.
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
            stash = get_stash_interface()
            filters: Dict = {
                "performers_filter": {
                    "name": {"value": performer_name, "modifier": "EQUALS"}
                }
            }
            if organized_only:
                filters["organized"] = True

            scenes = stash.find_scenes(
                f=filters,
                fragment=FRAGMENTS["scene"],
            )
            logger.info(
                "Found %d scene(s) for '%s'%s",
                len(scenes),
                performer_name,
                " (organized only)" if organized_only else ""
            )
            return scenes  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(
                "Error get_all_scenes_from_performer('%s'): %s",
                performer_name,
                e
            )
            return []

    @mcp.tool(
        name="health_check",
        description=(
            "Return basic health/connectivity information for the MCP server"
        ),
        annotations={
            "title": "Health Check",
            "readOnlyHint": True,
            "openWorldHint": False
        }
    )
    def health_check() -> Dict:
        """Return basic health / connectivity information.

        Returns
        -------
        Dict
            Diagnostic data: connection status, endpoint, cached counts.
        """
        connected = connect_to_stash() is not None

        # Access internal cache wrappers for statistics
        performer_cache_info = _cached_get_performer_info.cache_info()
        all_perf_cache_info = _cached_get_all_performers.cache_info()
        all_scenes_cache_info = _cached_get_all_scenes.cache_info()

        return {
            "connected": connected,
            "endpoint": get_stash_interface()._server_url  # type: ignore
            if connected else None,
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

    # Register advanced tools
    _register_advanced_tools(mcp)


def _register_advanced_tools(mcp: FastMCP) -> None:
    """Register advanced analysis tools with the MCP server.

    Parameters
    ----------
    mcp : FastMCP
        The FastMCP instance to register tools with.
    """

    @mcp.tool(
        name="advanced_performer_analysis",
        description=(
            "Advanced performer analysis with progress reporting and "
            "contextual logging"
        ),
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
                stash = get_stash_interface()
                filters = {
                    "performers_filter": {
                        "name": {
                            "value": performer_name,
                            "modifier": "EQUALS"
                        }
                    }
                }
                scenes = stash.find_scenes(
                    f=filters, fragment=FRAGMENTS["scene"]
                )
            except Exception as e:
                await ctx.warning(f"Error getting scenes: {e}")

            await ctx.report_progress(40, 100)

            # Statistical analysis of scenes
            scene_stats = {
                "total_scenes": len(scenes),
                "average_rating": calculate_average_rating(scenes),
                "top_rated_scenes": [],
                "all_tags": [],
                "tag_frequency": {}
            }

            if scenes:
                # Get top rated scenes
                top_rated = [
                    s for s in scenes
                    if s.get("rating100") is not None
                    and s.get("rating100") > 80
                ]
                scene_stats["top_rated_scenes"] = sorted(
                    top_rated,
                    key=lambda x: x.get("rating100", 0),
                    reverse=True
                )[:5]

                # Tag analysis
                tag_frequency = extract_tag_frequency(scenes)
                scene_stats["tag_frequency"] = tag_frequency
                scene_stats["all_tags"] = list(tag_frequency.keys())

            await ctx.report_progress(60, 100)

            # Phase 3: Similar performers (if requested)
            similar_performers: list[dict[str, Any]] = []
            if include_similar:
                await ctx.info("Searching for similar performers...")
                try:
                    perf_filters: Dict[str, Any] = {}
                    if performer_info.get("country"):
                        perf_filters["country"] = performer_info["country"]
                    if performer_info.get("ethnicity"):
                        perf_filters["ethnicity"] = performer_info["ethnicity"]

                    # Get all performers (cannot use **filters due to caching)
                    all_performers = _cached_get_all_performers(
                        favorites_only=False,
                        country=perf_filters.get("country"),
                        ethnicity=perf_filters.get("ethnicity")
                    )

                    # Filter out current performer and take first 5
                    similar_performers = [
                        p for p in all_performers
                        if p.get("name", "").lower()
                        != performer_name.lower()
                    ][:5]

                except Exception as e:
                    await ctx.warning(
                        f"Error searching similar performers: {e}"
                    )

            await ctx.report_progress(80, 100)

            # Phase 4: Deep scene analysis (if requested)
            detailed_scene_analysis = {}
            if deep_scene_analysis and scenes:
                await ctx.info("Performing deep scene analysis...")

                detailed_scene_analysis = {
                    "scenes_by_rating": {
                        "excellent": count_scenes_by_rating(
                            scenes, RATING_EXCELLENT
                        ),
                        "good": count_scenes_by_rating(
                            scenes, RATING_GOOD, RATING_EXCELLENT
                        ),
                        "average": count_scenes_by_rating(
                            scenes, RATING_AVERAGE, RATING_GOOD - 1
                        ),
                        "below_average": count_scenes_by_rating(
                            scenes, 0, RATING_AVERAGE
                        )
                    },
                    "scenes_per_year": {},
                    "most_common_tags": sorted(
                        tag_frequency.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                }

            await ctx.report_progress(100, 100)
            await ctx.info(f"Analysis completed for {performer_name}")

            # Build final response
            result: Dict[str, Any] = {
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
        description=(
            "Generates insights for multiple performers with detailed "
            "progress"
        ),
        annotations={
            "title": "Batch Performer Insights",
            "readOnlyHint": True,
            "openWorldHint": False
        }
    )
    async def batch_performer_insights(
        performer_names: List[str],
        ctx: Context,
        max_performers: int = DEFAULT_MAX_BATCH_PERFORMERS
    ) -> Dict:
        """Generates insights for multiple performers with progress.

        Parameters
        ----------
        performer_names : List[str]
            List of performer names to analyze
        ctx : Context
            MCP context for logging and progress
        max_performers : int, default DEFAULT_MAX_BATCH_PERFORMERS
            Maximum number of performers to process

        Returns
        -------
        Dict
            Aggregated insights from all performers
        """
        await ctx.info(
            f"Starting batch analysis of {len(performer_names)} performers"
        )

        # Limit number of performers for performance
        if len(performer_names) > max_performers:
            await ctx.warning(
                f"Limiting analysis to {max_performers} performers "
                f"(from {len(performer_names)} requested)"
            )
            performer_names = performer_names[:max_performers]

        total_performers = len(performer_names)
        processed_performers: List[Dict[str, Any]] = []
        failed_performers = []

        for i, performer_name in enumerate(performer_names):
            progress = int((i / total_performers) * 100)
            await ctx.report_progress(progress, 100)
            await ctx.info(
                f"Processing performer {i + 1}/{total_performers}: "
                f"{performer_name}"
            )

            try:
                performer_info = _cached_get_performer_info(performer_name)
                if performer_info:
                    # Get basic scene count
                    scenes = []
                    try:
                        stash = get_stash_interface()
                        filters = {
                            "performers_filter": {
                                "name": {
                                    "value": performer_name,
                                    "modifier": "EQUALS"
                                }
                            }
                        }
                        scenes = stash.find_scenes(
                            f=filters, fragment=FRAGMENTS["scene"]
                        )
                    except Exception:
                        pass  # Continue without scenes if error

                    avg_rating = calculate_average_rating(scenes)

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
        await ctx.info(
            f"Analysis completed. Processed: {len(processed_performers)}, "
            f"Failed: {len(failed_performers)}"
        )

        # Generate aggregated insights
        if processed_performers:
            countries = [
                p["info"].get("country")
                for p in processed_performers
                if p["info"].get("country")
            ]
            ethnicities = [
                p["info"].get("ethnicity")
                for p in processed_performers
                if p["info"].get("ethnicity")
            ]

            insights = {
                "summary": {
                    "total_processed": len(processed_performers),
                    "total_failed": len(failed_performers),
                    "average_scenes_per_performer": (
                        sum(
                            p["scene_count"]
                            for p in processed_performers
                        ) / len(processed_performers)
                    ),
                    "average_rating_across_all": (
                        sum(
                            p["average_rating"]
                            for p in processed_performers
                        ) / len(processed_performers)
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
