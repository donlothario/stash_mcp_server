"""GraphQL fragment definitions for Stash queries.

This module contains all GraphQL fragment definitions used throughout
the application for consistent data retrieval.
"""

from typing import Final, Dict


PERFORMER_FRAGMENT: Final[str] = """
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


SCENE_FRAGMENT: Final[str] = """
id
title
details
rating100
performers { name rating100 tags { name } }
tags { name }
""".strip()


# Dictionary for easy access to all fragments
FRAGMENTS: Final[Dict[str, str]] = {
    "performer": PERFORMER_FRAGMENT,
    "scene": SCENE_FRAGMENT,
}
