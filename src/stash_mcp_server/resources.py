"""MCP Resources for Stash performer information.

This module provides resources that expose detailed performer information
from the Stash database, allowing clients to access performer data
through the MCP resource protocol.
"""

import json
import logging
from typing import Any, Dict, List

from fastmcp import FastMCP

from .config import FAVORITES_ONLY
from .connection import get_stash_interface
from .fragments import FRAGMENTS
from .utils import add_filter

logger: logging.Logger = logging.getLogger(__name__)


def register_resources(mcp: FastMCP) -> None:
    """Register all resources with the MCP server.

    Parameters
    ----------
    mcp : FastMCP
        The FastMCP instance to register resources with.
    """

    @mcp.resource(
        uri="stash://performer/all",
        name="All performers",
        description="List of all favorite performers in the Stash database"
    )
    def list_all_performers() -> str:
        """Return a JSON list of all favorite performers.

        Returns
        -------
        str
            JSON string containing all performers with basic information.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"filter_favorites": True}

            performers = stash.find_performers(
                f=filters,
                fragment=FRAGMENTS["performer"],
            )

            if not performers:
                return json.dumps({
                    "success": True,
                    "total": 0,
                    "performers": []
                })

            logger.info("Retrieved %d favorite performers", len(performers))

            # Build performer list
            performers_list = []
            for performer in performers:
                performer_data: Dict[str, Any] = {
                    "name": performer.get("name", "Unknown"),
                    "country": performer.get("country", "Unknown"),
                    "ethnicity": performer.get("ethnicity", "Unknown"),
                }

                height = performer.get("height_cm")
                if height:
                    performer_data["height_cm"] = height

                weight = performer.get("weight")
                if weight:
                    performer_data["weight"] = weight

                # Add tags if available
                tags = performer.get("tags", [])
                if tags:
                    performer_data["tags"] = [
                        tag.get("name", "Unknown") for tag in tags
                    ]

                performers_list.append(performer_data)

            return json.dumps({
                "success": True,
                "total": len(performers_list),
                "performers": performers_list
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error listing all performers: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://performer/{name}",
        name="Performer Information",
        description="Detailed information about a specific performer"
    )
    def get_performers_info(name: str) -> str:
        """Return detailed information about a specific performer.

        Parameters
        ----------
        name : str
            Name of the performer

        Returns
        -------
        str
            JSON string containing detailed performer information.
        """
        try:
            stash = get_stash_interface()
            performer = stash.find_performer(
                name, fragment=FRAGMENTS["performer"]
            )

            if not performer:
                logger.warning("Performer '%s' not found", name)
                return json.dumps({
                    "success": False,
                    "error": f"Performer '{name}' not found in the database."
                })

            logger.info("Retrieved information for performer '%s'", name)

            # Build detailed information
            performer_info: Dict[str, Any] = {
                "name": performer.get("name", "Unknown"),
                "country": performer.get("country", "Not specified"),
                "ethnicity": performer.get("ethnicity", "Not specified"),
                "eye_color": performer.get("eye_color", "Not specified"),
                "hair_color": performer.get("hair_color", "Not specified"),
            }

            # Physical measurements
            height = performer.get("height_cm")
            if height:
                performer_info["height_cm"] = height

            weight = performer.get("weight")
            if weight:
                performer_info["weight"] = weight

            measurements = performer.get("measurements")
            if measurements:
                performer_info["measurements"] = measurements

            # Physical characteristics
            physical_chars: Dict[str, Any] = {}
            piercings = performer.get("piercings")
            if piercings:
                physical_chars["piercings"] = piercings

            tattoos = performer.get("tattoos")
            if tattoos:
                physical_chars["tattoos"] = tattoos

            if physical_chars:
                performer_info["physical_characteristics"] = physical_chars

            # Bio/Details
            details = performer.get("details")
            if details:
                performer_info["bio"] = details

            # Tags
            tags = performer.get("tags", [])
            if tags:
                performer_info["tags"] = [
                    tag.get("name", "Unknown") for tag in tags
                ]

            return json.dumps({
                "success": True,
                "performer": performer_info
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error getting performer info for '%s': %s", name, e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://performer/country/{country}",
        name="Performers by Country",
        description="List of performers from a specific country"
    )
    def get_performers_by_country(country: str) -> str:
        """Return performers from a specific country.

        Parameters
        ----------
        country : str
            Country name to filter by

        Returns
        -------
        str
            JSON string containing performers from the specified country.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"filter_favorites": FAVORITES_ONLY}
            add_filter(filters, "country", country, "EQUALS")

            performers = stash.find_performers(
                f=filters,
                fragment=FRAGMENTS["performer"],
            )

            if not performers:
                return json.dumps({
                    "success": True,
                    "country": country,
                    "total": 0,
                    "performers": []
                })

            logger.info(
                "Retrieved %d performers from %s",
                len(performers),
                country
            )

            performers_list = []
            for performer in performers:
                performers_list.append({
                    "name": performer.get("name", "Unknown"),
                    "ethnicity": performer.get("ethnicity", "Unknown")
                })

            return json.dumps({
                "success": True,
                "country": country,
                "total": len(performers_list),
                "performers": performers_list
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(
                "Error getting performers from country '%s': %s",
                country,
                e
            )
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://performer/ethnicity/{ethnicity}",
        name="Performers by Ethnicity",
        description="List of performers with a specific ethnicity"
    )
    def get_performers_by_ethnicity(ethnicity: str) -> str:
        """Return performers with a specific ethnicity.

        Parameters
        ----------
        ethnicity : str
            Ethnicity to filter by

        Returns
        -------
        str
            JSON string containing performers with the specified ethnicity.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"filter_favorites": FAVORITES_ONLY}
            add_filter(filters, "ethnicity", ethnicity, "EQUALS")

            performers = stash.find_performers(
                f=filters,
                fragment=FRAGMENTS["performer"],
            )

            if not performers:
                return json.dumps({
                    "success": True,
                    "ethnicity": ethnicity,
                    "total": 0,
                    "performers": []
                })

            logger.info(
                "Retrieved %d performers with ethnicity %s",
                len(performers),
                ethnicity
            )

            performers_list = []
            for performer in performers:
                performers_list.append({
                    "name": performer.get("name", "Unknown"),
                    "country": performer.get("country", "Unknown")
                })

            return json.dumps({
                "success": True,
                "ethnicity": ethnicity,
                "total": len(performers_list),
                "performers": performers_list
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(
                "Error getting performers with ethnicity '%s': %s",
                ethnicity,
                e
            )
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://performer/stats",
        name="Performers Statistics",
        description="Statistical summary of all performers in the database"
    )
    def get_performer_statistics() -> str:
        """Return statistical summary of all performers.

        Returns
        -------
        str
            JSON string containing performer statistics.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"filter_favorites": True}

            performers = stash.find_performers(
                f=filters,
                fragment=FRAGMENTS["performer"],
            )

            if not performers:
                return json.dumps({
                    "success": True,
                    "total_performers": 0,
                    "statistics": {}
                })

            logger.info("Generated statistics for %d performers", len(performers))

            # Calculate statistics
            countries: Dict[str, int] = {}
            ethnicities: Dict[str, int] = {}
            heights: List[int] = []
            weights: List[int] = []

            for performer in performers:
                country = performer.get("country")
                if country:
                    countries[country] = countries.get(country, 0) + 1

                ethnicity = performer.get("ethnicity")
                if ethnicity:
                    ethnicities[ethnicity] = ethnicities.get(
                        ethnicity, 0
                    ) + 1

                height = performer.get("height_cm")
                if height:
                    heights.append(height)

                weight = performer.get("weight")
                if weight:
                    weights.append(weight)

            # Build statistics object
            stats: Dict[str, Any] = {
                "geographic_distribution": {
                    "total_countries": len(countries),
                    "countries": dict(
                        sorted(
                            countries.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:10]
                    )
                },
                "ethnic_distribution": {
                    "total_ethnicities": len(ethnicities),
                    "ethnicities": dict(
                        sorted(
                            ethnicities.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:10]
                    )
                }
            }

            # Physical statistics
            if heights:
                avg_height = sum(heights) / len(heights)
                stats["physical_statistics"] = {
                    "height": {
                        "average_cm": round(avg_height, 1),
                        "min_cm": min(heights),
                        "max_cm": max(heights),
                        "count": len(heights)
                    }
                }

            if weights:
                avg_weight = sum(weights) / len(weights)
                if "physical_statistics" not in stats:
                    stats["physical_statistics"] = {}
                stats["physical_statistics"]["weight"] = {
                    "average_kg": round(avg_weight, 1),
                    "min_kg": min(weights),
                    "max_kg": max(weights),
                    "count": len(weights)
                }

            return json.dumps({
                "success": True,
                "total_performers": len(performers),
                "statistics": stats
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error generating performer statistics: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    # ========================================================================
    # Studio Resources
    # ========================================================================

    @mcp.resource(
        uri="stash://studio/all",
        name="All studios",
        description="List of all favorite studios in the Stash database"
    )
    def list_all_studios() -> str:
        """Return a JSON list of all favorite studios.

        Returns
        -------
        str
            JSON string containing all studios with basic information.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"favorite": FAVORITES_ONLY}

            studios = stash.find_studios(
                f=filters,
                fragment=FRAGMENTS["studio"],
            )

            if not studios:
                return json.dumps({
                    "success": True,
                    "total": 0,
                    "studios": []
                })

            logger.info("Retrieved %d favorite studios", len(studios))

            studios_list = []
            for studio in studios:
                studio_data: Dict[str, Any] = {
                    "name": studio.get("name", "Unknown"),
                    "scene_count": studio.get("scene_count", 0),
                }

                url = studio.get("url")
                if url:
                    studio_data["url"] = url

                rating = studio.get("rating100")
                if rating:
                    studio_data["rating100"] = rating

                parent = studio.get("parent_studio")
                if parent:
                    studio_data["parent_studio"] = parent.get("name")

                tags = studio.get("tags", [])
                if tags:
                    studio_data["tags"] = [
                        tag.get("name", "Unknown") for tag in tags
                    ]

                studios_list.append(studio_data)

            return json.dumps({
                "success": True,
                "total": len(studios_list),
                "studios": studios_list
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error listing all studios: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://studio/{name}",
        name="Studio Information",
        description="Detailed information about a specific studio"
    )
    def get_studio_info(name: str) -> str:
        """Return detailed information about a specific studio.

        Parameters
        ----------
        name : str
            Name of the studio

        Returns
        -------
        str
            JSON string containing detailed studio information.
        """
        try:
            stash = get_stash_interface()
            studio = stash.find_studio(name, fragment=FRAGMENTS["studio"])

            if not studio:
                logger.warning("Studio '%s' not found", name)
                return json.dumps({
                    "success": False,
                    "error": f"Studio '{name}' not found in the database."
                })

            logger.info("Retrieved information for studio '%s'", name)

            studio_info: Dict[str, Any] = {
                "name": studio.get("name", "Unknown"),
                "scene_count": studio.get("scene_count", 0),
                "favorite": studio.get("favorite", False),
            }

            url = studio.get("url")
            if url:
                studio_info["url"] = url

            details = studio.get("details")
            if details:
                studio_info["details"] = details

            rating = studio.get("rating100")
            if rating:
                studio_info["rating100"] = rating

            aliases = studio.get("aliases")
            if aliases:
                studio_info["aliases"] = aliases

            parent = studio.get("parent_studio")
            if parent:
                studio_info["parent_studio"] = {
                    "id": parent.get("id"),
                    "name": parent.get("name")
                }

            children = studio.get("child_studios", [])
            if children:
                studio_info["child_studios"] = [
                    {"id": child.get("id"), "name": child.get("name")}
                    for child in children
                ]

            tags = studio.get("tags", [])
            if tags:
                studio_info["tags"] = [
                    tag.get("name", "Unknown") for tag in tags
                ]

            return json.dumps({
                "success": True,
                "studio": studio_info
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error getting studio info for '%s': %s", name, e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://studio/stats",
        name="Studios Statistics",
        description="Statistical summary of all studios in the database"
    )
    def get_studio_statistics() -> str:
        """Return statistical summary of all studios.

        Returns
        -------
        str
            JSON string containing studio statistics.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"favorite": FAVORITES_ONLY}

            studios = stash.find_studios(
                f=filters,
                fragment=FRAGMENTS["studio"],
            )

            if not studios:
                return json.dumps({
                    "success": True,
                    "total_studios": 0,
                    "statistics": {}
                })

            logger.info("Generated statistics for %d studios", len(studios))

            total_scenes = 0
            ratings: List[int] = []
            with_parent = 0
            with_children = 0

            for studio in studios:
                scene_count = studio.get("scene_count", 0)
                total_scenes += scene_count

                rating = studio.get("rating100")
                if rating:
                    ratings.append(rating)

                if studio.get("parent_studio"):
                    with_parent += 1

                if studio.get("child_studios"):
                    with_children += 1

            stats: Dict[str, Any] = {
                "total_scenes": total_scenes,
                "hierarchy": {
                    "studios_with_parent": with_parent,
                    "studios_with_children": with_children
                }
            }

            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                stats["ratings"] = {
                    "average": round(avg_rating, 1),
                    "min": min(ratings),
                    "max": max(ratings),
                    "count": len(ratings)
                }

            return json.dumps({
                "success": True,
                "total_studios": len(studios),
                "statistics": stats
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error generating studio statistics: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    # ========================================================================
    # Tag Resources
    # ========================================================================

    @mcp.resource(
        uri="stash://tag/all",
        name="All tags",
        description="List of all favorite tags in the Stash database"
    )
    def list_all_tags() -> str:
        """Return a JSON list of all favorite tags.

        Returns
        -------
        str
            JSON string containing all tags with basic information.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"favorite": FAVORITES_ONLY}

            tags = stash.find_tags(f=filters, fragment=FRAGMENTS["tag"])

            if not tags:
                return json.dumps({
                    "success": True,
                    "total": 0,
                    "tags": []
                })

            logger.info("Retrieved %d favorite tags", len(tags))

            tags_list = []
            for tag in tags:
                tag_data: Dict[str, Any] = {
                    "name": tag.get("name", "Unknown"),
                    "scene_count": tag.get("scene_count", 0),
                }

                description = tag.get("description")
                if description:
                    tag_data["description"] = description

                marker_count = tag.get("scene_marker_count", 0)
                if marker_count:
                    tag_data["scene_marker_count"] = marker_count

                parents = tag.get("parents", [])
                if parents:
                    tag_data["parents"] = [
                        p.get("name", "Unknown") for p in parents
                    ]

                tags_list.append(tag_data)

            return json.dumps({
                "success": True,
                "total": len(tags_list),
                "tags": tags_list
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error listing all tags: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://tag/{name}",
        name="Tag Information",
        description="Detailed information about a specific tag"
    )
    def get_tag_info(name: str) -> str:
        """Return detailed information about a specific tag.

        Parameters
        ----------
        name : str
            Name of the tag

        Returns
        -------
        str
            JSON string containing detailed tag information.
        """
        try:
            stash = get_stash_interface()
            tag = stash.find_tag(name, fragment=FRAGMENTS["tag"])

            if not tag:
                logger.warning("Tag '%s' not found", name)
                return json.dumps({
                    "success": False,
                    "error": f"Tag '{name}' not found in the database."
                })

            logger.info("Retrieved information for tag '%s'", name)

            tag_info: Dict[str, Any] = {
                "name": tag.get("name", "Unknown"),
                "scene_count": tag.get("scene_count", 0),
                "scene_marker_count": tag.get("scene_marker_count", 0),
                "favorite": tag.get("favorite", False),
            }

            description = tag.get("description")
            if description:
                tag_info["description"] = description

            aliases = tag.get("aliases")
            if aliases:
                tag_info["aliases"] = aliases

            parents = tag.get("parents", [])
            if parents:
                tag_info["parents"] = [
                    {"id": p.get("id"), "name": p.get("name")}
                    for p in parents
                ]

            children = tag.get("children", [])
            if children:
                tag_info["children"] = [
                    {"id": c.get("id"), "name": c.get("name")}
                    for c in children
                ]

            return json.dumps({
                "success": True,
                "tag": tag_info
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error getting tag info for '%s': %s", name, e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.resource(
        uri="stash://tag/stats",
        name="Tags Statistics",
        description="Statistical summary of all tags in the database"
    )
    def get_tag_statistics() -> str:
        """Return statistical summary of all tags.

        Returns
        -------
        str
            JSON string containing tag statistics.
        """
        try:
            stash = get_stash_interface()
            filters: Dict[str, Any] = {"favorite": FAVORITES_ONLY}

            tags = stash.find_tags(f=filters, fragment=FRAGMENTS["tag"])

            if not tags:
                return json.dumps({
                    "success": True,
                    "total_tags": 0,
                    "statistics": {}
                })

            logger.info("Generated statistics for %d tags", len(tags))

            total_scenes = 0
            total_markers = 0
            scene_counts: List[int] = []
            with_parents = 0
            with_children = 0

            for tag in tags:
                scene_count = tag.get("scene_count", 0)
                total_scenes += scene_count
                scene_counts.append(scene_count)

                marker_count = tag.get("scene_marker_count", 0)
                total_markers += marker_count

                if tag.get("parents"):
                    with_parents += 1

                if tag.get("children"):
                    with_children += 1

            stats: Dict[str, Any] = {
                "total_scene_associations": total_scenes,
                "total_marker_associations": total_markers,
                "hierarchy": {
                    "tags_with_parents": with_parents,
                    "tags_with_children": with_children
                }
            }

            if scene_counts:
                avg_scenes = sum(scene_counts) / len(scene_counts)
                stats["scene_usage"] = {
                    "average_per_tag": round(avg_scenes, 1),
                    "min": min(scene_counts),
                    "max": max(scene_counts)
                }

            return json.dumps({
                "success": True,
                "total_tags": len(tags),
                "statistics": stats
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error generating tag statistics: %s", e)
            return json.dumps({
                "success": False,
                "error": str(e)
            })
