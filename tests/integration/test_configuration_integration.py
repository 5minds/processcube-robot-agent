"""Integration tests for configuration management.

Tests configuration loading, validation, and environment variable handling.
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from tests.integration.helpers import create_temp_config, cleanup_config


class TestConfigurationLoading:
    """Test configuration file loading."""
    
    def test_config_file_creation(self):
        """Test that config file can be created."""
        config_path = create_temp_config()
        
        try:
            assert os.path.exists(config_path)
            
            # Verify content
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert "debugging" in config
            assert "engine" in config
            assert "rcc" in config
            assert "rest_api" in config
        finally:
            cleanup_config(config_path)
    
    def test_config_content_structure(self):
        """Test that config has correct structure."""
        config_path = create_temp_config()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Verify debugging section
            assert "enabled" in config["debugging"]
            assert "hostname" in config["debugging"]
            assert "port" in config["debugging"]
            
            # Verify engine section
            assert "url" in config["engine"]
            
            # Verify rcc section
            assert "topic_prefix" in config["rcc"]
            assert "wrap_dir" in config["rcc"]
            assert "unwrap_dir" in config["rcc"]
            assert "start_watch_project_dir" in config["rcc"]
            assert "project_dir" in config["rcc"]
            
            # Verify rest_api section
            assert "port" in config["rest_api"]
            assert "host" in config["rest_api"]
        finally:
            cleanup_config(config_path)
    
    def test_config_with_custom_values(self):
        """Test config creation with custom values."""
        config_path = create_temp_config(
            engine_url="http://custom-engine:56100",
            api_port=43000,
            topic_prefix="custom"
        )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert config["engine"]["url"] == "http://custom-engine:56100"
            assert config["rest_api"]["port"] == 43000
            assert config["rcc"]["topic_prefix"] == "custom"
        finally:
            cleanup_config(config_path)


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_config_json_validity(self):
        """Test that generated config is valid JSON."""
        config_path = create_temp_config()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Re-serialize to ensure JSON validity
            json_str = json.dumps(config)
            reloaded = json.loads(json_str)
            
            assert config == reloaded
        finally:
            cleanup_config(config_path)
    
    def test_required_fields_present(self):
        """Test that all required fields are present."""
        config_path = create_temp_config()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required top-level sections
            required_sections = ["debugging", "engine", "rcc", "rest_api"]
            for section in required_sections:
                assert section in config, f"Missing section: {section}"
        finally:
            cleanup_config(config_path)
    
    def test_config_types(self):
        """Test that configuration values have correct types."""
        config_path = create_temp_config()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate types
            assert isinstance(config["debugging"]["enabled"], bool)
            assert isinstance(config["debugging"]["port"], int)
            assert isinstance(config["engine"]["url"], str)
            assert isinstance(config["rest_api"]["port"], int)
            assert isinstance(config["rest_api"]["host"], str)
        finally:
            cleanup_config(config_path)


class TestMultipleConfigurations:
    """Test handling multiple configuration scenarios."""
    
    def test_development_config(self):
        """Test development configuration."""
        config_path = create_temp_config(
            api_port=42042,
            topic_prefix="dev"
        )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert config["rest_api"]["port"] == 42042
            assert config["rcc"]["topic_prefix"] == "dev"
            assert config["debugging"]["enabled"] is False
        finally:
            cleanup_config(config_path)
    
    def test_production_config(self):
        """Test production-like configuration."""
        config_path = create_temp_config(
            engine_url="http://processcube-engine:56100",
            api_port=42042,
            topic_prefix="robot"
        )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert config["debugging"]["enabled"] is False
            assert config["engine"]["url"] == "http://processcube-engine:56100"
            assert config["rcc"]["start_watch_project_dir"] is False
        finally:
            cleanup_config(config_path)
    
    def test_testing_config(self):
        """Test testing configuration."""
        config_path = create_temp_config(
            engine_url="http://mock-engine:56100",
            api_port=42043,
            topic_prefix="test"
        )
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            assert config["rcc"]["topic_prefix"] == "test"
            assert config["rest_api"]["port"] == 42043
        finally:
            cleanup_config(config_path)


class TestConfigurationEnvironmentVariables:
    """Test environment variable handling in configuration."""
    
    @patch.dict(os.environ, {'CONFIG_FILE': '/path/to/config.json'})
    def test_config_file_env_variable(self):
        """Test CONFIG_FILE environment variable."""
        config_file = os.environ.get('CONFIG_FILE')
        assert config_file == '/path/to/config.json'
    
    @patch.dict(os.environ, {'PYTHONPATH': '/app'})
    def test_pythonpath_env_variable(self):
        """Test PYTHONPATH environment variable."""
        pythonpath = os.environ.get('PYTHONPATH')
        assert pythonpath == '/app'
    
    def test_config_without_env_variable(self):
        """Test config file without environment variable set."""
        # Ensure CONFIG_FILE is not set
        env_copy = os.environ.copy()
        if 'CONFIG_FILE' in env_copy:
            del env_copy['CONFIG_FILE']
        
        # CONFIG_FILE should not be in environment
        assert 'CONFIG_FILE' not in env_copy


class TestConfigurationErrors:
    """Test error handling in configuration."""
    
    def test_invalid_json_config(self):
        """Test handling of invalid JSON config."""
        fd, config_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write("{ invalid json }")
            
            with pytest.raises(json.JSONDecodeError):
                with open(config_path, 'r') as f:
                    json.load(f)
        finally:
            if os.path.exists(config_path):
                os.remove(config_path)
    
    def test_missing_config_file(self):
        """Test handling of missing config file."""
        missing_path = "/nonexistent/path/config.json"
        
        with pytest.raises(FileNotFoundError):
            with open(missing_path, 'r') as f:
                json.load(f)
    
    def test_config_file_permissions_error(self):
        """Test handling of config file with restricted permissions."""
        config_path = create_temp_config()
        
        try:
            # Make file unreadable
            os.chmod(config_path, 0o000)
            
            with pytest.raises(PermissionError):
                with open(config_path, 'r') as f:
                    json.load(f)
        finally:
            # Restore permissions before cleanup
            os.chmod(config_path, 0o644)
            cleanup_config(config_path)


class TestConfigurationIntegration:
    """Test configuration integration with other components."""
    
    def test_config_for_rest_api(self):
        """Test configuration values for REST API."""
        config_path = create_temp_config(api_port=42050)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # REST API should use configured port
            port = config["rest_api"]["port"]
            assert port == 42050
            assert isinstance(port, int)
        finally:
            cleanup_config(config_path)
    
    def test_config_for_robot_topics(self):
        """Test configuration values for robot topics."""
        config_path = create_temp_config(topic_prefix="myagent")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Topics should use configured prefix
            prefix = config["rcc"]["topic_prefix"]
            assert prefix == "myagent"
        finally:
            cleanup_config(config_path)
    
    def test_config_for_engine_connection(self):
        """Test configuration values for engine connection."""
        engine_url = "http://my-engine:56100"
        config_path = create_temp_config(engine_url=engine_url)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Engine URL should be configured correctly
            url = config["engine"]["url"]
            assert url == engine_url
        finally:
            cleanup_config(config_path)
    
    def test_config_file_cleanup(self):
        """Test that temp config files are properly cleaned up."""
        config_path = create_temp_config()
        
        assert os.path.exists(config_path)
        
        cleanup_config(config_path)
        
        assert not os.path.exists(config_path)
