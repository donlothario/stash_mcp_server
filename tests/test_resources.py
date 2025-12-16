"""Tests for the MCP Resources module.

This module contains comprehensive tests for all resource functions
that expose performer information from the Stash database.
"""

import json
from typing import Any, Callable, Dict
from unittest.mock import Mock, patch

import pytest

from stash_mcp_server.resources import register_resources


class TestListAllPerformers:
    """Tests for the list_all_performers resource."""

    def test_list_all_performers_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test successful listing of all favorite performers.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers_list = [sample_performer.copy() for _ in range(3)]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = (
                performers_list
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/all']()

            # Assert
            assert mock_stash_interface.find_performers.called
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 3
            assert 'performers' in result_data
            assert len(result_data['performers']) == 3

    def test_list_all_performers_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test listing performers when none exist.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 0
            assert result_data['performers'] == []

    def test_list_all_performers_with_full_data(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test listing performers with all available fields.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        sample_performer['tags'] = [
            {'name': 'tag1'},
            {'name': 'tag2'},
        ]

        performers_list = [sample_performer]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers_list

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert len(result_data['performers']) == 1
            performer = result_data['performers'][0]
            assert 'height_cm' in performer
            assert 'weight' in performer
            assert 'tags' in performer

    def test_list_all_performers_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling when listing performers fails.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.side_effect = (
                Exception('Database error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False
            assert 'error' in result_data


class TestGetPerformersInfo:
    """Tests for the get_performers_info resource."""

    def test_get_performer_info_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test successful retrieval of performer info.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performer.return_value = (
                sample_performer
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/{name}'](
                'Test Performer'
            )

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert 'performer' in result_data
            performer = result_data['performer']
            assert performer['name'] == 'Test Performer'

    def test_get_performer_info_not_found(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test retrieval when performer is not found.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performer.return_value = None

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/{name}']('Unknown')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False
            assert 'error' in result_data

    def test_get_performer_info_full_details(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test performer info with all optional fields.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        sample_performer['details'] = 'Bio information'
        sample_performer['tags'] = [{'name': 'tag1'}, {'name': 'tag2'}]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performer.return_value = (
                sample_performer
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/{name}']('Test')

            # Assert
            result_data = json.loads(result)
            performer = result_data['performer']
            assert 'bio' in performer
            assert 'tags' in performer
            assert 'measurements' in performer
            assert 'physical_characteristics' in performer

    def test_get_performer_info_minimal_data(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test performer info with minimal fields.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        minimal_performer = {'name': 'Minimal Performer'}

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performer.return_value = (
                minimal_performer
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/{name}']('Minimal')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            performer = result_data['performer']
            assert performer['name'] == 'Minimal Performer'
            assert performer['country'] == 'Not specified'

    def test_get_performer_info_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in performer info retrieval.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performer.side_effect = (
                Exception('Connection failed')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/{name}']('Test')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetPerformersByCountry:
    """Tests for the get_performers_by_country resource."""

    def test_get_performers_by_country_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test successful retrieval of performers by country.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers_list = [sample_performer.copy() for _ in range(3)]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ) as mock_add_filter:
            mock_stash_interface.find_performers.return_value = (
                performers_list
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/country/{country}'](
                'USA',
            )

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['country'] == 'USA'
            assert result_data['total'] == 3
            mock_add_filter.assert_called_once()

    def test_get_performers_by_country_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test retrieval when no performers from country found.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ):
            mock_stash_interface.find_performers.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/country/{country}'](
                'Unknown',
            )

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 0
            assert result_data['performers'] == []

    def test_get_performers_by_country_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in country filtering.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ):
            mock_stash_interface.find_performers.side_effect = (
                Exception('Filter error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/country/{country}'](
                'USA',
            )

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetPerformersByEthnicity:
    """Tests for the get_performers_by_ethnicity resource."""

    def test_get_performers_by_ethnicity_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test successful retrieval by ethnicity.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers_list = [sample_performer.copy() for _ in range(3)]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ) as mock_add_filter:
            mock_stash_interface.find_performers.return_value = (
                performers_list
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict[
                'stash://performer/ethnicity/{ethnicity}'
            ]('Asian')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['ethnicity'] == 'Asian'
            assert result_data['total'] == 3
            mock_add_filter.assert_called_once()

    def test_get_performers_by_ethnicity_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test retrieval when no performers with ethnicity found.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ):
            mock_stash_interface.find_performers.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict[
                'stash://performer/ethnicity/{ethnicity}'
            ]('Unknown')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 0
            assert result_data['performers'] == []

    def test_get_performers_by_ethnicity_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in ethnicity filtering.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ), patch(
            'stash_mcp_server.resources.add_filter',
        ):
            mock_stash_interface.find_performers.side_effect = (
                Exception('Filter error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict[
                'stash://performer/ethnicity/{ethnicity}'
            ]('Asian')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetPerformerStatistics:
    """Tests for the get_performer_statistics resource."""

    def test_get_statistics_success(
        self,
        mock_stash_interface: Mock,
        sample_performer: Dict[str, Any],
    ) -> None:
        """Test successful retrieval of statistics.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        sample_performer : Dict[str, Any]
            Sample performer data.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers_list = [sample_performer.copy() for _ in range(3)]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = (
                performers_list
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_performers'] == 3
            assert 'statistics' in result_data

    def test_get_statistics_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics retrieval with no performers.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_performers'] == 0
            assert result_data['statistics'] == {}

    def test_get_statistics_with_all_fields(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics with all optional fields present.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers = [
            {
                'name': 'Performer 1',
                'country': 'USA',
                'ethnicity': 'Caucasian',
                'height_cm': 170,
                'weight': 65,
            },
            {
                'name': 'Performer 2',
                'country': 'USA',
                'ethnicity': 'Asian',
                'height_cm': 165,
                'weight': 60,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            stats = result_data['statistics']
            assert 'geographic_distribution' in stats
            assert 'ethnic_distribution' in stats
            assert 'physical_statistics' in stats
            assert 'height' in stats['physical_statistics']
            assert 'weight' in stats['physical_statistics']

    def test_get_statistics_partial_fields(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics with some optional fields missing.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers = [
            {
                'name': 'Performer 1',
                'height_cm': 170,
            },
            {
                'name': 'Performer 2',
                'country': 'Canada',
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            stats = result_data['statistics']
            assert 'physical_statistics' in stats
            assert 'height' in stats['physical_statistics']
            assert 'weight' not in stats['physical_statistics']

    def test_get_statistics_only_weights(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics with only weight data.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers = [
            {
                'name': 'Performer 1',
                'weight': 65,
            },
            {
                'name': 'Performer 2',
                'weight': 60,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            stats = result_data['statistics']
            assert 'physical_statistics' in stats
            assert 'weight' in stats['physical_statistics']
            assert stats['physical_statistics']['weight']['average_kg'] == 62.5

    def test_get_statistics_only_heights(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics with only height data.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers = [
            {
                'name': 'Performer 1',
                'height_cm': 170,
            },
            {
                'name': 'Performer 2',
                'height_cm': 165,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            stats = result_data['statistics']
            assert 'physical_statistics' in stats
            assert 'height' in stats['physical_statistics']
            assert stats['physical_statistics']['height']['average_cm'] == 167.5
            assert 'weight' not in stats['physical_statistics']

    def test_get_statistics_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in statistics calculation.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.side_effect = (
                Exception('Database error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestRegisterResourcesFunction:
    """Tests for the register_resources function."""

    def test_register_resources_registers_all_endpoints(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test that all resource endpoints are registered.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        registered_resources: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                registered_resources[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        # Act
        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            register_resources(mock_mcp)

        # Assert
        expected_uris = [
            'stash://performer/all',
            'stash://performer/{name}',
            'stash://performer/country/{country}',
            'stash://performer/ethnicity/{ethnicity}',
            'stash://performer/stats',
        ]
        for uri in expected_uris:
            assert uri in registered_resources
            assert callable(registered_resources[uri])

    def test_get_statistics_no_demographic_data(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test statistics with performers lacking demographic data.

        Parameters
        ----------
        mock_stash_interface : Mock
            Mocked Stash interface.
        """
        # Arrange
        mock_mcp = Mock()
        resources_dict: Dict[str, Any] = {}

        def capture_resource(
            uri: str,
            name: str,
            description: str,
        ) -> Callable:
            """Capture resource function for testing."""
            def decorator(func: Callable) -> Callable:
                resources_dict[uri] = func
                return func
            return decorator

        mock_mcp.resource = capture_resource

        performers = [
            {
                'name': 'Performer 1',
            },
            {
                'name': 'Performer 2',
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_performers.return_value = performers

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://performer/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            stats = result_data['statistics']
            assert 'geographic_distribution' in stats
            assert stats['geographic_distribution']['total_countries'] == 0
            assert stats['geographic_distribution']['countries'] == {}
            assert 'ethnic_distribution' in stats
            assert stats['ethnic_distribution']['total_ethnicities'] == 0
