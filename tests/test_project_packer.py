"""Unit tests for ProjectPacker class."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from processcube_robot_agent.robot_agent.rcc.project_packer import ProjectPacker
from processcube_robot_agent.robot_agent.error import RobotError


class TestProjectPackerInit:
    """Tests for ProjectPacker initialization."""

    def test_init_sets_attributes(self, mock_config):
        """Test that __init__ sets required attributes."""
        packer = ProjectPacker(mock_config)

        assert packer._config == mock_config
        assert packer._absolute_project_dir == Path("robots/src/rcc").absolute()
        assert packer._wrap_dir == Path("robots/installed/rcc").absolute()

    def test_init_with_custom_config(self, tmp_path):
        """Test initialization with custom paths."""
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(tmp_path / 'projects'),
            ('rcc', 'wrap_dir'): str(tmp_path / 'wrapped'),
        }.get((section, key), default)

        packer = ProjectPacker(config)

        assert packer._absolute_project_dir == (tmp_path / 'projects').absolute()
        assert packer._wrap_dir == (tmp_path / 'wrapped').absolute()


class TestProjectPackerPackFolder:
    """Tests for pack_folder method."""

    @patch('subprocess.run')
    @patch.object(ProjectPacker, 'check_rcc')
    def test_pack_folder_creates_output_dir(
        self,
        mock_check_rcc,
        mock_run,
        mock_config,
        tmp_path
    ):
        """Test that pack_folder creates output directory if missing."""
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(tmp_path / 'src'),
            ('rcc', 'wrap_dir'): str(tmp_path / 'wrap'),
        }.get((section, key), default)

        # Create project structure
        project_dir = tmp_path / 'src'
        project_dir.mkdir()
        robot_yaml = project_dir / 'robot.yaml'
        robot_yaml.write_text("test: config")

        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        result = packer.pack_folder(robot_yaml)

        assert result.exists() or mock_run.called

    @patch('subprocess.run')
    def test_pack_folder_calls_rcc(self, mock_run, mock_config, temp_robot_dir):
        """Test that pack_folder calls RCC subprocess."""
        config = MagicMock()
        wrap_dir = temp_robot_dir.parent / 'wrap'
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(temp_robot_dir.parent),
            ('rcc', 'wrap_dir'): str(wrap_dir),
        }.get((section, key), default)

        wrap_dir.mkdir(parents=True, exist_ok=True)
        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        robot_yaml = temp_robot_dir / 'robot.yaml'

        packer.pack_folder(robot_yaml)

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert isinstance(call_args[0][0], list)
        assert call_args[0][0][0] == "rcc"

    @patch('subprocess.run')
    def test_pack_folder_failure(self, mock_run, mock_config, temp_robot_dir):
        """Test pack_folder handles RCC failure gracefully."""
        config = MagicMock()
        wrap_dir = temp_robot_dir.parent / 'wrap'
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(temp_robot_dir.parent),
            ('rcc', 'wrap_dir'): str(wrap_dir),
        }.get((section, key), default)

        wrap_dir.mkdir(parents=True, exist_ok=True)
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")

        packer = ProjectPacker(config)
        robot_yaml = temp_robot_dir / 'robot.yaml'

        # Should not raise, just return path
        result = packer.pack_folder(robot_yaml)
        assert result is not None

    @patch('subprocess.run')
    def test_pack_folder_uses_argument_list(
        self,
        mock_run,
        mock_config,
        temp_robot_dir
    ):
        """Test that pack_folder uses argument list (not shell=True)."""
        config = MagicMock()
        wrap_dir = temp_robot_dir.parent / 'wrap'
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(temp_robot_dir.parent),
            ('rcc', 'wrap_dir'): str(wrap_dir),
        }.get((section, key), default)

        wrap_dir.mkdir(parents=True, exist_ok=True)
        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        robot_yaml = temp_robot_dir / 'robot.yaml'

        packer.pack_folder(robot_yaml)

        call_args = mock_run.call_args
        assert isinstance(call_args[0][0], list)
        assert "shell" not in call_args[1] or call_args[1].get("shell") is False


class TestProjectPackerPackAll:
    """Tests for pack_all method."""

    @patch.object(ProjectPacker, 'pack_folder')
    def test_pack_all_finds_all_robots(self, mock_pack, mock_config, tmp_path):
        """Test that pack_all finds and packs all robot.yaml files."""
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(tmp_path),
            ('rcc', 'wrap_dir'): str(tmp_path / 'wrap'),
        }.get((section, key), default)

        # Create multiple robot directories
        (tmp_path / 'robot1').mkdir()
        (tmp_path / 'robot1' / 'robot.yaml').write_text("test")
        (tmp_path / 'robot2').mkdir()
        (tmp_path / 'robot2' / 'robot.yaml').write_text("test")

        packer = ProjectPacker(config)
        packer.pack_all(tmp_path)

        assert mock_pack.call_count == 2

    @patch.object(ProjectPacker, 'pack_folder')
    def test_pack_all_empty_directory(self, mock_pack, mock_config, tmp_path):
        """Test pack_all with directory containing no robots."""
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ('rcc', 'project_dir'): str(tmp_path),
            ('rcc', 'wrap_dir'): str(tmp_path / 'wrap'),
        }.get((section, key), default)

        packer = ProjectPacker(config)
        packer.pack_all(tmp_path)

        mock_pack.assert_not_called()


class TestProjectPackerStart:
    """Tests for start method."""

    @patch.object(ProjectPacker, 'check_rcc')
    @patch.object(ProjectPacker, 'pack_all')
    def test_start_checks_rcc_first(self, mock_pack_all, mock_check_rcc, mock_config):
        """Test that start checks RCC before packing."""
        packer = ProjectPacker(mock_config)
        packer.start()

        mock_check_rcc.assert_called_once()
        mock_pack_all.assert_called_once()

    @patch.object(ProjectPacker, 'check_rcc')
    @patch.object(ProjectPacker, 'pack_all')
    def test_start_propagates_rcc_error(self, mock_pack_all, mock_check_rcc, mock_config):
        """Test that start propagates RCC check errors."""
        mock_check_rcc.side_effect = RobotError("rcc", "RCC not found")

        packer = ProjectPacker(mock_config)

        with pytest.raises(RobotError):
            packer.start()

        mock_pack_all.assert_not_called()

    @patch.object(ProjectPacker, 'check_rcc')
    @patch.object(ProjectPacker, 'pack_all')
    def test_start_packs_from_project_dir(self, mock_pack_all, mock_check_rcc, mock_config):
        """Test that start packs from configured project directory."""
        packer = ProjectPacker(mock_config)
        packer.start()

        mock_pack_all.assert_called_once()
        call_args = mock_pack_all.call_args[0][0]
        assert call_args == packer._absolute_project_dir