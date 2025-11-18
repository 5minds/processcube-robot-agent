"""Tests for error handlers tool."""

import pytest
from processcube_sdk.external_tasks import FunctionalError

from processcube_robot_agent.tools import (
    raise_robot_test_failed,
    raise_robot_execution_error,
    raise_functional_error,
)


class TestErrorHandlers:
    """Tests for error handling functions."""
    
    def test_raise_robot_test_failed(self):
        """Test raising robot test failed error."""
        with pytest.raises(FunctionalError) as exc_info:
            raise_robot_test_failed("test.robot", 1)
        
        error = exc_info.value
        assert error.get_code() == "ROBOT_TESTS_FAILED"
        assert "test.robot" in error.get_message()
        assert "return code: 1" in error.get_message()
    
    def test_raise_robot_test_failed_with_details(self):
        """Test raising robot test failed error with details."""
        with pytest.raises(FunctionalError) as exc_info:
            raise_robot_test_failed("test.robot", 1, "Test timeout")
        
        error = exc_info.value
        assert error.get_code() == "ROBOT_TESTS_FAILED"
        assert "Test timeout" in error.get_message()
    
    def test_raise_robot_execution_error(self):
        """Test raising robot execution error."""
        with pytest.raises(FunctionalError) as exc_info:
            raise_robot_execution_error("Robot not found")
        
        error = exc_info.value
        assert error.get_code() == "ROBOT_EXECUTION_ERROR"
        assert "Robot not found" in error.get_message()
    
    def test_raise_robot_execution_error_with_file(self):
        """Test raising robot execution error with file."""
        with pytest.raises(FunctionalError) as exc_info:
            raise_robot_execution_error("File not found", "test.robot")
        
        error = exc_info.value
        assert error.get_code() == "ROBOT_EXECUTION_ERROR"
        assert "test.robot" in error.get_message()
        assert "File not found" in error.get_message()
    
    def test_raise_functional_error(self):
        """Test raising custom functional error."""
        with pytest.raises(FunctionalError) as exc_info:
            raise_functional_error("CUSTOM_ERROR", "Custom error message")
        
        error = exc_info.value
        assert error.get_code() == "CUSTOM_ERROR"
        assert error.get_message() == "Custom error message"
    
    def test_raise_functional_error_custom_codes(self):
        """Test raising functional error with various custom codes."""
        custom_codes = [
            "INVALID_INPUT",
            "API_FAILED",
            "VALIDATION_ERROR",
            "TIMEOUT",
        ]
        
        for code in custom_codes:
            with pytest.raises(FunctionalError) as exc_info:
                raise_functional_error(code, "Test message")
            
            error = exc_info.value
            assert error.get_code() == code
