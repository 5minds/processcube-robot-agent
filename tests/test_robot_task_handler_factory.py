"""
Unit tests for robot_task_handler_factory module.

Tests the Factory, FactoryBuilder, and RobotTaskHandlerFactoryCreator classes
for correct topic generation, robot path resolution, and factory creation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from processcube_robot_agent.robot_agent.rcc.robot_task_handler_factory import (
    Factory,
    FactoryBuilder,
    RobotTaskHandlerFactoryCreator
)


class TestFactory:
    """Test suite for Factory class."""

    def test_factory_initialization(self):
        """Test Factory initialization with filename and topic."""
        filename = "path/to/robot.zip"
        topic = "rcc.robot"

        factory = Factory(filename, topic)

        assert factory._filename == filename
        assert factory._topic == topic

    def test_factory_get_topic(self):
        """Test Factory.get_topic() returns the correct topic."""
        factory = Factory("robot.zip", "rcc.webui")

        assert factory.get_topic() == "rcc.webui"

    @patch('processcube_robot_agent.robot_agent.rcc.robot_task_handler_factory.RobotTaskHandler')
    @patch('processcube_robot_agent.robot_agent.rcc.robot_task_handler_factory.RobotAgent')
    def test_factory_create_external_task(self, mock_robot_agent_class, mock_handler_class):
        """Test Factory.create_external_task() creates handler correctly."""
        # Setup
        mock_config = Mock()
        mock_agent = Mock()
        mock_robot_agent_class.return_value = mock_agent

        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler

        factory = Factory("webui.zip", "rcc.webui")

        # Execute
        result = factory.create_external_task(mock_config)

        # Verify RobotAgent was created with correct filename
        mock_robot_agent_class.assert_called_once_with("webui.zip", mock_config)

        # Verify RobotTaskHandler was created with topic and agent
        mock_handler_class.assert_called_once_with("rcc.webui", mock_agent)

        # Verify handler is returned
        assert result == mock_handler


class TestFactoryBuilder:
    """Test suite for FactoryBuilder class."""

    def test_factory_builder_initialization(self):
        """Test FactoryBuilder initialization."""
        builder = FactoryBuilder("/path/to/wrap", "robot_task")

        assert builder._wrap_dir == "/path/to/wrap"
        assert builder._topic_prefix == "robot_task"

    def test_build_topic_simple(self):
        """Test _build_topic() with simple filename."""
        builder = FactoryBuilder("/wrap", "rcc")

        topic = builder._build_topic("webui.zip")

        assert topic == "rcc.webui"

    def test_build_topic_with_subdirectory(self):
        """Test _build_topic() with subdirectory in filename."""
        builder = FactoryBuilder("/wrap", "rcc")

        topic = builder._build_topic("windows/ui.zip")

        assert topic == "rcc.windows.ui"

    def test_build_topic_nested_directories(self):
        """Test _build_topic() with deeply nested directories."""
        builder = FactoryBuilder("/wrap", "rcc")

        topic = builder._build_topic("level1/level2/level3/robot.zip")

        assert topic == "rcc.level1.level2.level3.robot"

    def test_build_topic_custom_prefix(self):
        """Test _build_topic() with custom topic prefix."""
        builder = FactoryBuilder("/wrap", "custom_prefix")

        topic = builder._build_topic("robot.zip")

        assert topic == "custom_prefix.robot"

    def test_build_robot_path(self, tmp_path):
        """Test _build_robot_path() returns relative path."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        builder = FactoryBuilder(str(wrap_dir), "rcc")

        full_path = str(wrap_dir / "subdir" / "robot.zip")
        robot_path = builder._build_robot_path(full_path)

        assert robot_path == "subdir/robot.zip"

    def test_build_factory(self, tmp_path):
        """Test build() creates Factory with correct properties."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        builder = FactoryBuilder(str(wrap_dir), "rcc")

        full_path = str(wrap_dir / "windows" / "ui.zip")
        factory = builder.build(full_path)

        assert isinstance(factory, Factory)
        assert factory._filename == "windows/ui.zip"
        assert factory.get_topic() == "rcc.windows.ui"


class TestRobotTaskHandlerFactoryCreator:
    """Test suite for RobotTaskHandlerFactoryCreator class."""

    def test_initialization(self, tmp_path):
        """Test RobotTaskHandlerFactoryCreator initialization."""
        wrap_dir = tmp_path / "installed" / "rcc"
        wrap_dir.mkdir(parents=True)

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        assert creator._config == mock_config
        assert creator._wrap_dir == wrap_dir.absolute()
        assert creator._topic_prefix == 'rcc'

    def test_initialization_with_custom_prefix(self, tmp_path):
        """Test initialization with custom topic prefix."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'custom'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        assert creator.get_topic_prefix() == 'custom'

    def test_get_topic_prefix(self, tmp_path):
        """Test get_topic_prefix() returns correct prefix."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'my_robots'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        assert creator.get_topic_prefix() == 'my_robots'

    def test_build_topic(self, tmp_path):
        """Test _build_topic() generates correct topic."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        topic = creator._build_topic("windows/ui.zip")

        assert topic == "rcc.windows.ui"

    def test_build_factory_new(self, tmp_path):
        """Test _build_factory_new() creates factory."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        full_path = str(wrap_dir / "webui.zip")
        factory = creator._build_factory_new(full_path)

        assert isinstance(factory, Factory)
        assert factory.get_topic() == "rcc.webui"

    def test_build_factory_delegates_to_builder(self, tmp_path):
        """Test _build_factory() delegates to FactoryBuilder."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        full_path = str(wrap_dir / "webui.zip")
        factory = creator._build_factory(full_path)

        assert isinstance(factory, Factory)
        assert factory.get_topic() == "rcc.webui"

    def test_iterator_with_no_robots(self, tmp_path):
        """Test __iter__() with no robots in wrap_dir."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        factories = list(creator)

        assert factories == []

    def test_iterator_with_single_robot(self, tmp_path):
        """Test __iter__() with single robot."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        # Create a robot zip file
        robot_file = wrap_dir / "webui.zip"
        robot_file.touch()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        factories = list(creator)

        assert len(factories) == 1
        assert factories[0].get_topic() == "rcc.webui"

    def test_iterator_with_multiple_robots(self, tmp_path):
        """Test __iter__() with multiple robots."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        # Create robot zip files
        (wrap_dir / "webui.zip").touch()
        (wrap_dir / "windows").mkdir()
        (wrap_dir / "windows" / "ui.zip").touch()
        (wrap_dir / "test.zip").touch()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        factories = list(creator)

        # Verify we got 3 factories
        assert len(factories) == 3

        # Verify topics
        topics = [f.get_topic() for f in factories]
        assert "rcc.webui" in topics
        assert "rcc.windows.ui" in topics
        assert "rcc.test" in topics

    def test_iterator_recursive_search(self, tmp_path):
        """Test __iter__() searches recursively for robots."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        # Create nested robot structure
        (wrap_dir / "level1").mkdir()
        (wrap_dir / "level1" / "level2").mkdir()
        (wrap_dir / "level1" / "level2" / "robot.zip").touch()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        factories = list(creator)

        assert len(factories) == 1
        assert factories[0].get_topic() == "rcc.level1.level2.robot"

    def test_iterator_ignores_non_zip_files(self, tmp_path):
        """Test __iter__() only matches .zip files."""
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        # Create various files
        (wrap_dir / "robot.zip").touch()
        (wrap_dir / "robot.tar").touch()
        (wrap_dir / "robot.gz").touch()
        (wrap_dir / "robot.txt").touch()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        creator = RobotTaskHandlerFactoryCreator(mock_config)

        factories = list(creator)

        # Only .zip file should be matched
        assert len(factories) == 1
        assert factories[0].get_topic() == "rcc.robot"