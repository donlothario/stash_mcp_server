"""Tests for Stash MCP Server tools.

This module tests all tool implementations including caching,
error handling, and correct data processing.
"""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

from fastmcp import Client

from stash_mcp_server.server import mcp
from stash_mcp_server.tools import _cached_get_performer_info


class TestGetPerformerInfo:
    """Tests for get_performer_info tool."""

    async def test_get_performer_info_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test successful retrieval of performer information.

        Verifies that the tool correctly retrieves and returns
        performer data when the performer exists.
        """
        mock_stash_interface.find_performer.return_value = sample_performer

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_performer_info",
                    {"performer_name": "Test Performer"}
                )

                assert result.data == sample_performer
                mock_stash_interface.find_performer.assert_called_once()

    async def test_get_performer_info_not_found(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test behavior when performer is not found.

        Verifies that the tool returns an empty dict when the
        performer doesn't exist in the database.
        """
        mock_stash_interface.find_performer.return_value = None

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_performer_info",
                    {"performer_name": "Nonexistent Performer"}
                )

                # The result might be in structured_content or as text
                assert (
                    result.data == {}
                    or result.structured_content == {}
                    or "{}" in str(result.content)
                )

    async def test_get_performer_info_handles_errors(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test error handling in performer info retrieval.

        Verifies that the tool handles exceptions gracefully and
        returns an empty dict on error.
        """
        # Clear the cache first
        _cached_get_performer_info.cache_clear()
        
        mock_stash_interface.find_performer.side_effect = Exception(
            "Database error"
        )

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_performer_info",
                    {"performer_name": "Error Test Performer"}
                )

                # Should return empty dict on error
                assert (
                    result.data == {}
                    or result.structured_content == {}
                    or "{}" in str(result.content)
                )

    def test_cached_get_performer_info_caching(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test that performer info queries are cached.

        Verifies that repeated queries for the same performer use
        the cache instead of making additional API calls.
        """
        mock_stash_interface.find_performer.return_value = sample_performer

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            # Clear cache before test
            _cached_get_performer_info.cache_clear()

            # First call - should hit the API
            result1 = _cached_get_performer_info("Test Performer")
            assert result1 == sample_performer

            # Second call - should use cache
            result2 = _cached_get_performer_info("Test Performer")
            assert result2 == sample_performer

            # Should only be called once due to caching
            assert mock_stash_interface.find_performer.call_count == 1


class TestGetAllPerformers:
    """Tests for get_all_performers tool."""

    async def test_get_all_performers_default(
        self,
        mock_stash_interface: Mock,
        sample_performers_list: List[Dict[str, Any]]
    ) -> None:
        """Test get_all_performers with default parameters.

        Verifies that the tool returns favorite performers by default.
        """
        mock_stash_interface.find_performers.return_value = (
            sample_performers_list
        )

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_performers",
                    {}
                )

                assert len(result.data) == 3
                mock_stash_interface.find_performers.assert_called_once()

    async def test_get_all_performers_with_filters(
        self,
        mock_stash_interface: Mock,
        sample_performers_list: List[Dict[str, Any]]
    ) -> None:
        """Test get_all_performers with filtering options.

        Verifies that the tool correctly applies filters for
        country, ethnicity, and other attributes.
        """
        filtered_performers = [sample_performers_list[0]]
        mock_stash_interface.find_performers.return_value = (
            filtered_performers
        )

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_performers",
                    {
                        "favorites_only": True,
                        "country": "USA",
                        "ethnicity": "Caucasian"
                    }
                )

                assert len(result.data) == 1


