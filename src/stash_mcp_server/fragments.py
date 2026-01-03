"""GraphQL fragment definitions for Stash queries.

This module contains all GraphQL fragment definitions used throughout
the application for consistent data retrieval.
"""

from typing import Dict, Final

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


STUDIO_FRAGMENT: Final[str] = """
id
name
url
details
rating100
favorite
scene_count
parent_studio { id name }
child_studios { id name }
aliases
tags { name }
""".strip()


TAG_FRAGMENT: Final[str] = """
id
name
description
favorite
scene_count
scene_marker_count
aliases
parents { id name }
children { id name }
""".strip()


# Dictionary for easy access to all fragments
FRAGMENTS: Final[Dict[str, str]] = {
    "performer": PERFORMER_FRAGMENT,
    "scene": SCENE_FRAGMENT,
    "studio": STUDIO_FRAGMENT,
    "tag": TAG_FRAGMENT,
}
