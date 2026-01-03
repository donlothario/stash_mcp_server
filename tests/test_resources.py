"""Tests for the MCP Resources module.

This module contains comprehensive tests for all resource functions
that expose performer information from the Stash database.
"""

import json
from typing import Any, Callable, Dict
from unittest.mock import Mock, patch

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


# ============================================================================
# Studio Resources Tests
# ============================================================================

class TestListAllStudios:
    """Tests for the list_all_studios resource."""

    def test_list_all_studios_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful listing of all favorite studios.

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

        studios_list = [
            {
                "id": "1",
                "name": "Studio 1",
                "scene_count": 10,
                "url": "http://example.com",
                "rating100": 85,
            },
            {
                "id": "2",
                "name": "Studio 2",
                "scene_count": 5,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_studios.return_value = studios_list

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/all']()

            # Assert
            assert mock_stash_interface.find_studios.called
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 2
            assert 'studios' in result_data

    def test_list_all_studios_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test listing studios when none exist.

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
            mock_stash_interface.find_studios.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 0
            assert result_data['studios'] == []

    def test_list_all_studios_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling when listing studios.

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
            mock_stash_interface.find_studios.side_effect = (
                Exception('API error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetStudioInfo:
    """Tests for the get_studio_info resource."""

    def test_get_studio_info_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful retrieval of studio info.

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

        studio_data = {
            "id": "1",
            "name": "Test Studio",
            "scene_count": 10,
            "url": "http://example.com",
            "rating100": 85,
            "favorite": True,
            "details": "A test studio",
            "aliases": "TS",
            "parent_studio": {"id": "0", "name": "Parent"},
            "child_studios": [{"id": "2", "name": "Child"}],
            "tags": [{"name": "tag1"}],
        }

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_studio.return_value = studio_data

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/{name}']('Test Studio')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['studio']['name'] == 'Test Studio'
            assert result_data['studio']['scene_count'] == 10

    def test_get_studio_info_not_found(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test studio not found error.

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
            mock_stash_interface.find_studio.return_value = None

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/{name}']('Unknown')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False

    def test_get_studio_info_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in studio info retrieval.

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
            mock_stash_interface.find_studio.side_effect = (
                Exception('API error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/{name}']('Test')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetStudioStatistics:
    """Tests for the get_studio_statistics resource."""

    def test_get_studio_statistics_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful retrieval of studio statistics.

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

        studios = [
            {
                "id": "1",
                "name": "Studio 1",
                "scene_count": 10,
                "rating100": 85,
                "parent_studio": None,
                "child_studios": [{"id": "2"}],
            },
            {
                "id": "2",
                "name": "Studio 2",
                "scene_count": 5,
                "rating100": 75,
                "parent_studio": {"id": "1"},
                "child_studios": None,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_studios.return_value = studios

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_studios'] == 2
            assert result_data['statistics']['total_scenes'] == 15

    def test_get_studio_statistics_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test studio statistics with no studios.

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
            mock_stash_interface.find_studios.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_studios'] == 0

    def test_get_studio_statistics_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in studio statistics.

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
            mock_stash_interface.find_studios.side_effect = (
                Exception('DB error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://studio/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


# ============================================================================
# Tag Resources Tests
# ============================================================================

class TestListAllTags:
    """Tests for the list_all_tags resource."""

    def test_list_all_tags_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful listing of all favorite tags.

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

        tags_list = [
            {
                "id": "1",
                "name": "Tag 1",
                "scene_count": 10,
                "description": "A tag",
                "scene_marker_count": 5,
            },
            {
                "id": "2",
                "name": "Tag 2",
                "scene_count": 8,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_tags.return_value = tags_list

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/all']()

            # Assert
            assert mock_stash_interface.find_tags.called
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 2

    def test_list_all_tags_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test listing tags when none exist.

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
            mock_stash_interface.find_tags.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total'] == 0

    def test_list_all_tags_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling when listing tags.

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
            mock_stash_interface.find_tags.side_effect = (
                Exception('API error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/all']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetTagInfo:
    """Tests for the get_tag_info resource."""

    def test_get_tag_info_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful retrieval of tag info.

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

        tag_data = {
            "id": "1",
            "name": "Test Tag",
            "scene_count": 10,
            "scene_marker_count": 5,
            "favorite": True,
            "description": "A test tag",
            "aliases": "tt",
            "parents": [{"id": "0", "name": "Parent"}],
            "children": [{"id": "2", "name": "Child"}],
        }

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_tag.return_value = tag_data

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/{name}']('Test Tag')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['tag']['name'] == 'Test Tag'

    def test_get_tag_info_not_found(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test tag not found error.

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
            mock_stash_interface.find_tag.return_value = None

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/{name}']('Unknown')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False

    def test_get_tag_info_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in tag info retrieval.

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
            mock_stash_interface.find_tag.side_effect = (
                Exception('API error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/{name}']('Test')

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False


class TestGetTagStatistics:
    """Tests for the get_tag_statistics resource."""

    def test_get_tag_statistics_success(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test successful retrieval of tag statistics.

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

        tags = [
            {
                "id": "1",
                "name": "Tag 1",
                "scene_count": 10,
                "scene_marker_count": 5,
                "parents": [{"id": "0"}],
                "children": [{"id": "2"}],
            },
            {
                "id": "2",
                "name": "Tag 2",
                "scene_count": 8,
                "scene_marker_count": 3,
                "parents": None,
                "children": None,
            },
        ]

        with patch(
            'stash_mcp_server.resources.get_stash_interface',
            return_value=mock_stash_interface,
        ):
            mock_stash_interface.find_tags.return_value = tags

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_tags'] == 2
            assert result_data['statistics']['total_scene_associations'] == 18
            assert result_data['statistics']['total_marker_associations'] == 8

    def test_get_tag_statistics_empty(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test tag statistics with no tags.

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
            mock_stash_interface.find_tags.return_value = []

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is True
            assert result_data['total_tags'] == 0

    def test_get_tag_statistics_exception(
        self,
        mock_stash_interface: Mock,
    ) -> None:
        """Test error handling in tag statistics.

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
            mock_stash_interface.find_tags.side_effect = (
                Exception('DB error')
            )

            # Act
            register_resources(mock_mcp)
            result = resources_dict['stash://tag/stats']()

            # Assert
            result_data = json.loads(result)
            assert result_data['success'] is False