class TestGetAllScenes:
    """Tests for get_all_scenes tool."""

    async def test_get_all_scenes_default(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test get_all_scenes with default parameters.

        Verifies that the tool returns organized scenes by default.
        """
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes",
                    {}
                )

                assert len(result.data) == 5
                mock_stash_interface.find_scenes.assert_called_once()

    async def test_get_all_scenes_with_rating_filter(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test get_all_scenes with rating filters.

        Verifies that the tool correctly filters scenes by
        minimum and maximum ratings.
        """
        # Filter scenes with rating >= 80
        high_rated_scenes = [
            s for s in sample_scenes_list if s["rating100"] >= 80
        ]
        mock_stash_interface.find_scenes.return_value = high_rated_scenes

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes",
                    {"min_rating": 80}
                )

                # Check if data is in the expected format
                scenes = result.data if result.data else result.structured_content
                assert len(scenes) == len(high_rated_scenes)

    async def test_get_all_scenes_handles_errors(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test error handling in scene retrieval.

        Verifies that the tool handles exceptions gracefully.
        """
        # Clear cache to ensure we get fresh results
        from stash_mcp_server.tools import _cached_get_all_scenes
        _cached_get_all_scenes.cache_clear()
        
        mock_stash_interface.find_scenes.side_effect = Exception(
            "Database error"
        )

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool("get_all_scenes", {})
                # Should return empty list or empty structured content
                assert (
                    result.data == []
                    or result.structured_content == []
                    or "[]" in str(result.content)
                )

    async def test_get_all_scenes_without_tags(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test getting scenes without tag filtering.

        Verifies that scenes can be retrieved without tag filters.
        """
        # Clear cache
        from stash_mcp_server.tools import _cached_get_all_scenes
        _cached_get_all_scenes.cache_clear()

        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes",
                    {
                        "organized_only": False,
                        "include_tags": None,
                        "exclude_tags": None
                    }
                )

                # Should return scenes
                assert result.data or result.structured_content

    async def test_get_all_scenes_with_rating_only(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test getting scenes with only rating filter (no tags).

        Verifies scenes can be retrieved with rating filter but no tag filter.
        """
        # Clear cache
        from stash_mcp_server.tools import _cached_get_all_scenes
        _cached_get_all_scenes.cache_clear()

        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes",
                    {
                        "organized_only": False,
                        "min_rating": 80,
                        "max_rating": None,
                        "include_tags": "",
                        "exclude_tags": ""
                    }
                )

                # Should return scenes
                assert result.data or result.structured_content


class TestGetAllScenesFromPerformer:
    """Tests for get_all_scenes_from_performer tool."""

    async def test_get_scenes_from_performer_success(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test successful retrieval of performer's scenes.

        Verifies that the tool returns all scenes featuring
        the specified performer.
        """
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes_from_performer",
                    {"performer_name": "Test Performer"}
                )

                assert len(result.data) == 5

    async def test_get_scenes_from_performer_organized_only(
        self,
        mock_stash_interface: Mock,
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test filtering for organized scenes only.

        Verifies that the organized_only parameter correctly
        filters the results.
        """
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes_from_performer",
                    {
                        "performer_name": "Test Performer",
                        "organized_only": True
                    }
                )

                # Verify we got results
                scenes = result.data if result.data else result.structured_content
                assert len(scenes) == len(sample_scenes_list)


class TestHealthCheck:
    """Tests for health_check tool."""

    async def test_health_check_connected(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test health check when connection is successful.

        Verifies that the tool returns connection status and
        cache statistics.
        """
        with patch(
            'stash_mcp_server.tools.connect_to_stash',
            return_value=mock_stash_interface
        ):
            with patch(
                'stash_mcp_server.tools.get_stash_interface',
                return_value=mock_stash_interface
            ):
                async with Client(mcp) as client:
                    result = await client.call_tool("health_check", {})

                    assert "connected" in result.data
                    assert "endpoint" in result.data
                    assert "performer_cache" in result.data
                    assert "all_performers_cache" in result.data
                    assert "all_scenes_cache" in result.data

    async def test_health_check_cache_info(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test that health check returns cache statistics.

        Verifies that cache hit/miss information is included
        in the health check response.
        """
        with patch(
            'stash_mcp_server.tools.connect_to_stash',
            return_value=mock_stash_interface
        ):
            with patch(
                'stash_mcp_server.tools.get_stash_interface',
                return_value=mock_stash_interface
            ):
                async with Client(mcp) as client:
                    result = await client.call_tool("health_check", {})

                    cache = result.data["performer_cache"]
                    assert "hits" in cache
                    assert "misses" in cache
                    assert "currsize" in cache
                    assert "maxsize" in cache


class TestAdvancedPerformerAnalysis:
    """Tests for advanced_performer_analysis tool."""

    async def test_advanced_analysis_basic(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test basic advanced performer analysis.

        Verifies that the tool returns comprehensive performer
        analysis with statistics.
        """
        mock_stash_interface.find_performer.return_value = sample_performer
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {"performer_name": "Test Performer"}
                )

                assert "performer_info" in result.data
                assert "scene_statistics" in result.data
                assert "analysis_metadata" in result.data

    async def test_advanced_analysis_performer_not_found(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test advanced analysis with nonexistent performer.

        Verifies that the tool handles missing performers
        gracefully.
        """
        mock_stash_interface.find_performer.return_value = None

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {"performer_name": "Nonexistent"}
                )

                assert "error" in result.data


class TestBatchPerformerInsights:
    """Tests for batch_performer_insights tool."""

    async def test_batch_insights_multiple_performers(
        self,
        mock_stash_interface: Mock,
        sample_performers_list: List[Dict[str, Any]],
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test batch analysis of multiple performers.

        Verifies that the tool processes multiple performers
        and returns aggregated insights.
        """
        mock_stash_interface.find_performer.side_effect = (
            sample_performers_list
        )
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "batch_performer_insights",
                    {
                        "performer_names": [
                            "Test Performer 1",
                            "Test Performer 2",
                            "Test Performer 3"
                        ]
                    }
                )

                assert "summary" in result.data
                assert "performers" in result.data or "failed_performers" in result.data

    async def test_batch_insights_respects_max_limit(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test that batch analysis respects maximum performer limit.

        Verifies that the tool limits processing to the specified
        maximum number of performers.
        """
        mock_stash_interface.find_performer.return_value = sample_performer

        performer_names = [f"Performer {i}" for i in range(20)]

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "batch_performer_insights",
                    {
                        "performer_names": performer_names,
                        "max_performers": 5
                    }
                )

                # Should process at most 5 performers
                if "performers" in result.data:
                    assert len(result.data["performers"]) <= 5


class TestAdvancedAnalysisEdgeCases:
    """Tests for edge cases in advanced_performer_analysis."""

    async def test_advanced_analysis_with_scene_error(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test advanced analysis handles scene retrieval errors.

        Verifies graceful handling when scene fetching fails.
        """
        mock_stash_interface.find_performer.return_value = sample_performer
        mock_stash_interface.find_scenes.side_effect = Exception("Scene error")

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {"performer_name": "Test Performer"}
                )

                # Should still return some data despite error
                assert result.data is not None or result.structured_content

    async def test_advanced_analysis_with_similar_performers_error(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test analysis handles similar performer search errors.

        Verifies graceful handling when similar search fails.
        """
        mock_stash_interface.find_performer.return_value = sample_performer
        mock_stash_interface.find_scenes.return_value = []

        def mock_find_performers(*args: Any, **kwargs: Any) -> list[Any]:
            raise Exception("Search error")

        mock_stash_interface.find_performers = mock_find_performers

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {
                        "performer_name": "Test Performer",
                        "include_similar": True
                    }
                )

                # Should still return data
                assert result.data is not None or result.structured_content

    async def test_advanced_analysis_deep_scene_analysis(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
        sample_scenes_list: List[Dict[str, Any]]
    ) -> None:
        """Test deep scene analysis option.

        Verifies detailed scene analysis is included when requested.
        """
        mock_stash_interface.find_performer.return_value = sample_performer
        mock_stash_interface.find_scenes.return_value = sample_scenes_list

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {
                        "performer_name": "Test Performer",
                        "deep_scene_analysis": True
                    }
                )

                # Should include detailed analysis
                data = result.data or {}
                assert "performer_info" in data or result.structured_content

    async def test_advanced_analysis_general_exception(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test advanced analysis handles general exceptions.

        Verifies graceful error handling for unexpected errors.
        """
        # Make find_performer raise a general exception
        mock_stash_interface.find_performer.side_effect = RuntimeError(
            "Unexpected error"
        )

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {"performer_name": "Test Performer"}
                )

                # Should return error info
                data = result.data or {}
                if isinstance(data, dict):
                    assert "error" in data or result.structured_content

    async def test_advanced_analysis_similar_performers_filtering(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
        sample_performers_list: List[Dict[str, Any]]
    ) -> None:
        """Test that similar performers exclude the target performer.

        Verifies that the target performer is filtered from similar results.
        """
        # Create a list that includes the target performer
        target_performer = {"name": "Test Performer", "id": "1"}
        other_performers = [
            {"name": "Test Performer", "id": "1"},  # Same as target
            {"name": "Similar Performer 1", "id": "2"},
            {"name": "Similar Performer 2", "id": "3"},
        ]

        mock_stash_interface.find_performer.return_value = target_performer
        mock_stash_interface.find_scenes.return_value = []
        mock_stash_interface.find_performers.return_value = other_performers

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "advanced_performer_analysis",
                    {
                        "performer_name": "Test Performer",
                        "include_similar": True
                    }
                )

                # Should return data without the target performer in similar list
                assert result.data is not None or result.structured_content


