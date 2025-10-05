"""MCP Prompts for Stash analysis and recommendations.

This module contains all prompt definitions for the Stash MCP server,
providing structured analysis and recommendation capabilities.
"""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompts with the MCP server.

    Parameters
    ----------
    mcp : FastMCP
        The FastMCP instance to register prompts with.
    """

    @mcp.prompt(
        name="analyze-performer",
        description=(
            "Generates a complete analysis of a performer including "
            "statistics, popular scenes, frequent tags and similar "
            "recommendations"
        )
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
        return f"""Completely analyze the performer '{performer_name}' using \
the available Stash MCP server tools.

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
        description=(
            "Generates insights about the library: trends, metadata gaps, "
            "organization recommendations"
        )
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

    @mcp.prompt(
        name="recommend-scenes",
        description=(
            "Based on user preferences, recommends specific scenes with "
            "explanation of why each recommendation"
        )
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
   - Use `get_all_performers()` with appropriate filters based on \
preferences
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
- **Why it's recommended**: Specific explanation of how it matches \
preferences
- **Relevant tags**: Tags that match interests
- **Match level**: Percentage match with preferences

ADDITIONAL INSTRUCTIONS:
- Order by relevance (highest match first)
- If few exact matches, suggest similar alternatives
- Include a "Discoveries" section with unexpected but potentially \
interesting options"""

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
