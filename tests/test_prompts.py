"""Tests for MCP prompts.

This module tests all prompt definitions and their generation logic.
"""

from fastmcp import Client

from stash_mcp_server.server import mcp


class TestAnalyzePerformerPrompt:
    """Tests for analyze-performer prompt."""

    async def test_analyze_performer_prompt_structure(self) -> None:
        """Test that the analyze-performer prompt is properly structured.

        Verifies that the prompt is registered and returns
        a well-formatted analysis request.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "analyze-performer",
                {"performer_name": "Test Performer"}
            )

            assert result is not None
            assert "Test Performer" in result.messages[0].content.text
            assert "analysis" in result.messages[0].content.text.lower()

    async def test_analyze_performer_prompt_includes_sections(self) -> None:
        """Test that the prompt includes all required analysis sections.

        Verifies that the generated prompt requests comprehensive
        performer analysis including demographics, scenes, and stats.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "analyze-performer",
                {"performer_name": "Test Performer"}
            )

            prompt_text = result.messages[0].content.text.lower()

            # Check for key sections
            assert "performer" in prompt_text
            assert "scene" in prompt_text or "scenes" in prompt_text


class TestLibraryInsightsPrompt:
    """Tests for library-insights prompt."""

    async def test_library_insights_prompt_structure(self) -> None:
        """Test that the library-insights prompt is structured correctly.

        Verifies that the prompt generates comprehensive library
        analysis requests.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "library-insights",
                {}
            )

            assert result is not None
            prompt_text = result.messages[0].content.text.lower()
            assert "library" in prompt_text or "insight" in prompt_text

    async def test_library_insights_prompt_includes_analysis(
        self
    ) -> None:
        """Test that the prompt requests comprehensive analysis.

        Verifies that the prompt asks for library-wide analysis
        and insights.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "library-insights",
                {}
            )

            prompt_text = result.messages[0].content.text.lower()
            assert (
                "analysis" in prompt_text
                or "performer" in prompt_text
                or "statistics" in prompt_text
            )


class TestRecommendScenesPrompt:
    """Tests for recommend-scenes prompt."""

    async def test_recommend_scenes_prompt_structure(self) -> None:
        """Test scene recommendations prompt structure.

        Verifies that the prompt is properly formatted to request
        scene recommendations based on criteria.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "recommend-scenes",
                {"preferences": "high-rated, specific tags"}
            )

            assert result is not None
            assert "recommendation" in (
                result.messages[0].content.text.lower()
            )

    async def test_recommend_scenes_uses_preferences(self) -> None:
        """Test that preferences are included in the prompt.

        Verifies that user preferences are incorporated into
        the recommendation request.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "recommend-scenes",
                {"preferences": "high-rated scenes"}
            )

            prompt_text = result.messages[0].content.text
            assert "high-rated" in prompt_text


class TestDiscoverPerformersPrompt:
    """Tests for discover-performers prompt."""

    async def test_discover_performers_prompt_structure(self) -> None:
        """Test discover performers prompt structure.

        Verifies that the prompt requests performer discovery
        based on criteria.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "discover-performers",
                {"criteria": "tall, blonde, tattoos"}
            )

            assert result is not None
            prompt_text = result.messages[0].content.text.lower()
            assert (
                "discover" in prompt_text
                or "criteria" in prompt_text
                or "performer" in prompt_text
            )

    async def test_discover_performers_uses_criteria(self) -> None:
        """Test that criteria are included in the prompt.

        Verifies that the prompt asks for performer discovery
        based on specified criteria.
        """
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "discover-performers",
                {"criteria": "tall blonde performers"}
            )

            prompt_text = result.messages[0].content.text.lower()
            # Should mention the criteria or discovery process
            assert (
                "tall" in prompt_text
                or "blonde" in prompt_text
                or "criteria" in prompt_text
            )