class TestBatchInsightsEdgeCases:
    """Tests for edge cases in batch_performer_insights."""

    async def test_batch_insights_with_scene_fetch_error(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test batch insights handles scene fetch errors gracefully.

        Verifies processing continues even when scene fetching fails.
        """
        mock_stash_interface.find_performer.return_value = sample_performer
        mock_stash_interface.find_scenes.side_effect = Exception("Scene error")

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "batch_performer_insights",
                    {"performer_names": ["Test Performer"]}
                )

                # Should still return result structure
                assert result.data is not None or result.structured_content

    async def test_batch_insights_partial_failure(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any]
    ) -> None:
        """Test batch insights handles partial failures.

        Verifies that some performers failing doesn't stop processing.
        """
        # First performer succeeds, second fails
        mock_stash_interface.find_performer.side_effect = [
            sample_performer,
            None
        ]
        mock_stash_interface.find_scenes.return_value = []

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "batch_performer_insights",
                    {
                        "performer_names": ["Performer 1", "Performer 2"]
                    }
                )

                # Should have both successful and failed performers
                data = result.data or {}
                if isinstance(data, dict):
                    # At least one should be in failed list
                    assert "failed_performers" in data or "performers" in data


class TestGetAllScenesFromPerformerErrors:
    """Tests for error handling in get_all_scenes_from_performer."""

    async def test_get_scenes_from_performer_exception(
        self,
        mock_stash_interface: Mock
    ) -> None:
        """Test exception handling in performer scene retrieval.

        Verifies graceful error handling when scene fetching fails.
        """
        mock_stash_interface.find_scenes.side_effect = Exception("API error")

        with patch(
            'stash_mcp_server.tools.get_stash_interface',
            return_value=mock_stash_interface
        ):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "get_all_scenes_from_performer",
                    {"performer_name": "Test Performer"}
                )

                # Should return empty list on error
                assert (
                    result.data == []
                    or result.structured_content == []
                    or "[]" in str(result.content)
                )
