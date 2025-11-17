"""
Unit tests for project_watcher module.

Tests the RobotsFileSystemEventHandler and ProjectWatcher classes
for correct file watching, robot packing, and task registration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from watchdog.events import FileModifiedEvent, FileCreatedEvent, DirModifiedEvent

from processcube_robot_agent.robot_agent.rcc.project_watcher import (
    RobotsFileSystemEventHandler,
    ProjectWatcher
)


class TestRobotsFileSystemEventHandler:
    """Test suite for RobotsFileSystemEventHandler class."""

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_initialization(self, mock_packer_class, tmp_path):
        """Test RobotsFileSystemEventHandler initialization."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "robots" / "installed" / "rcc"
        wrap_dir.mkdir(parents=True)

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        # Execute
        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        # Verify
        assert handler._config == mock_config
        assert handler._project_dir == project_dir
        assert handler._external_task_client == mock_external_task_client
        assert handler._project_packer is not None
        assert handler._factory_builder is not None

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_install_robot_creates_and_registers_handler(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test install_robot creates factory and registers with client."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "robots" / "installed" / "rcc"
        wrap_dir.mkdir(parents=True)

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        packed_robot_path = str(wrap_dir / "webui.zip")

        # Execute
        handler.install_robot(packed_robot_path)

        # Verify client was called with topic and handler
        mock_external_task_client.subscribe_to_external_task_for_topic.assert_called_once()
        call_args = mock_external_task_client.subscribe_to_external_task_for_topic.call_args
        assert call_args[0][0] == "rcc.webui"  # topic
        assert call_args[0][1] is not None  # handler object

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_find_robot_yaml_with_direct_robot_file(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test find_robot_yaml finds robot.yaml directly."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)

        robot_dir = project_dir / "webui"
        robot_dir.mkdir()
        robot_yaml = robot_dir / "robot.yaml"
        robot_yaml.touch()

        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        # Create a valid packed robot path in wrap_dir
        packed_robot_path = str(wrap_dir / "webui.zip")

        # Create a mock event for the robot.yaml file
        event = FileModifiedEvent(str(robot_yaml))

        # Execute - mock pack_folder to return a valid path
        handler._project_packer.pack_folder.return_value = packed_robot_path
        handler.on_any_event(event)

        # Verify pack_folder was called
        handler._project_packer.pack_folder.assert_called()

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_find_robot_yaml_with_nested_file(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test find_robot_yaml finds robot.yaml in parent directory."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)

        robot_dir = project_dir / "webui"
        robot_dir.mkdir()
        robot_yaml = robot_dir / "robot.yaml"
        robot_yaml.touch()

        nested_dir = robot_dir / "nested" / "deep"
        nested_dir.mkdir(parents=True)
        nested_file = nested_dir / "tasks.robot"
        nested_file.touch()

        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        # Create event for nested file
        event = FileModifiedEvent(str(nested_file))

        # Create a valid packed robot path in wrap_dir
        packed_robot_path = str(wrap_dir / "webui.zip")

        # Execute
        with patch.object(handler._project_packer, 'pack_folder') as mock_pack:
            mock_pack.return_value = packed_robot_path
            handler.on_any_event(event)

        # Verify pack_folder was called with robot.yaml
        mock_pack.assert_called()
        pack_call_arg = mock_pack.call_args[0][0]
        assert pack_call_arg == robot_yaml

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_on_any_event_handles_file_with_no_robot_yaml(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test on_any_event handles files without robot.yaml."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)

        other_file = project_dir / "readme.txt"
        other_file.touch()

        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        event = FileModifiedEvent(str(other_file))

        # Execute
        handler.on_any_event(event)

        # Verify pack_folder was NOT called
        handler._project_packer.pack_folder.assert_not_called()

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_on_any_event_handles_packer_error(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test on_any_event handles exceptions from pack_folder."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)

        robot_dir = project_dir / "webui"
        robot_dir.mkdir()
        robot_yaml = robot_dir / "robot.yaml"
        robot_yaml.touch()

        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        # Make pack_folder raise an exception
        handler._project_packer.pack_folder.side_effect = RuntimeError("Pack failed")

        event = FileModifiedEvent(str(robot_yaml))

        # Execute - should not raise
        handler.on_any_event(event)

        # Verify error was handled
        handler._project_packer.pack_folder.assert_called()

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.ProjectPacker')
    def test_on_any_event_installs_after_packing(
        self,
        mock_packer_class,
        tmp_path
    ):
        """Test on_any_event calls install_robot after packing."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)

        robot_dir = project_dir / "webui"
        robot_dir.mkdir()
        robot_yaml = robot_dir / "robot.yaml"
        robot_yaml.touch()

        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'wrap_dir'): str(wrap_dir),
            ('rcc', 'topic_prefix'): 'rcc'
        }.get((section, key), default)

        mock_external_task_client = Mock()

        handler = RobotsFileSystemEventHandler(
            mock_config,
            project_dir,
            mock_external_task_client
        )

        packed_path = str(wrap_dir / "webui.zip")
        handler._project_packer.pack_folder.return_value = packed_path

        event = FileModifiedEvent(str(robot_yaml))

        # Execute
        handler.on_any_event(event)

        # Verify pack_folder was called and external task client was notified
        handler._project_packer.pack_folder.assert_called_once()
        mock_external_task_client.subscribe_to_external_task_for_topic.assert_called_once()


class TestProjectWatcher:
    """Test suite for ProjectWatcher class."""

    def test_initialization(self, tmp_path):
        """Test ProjectWatcher initialization."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "robots" / "installed" / "rcc"
        wrap_dir.mkdir(parents=True)

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(project_dir),
            ('rcc', 'wrap_dir'): str(wrap_dir)
        }.get((section, key), default)

        mock_external_task_client = Mock()

        # Execute
        watcher = ProjectWatcher(mock_config, mock_external_task_client)

        # Verify
        assert watcher._config == mock_config
        assert watcher._project_dir == project_dir.absolute()
        assert watcher._wrap_dir == wrap_dir.absolute()
        assert watcher._external_task_client == mock_external_task_client

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.Observer')
    def test_watch_starts_observer(
        self,
        mock_observer_class,
        tmp_path
    ):
        """Test watch() starts the watchdog observer."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(project_dir),
            ('rcc', 'wrap_dir'): str(wrap_dir)
        }.get((section, key), default)

        mock_external_task_client = Mock()

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        watcher = ProjectWatcher(mock_config, mock_external_task_client)

        # Execute
        watcher.watch()

        # Verify observer was created and started
        mock_observer_class.assert_called_once()
        mock_observer.schedule.assert_called_once()
        mock_observer.start.assert_called_once()

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.Observer')
    def test_watch_schedules_event_handler(
        self,
        mock_observer_class,
        tmp_path
    ):
        """Test watch() schedules event handler on project directory."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(project_dir),
            ('rcc', 'wrap_dir'): str(wrap_dir)
        }.get((section, key), default)

        mock_external_task_client = Mock()

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        watcher = ProjectWatcher(mock_config, mock_external_task_client)

        # Execute
        watcher.watch()

        # Verify schedule was called with project_dir and recursive=True
        schedule_call = mock_observer.schedule.call_args
        assert schedule_call[0][1] == project_dir.absolute()
        assert schedule_call[1]['recursive'] is True

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.Observer')
    def test_watch_with_multiple_calls(
        self,
        mock_observer_class,
        tmp_path
    ):
        """Test watch() can be called multiple times."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(project_dir),
            ('rcc', 'wrap_dir'): str(wrap_dir)
        }.get((section, key), default)

        mock_external_task_client = Mock()

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        watcher = ProjectWatcher(mock_config, mock_external_task_client)

        # Execute watch twice
        watcher.watch()
        watcher.watch()

        # Verify observers were created twice
        assert mock_observer_class.call_count == 2
        assert mock_observer.schedule.call_count == 2
        assert mock_observer.start.call_count == 2

    @patch('processcube_robot_agent.robot_agent.rcc.project_watcher.Observer')
    def test_watch_creates_event_handler_with_correct_params(
        self,
        mock_observer_class,
        tmp_path
    ):
        """Test watch() creates event handler with correct parameters."""
        # Setup
        project_dir = tmp_path / "robots" / "src" / "rcc"
        project_dir.mkdir(parents=True)
        wrap_dir = tmp_path / "wrap"
        wrap_dir.mkdir()

        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(project_dir),
            ('rcc', 'wrap_dir'): str(wrap_dir)
        }.get((section, key), default)

        mock_external_task_client = Mock()

        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer

        watcher = ProjectWatcher(mock_config, mock_external_task_client)

        # Execute
        watcher.watch()

        # Verify event handler was created
        schedule_call = mock_observer.schedule.call_args
        event_handler = schedule_call[0][0]

        assert isinstance(event_handler, RobotsFileSystemEventHandler)
        assert event_handler._config == mock_config
        assert event_handler._external_task_client == mock_external_task_client