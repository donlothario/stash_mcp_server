"""MCP Resources for Stash performer information.

This module provides resources that expose detailed performer information
from the Stash database, allowing clients to access performer data
through the MCP resource protocol.
"""

import json
import logging
from typing import Any, Dict, List

from fastmcp import FastMCP

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
            filters: Dict[str, Any] = {"filter_favorites": True}
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
            filters: Dict[str, Any] = {"filter_favorites": True}
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
