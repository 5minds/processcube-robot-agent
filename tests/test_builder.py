"""Unit tests for builder module."""

import pytest
from unittest.mock import patch, MagicMock
from processcube_robot_agent.robot_agent.builder import build, MultiRunnerFactoryCreator


class TestBuilderBuild:
    """Tests for build function."""

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_creates_factory_creator(self, mock_config_accessor):
        """Test that build returns MultiRunnerFactoryCreator instance."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.return_value = "/path/to/wrap_dir"
        mock_config_accessor.current.return_value = mock_config

        # Execute
        result = build()

        # Verify
        assert isinstance(result, MultiRunnerFactoryCreator)

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_ensures_config_from_env(self, mock_config_accessor):
        """Test that build ensures configuration is loaded from environment."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_accessor.current.return_value = mock_config

        # Execute
        build()

        # Verify ensure_from_env was called
        mock_config_accessor.ensure_from_env.assert_called_once()

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_retrieves_current_config(self, mock_config_accessor):
        """Test that build retrieves the current configuration."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_accessor.current.return_value = mock_config

        # Execute
        build()

        # Verify current() was called
        mock_config_accessor.current.assert_called_once()

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_passes_config_to_factory(self, mock_config_accessor):
        """Test that build passes config to MultiRunnerFactoryCreator."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.return_value = "test_value"
        mock_config_accessor.current.return_value = mock_config

        # Execute
        result = build()

        # Verify factory was initialized with the correct config
        assert result._config is mock_config

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_succeeds_with_valid_config(self, mock_config_accessor):
        """Test that build succeeds when configuration is valid."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.return_value = "/path/to/wrap_dir"
        mock_config_accessor.current.return_value = mock_config

        # Execute and verify no exception
        try:
            result = build()
            assert result is not None
        except Exception as e:
            pytest.fail(f"build() raised {type(e).__name__} unexpectedly: {e}")

    @patch('processcube_robot_agent.robot_agent.builder.ConfigAccessor')
    def test_build_call_sequence(self, mock_config_accessor):
        """Test that build calls ConfigAccessor methods in correct order."""
        # Setup mocks
        call_order = []
        mock_config = MagicMock()

        def track_ensure():
            call_order.append('ensure_from_env')

        def track_current():
            call_order.append('current')
            return mock_config

        mock_config_accessor.ensure_from_env.side_effect = track_ensure
        mock_config_accessor.current.side_effect = track_current

        # Execute
        build()

        # Verify correct call order
        assert call_order == ['ensure_from_env', 'current']