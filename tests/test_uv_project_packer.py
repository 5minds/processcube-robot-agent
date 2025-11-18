"""Unit tests for UV ProjectPacker class."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory
import zipfile

from processcube_robot_agent.robot_agent.uv.project_packer import ProjectPacker
from processcube_sdk.configuration import Config


class TestProjectPackerPackFolder:
    """Tests for pack_folder method."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with TemporaryDirectory() as project_dir:
            with TemporaryDirectory() as wrap_dir:
                yield project_dir, wrap_dir

    @patch('processcube_robot_agent.robot_agent.uv.project_packer.subprocess.run')
    def test_pack_folder_creates_zip(self, mock_run, temp_dirs):
        """Test that pack_folder creates a ZIP file."""
        project_dir, wrap_dir = temp_dirs
        
        # Override config for temp directories
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda section, key, default=None: {
            ('uv', 'project_dir'): project_dir,
            ('uv', 'wrap_dir'): wrap_dir
        }.get((section, key), default)

        # Create a test project structure
        robot_dir = Path(project_dir) / "example-robot"
        robot_dir.mkdir(parents=True)
        (robot_dir / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '0.1.0'")
        (robot_dir / "main.py").write_text("print('hello')")

        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        result = packer.pack_folder(robot_dir / "pyproject.toml")

        # Check that a ZIP file was created
        assert result.exists()
        assert result.suffix == '.zip'

    @patch('processcube_robot_agent.robot_agent.uv.project_packer.subprocess.run')
    def test_pack_folder_excludes_virtual_env(self, mock_run, temp_dirs):
        """Test that pack_folder excludes virtual environments."""
        project_dir, wrap_dir = temp_dirs

        config = MagicMock(spec=Config)
        config.get.side_effect = lambda section, key, default=None: {
            ('uv', 'project_dir'): project_dir,
            ('uv', 'wrap_dir'): wrap_dir
        }.get((section, key), default)

        # Create a test project with .venv directory
        robot_dir = Path(project_dir) / "example-robot"
        robot_dir.mkdir(parents=True)
        (robot_dir / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '0.1.0'")
        (robot_dir / "main.py").write_text("print('hello')")
        venv_dir = robot_dir / ".venv" / "bin"
        venv_dir.mkdir(parents=True)
        (venv_dir / "python").write_text("binary")

        # Mock subprocess to simulate uv lock success
        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        result = packer.pack_folder(robot_dir / "pyproject.toml")

        # Check ZIP contents don't include .venv
        with zipfile.ZipFile(result, 'r') as zipf:
            names = zipf.namelist()
            assert not any('.venv' in name for name in names), "Virtual env should not be in ZIP"

    @patch('processcube_robot_agent.robot_agent.uv.project_packer.subprocess.run')
    def test_pack_folder_creates_uv_lock(self, mock_run, temp_dirs):
        """Test that pack_folder creates uv.lock if it doesn't exist."""
        project_dir, wrap_dir = temp_dirs

        config = MagicMock(spec=Config)
        config.get.side_effect = lambda section, key, default=None: {
            ('uv', 'project_dir'): project_dir,
            ('uv', 'wrap_dir'): wrap_dir
        }.get((section, key), default)

        # Create a test project without uv.lock
        robot_dir = Path(project_dir) / "example-robot"
        robot_dir.mkdir(parents=True)
        (robot_dir / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '0.1.0'")
        (robot_dir / "main.py").write_text("print('hello')")

        mock_run.return_value = MagicMock(returncode=0)

        packer = ProjectPacker(config)
        result = packer.pack_folder(robot_dir / "pyproject.toml")

        # Check that uv lock was called
        lock_calls = [call for call in mock_run.call_args_list if len(call[0][0]) >= 2 and call[0][0][0:2] == ['uv', 'lock']]
        assert len(lock_calls) > 0, "uv lock should have been called"


class TestProjectPackerPackAll:
    """Tests for pack_all method."""

    @pytest.fixture
    def temp_dirs_for_pack_all(self):
        """Create temporary directories for pack_all testing."""
        with TemporaryDirectory() as project_dir:
            with TemporaryDirectory() as wrap_dir:
                yield project_dir, wrap_dir

    def test_pack_all_finds_pyproject_toml(self, temp_dirs_for_pack_all):
        """Test that pack_all finds and processes all pyproject.toml files."""
        project_dir, wrap_dir = temp_dirs_for_pack_all

        config = MagicMock(spec=Config)
        config.get.side_effect = lambda section, key, default=None: {
            ('uv', 'project_dir'): project_dir,
            ('uv', 'wrap_dir'): wrap_dir
        }.get((section, key), default)

        # Create multiple test projects
        for robot_name in ["robot1", "robot2", "subdir/robot3"]:
            robot_dir = Path(project_dir) / robot_name
            robot_dir.mkdir(parents=True, exist_ok=True)
            (robot_dir / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '0.1.0'")
            (robot_dir / "main.py").write_text("print('hello')")

        packer = ProjectPacker(config)
        
        with patch.object(packer, 'pack_folder') as mock_pack:
            mock_pack.return_value = Path(wrap_dir) / "dummy.zip"
            packer.pack_all(Path(project_dir))

            # Should be called 3 times (once per robot)
            assert mock_pack.call_count == 3
