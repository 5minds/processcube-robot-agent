"""Tests for work items processing framework."""

from unittest.mock import MagicMock, patch, call

import pytest
from processcube_sdk.external_tasks import FunctionalError

from processcube_robot_agent.tools import process_work_items


class TestWorkItemsProcessing:
    """Tests for process_work_items framework."""
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_single_work_item(self, mock_outputs, mock_inputs):
        """Test processing a single work item."""
        # Setup mocks
        mock_input_item = MagicMock()
        mock_input_item.payload = {"data": "test"}
        mock_inputs.__iter__.return_value = [mock_input_item]
        
        mock_output_item = MagicMock()
        mock_outputs.create.return_value = mock_output_item
        
        # Define processor
        def processor(payload):
            return {"status": "success", "result": payload["data"]}
        
        # Process
        process_work_items(processor)
        
        # Verify outputs were created and saved
        mock_outputs.create.assert_called_once()
        mock_output_item.save.assert_called_once()
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_multiple_work_items(self, mock_outputs, mock_inputs):
        """Test processing multiple work items."""
        # Setup mocks
        mock_input_items = [
            MagicMock(payload={"id": 1}),
            MagicMock(payload={"id": 2}),
            MagicMock(payload={"id": 3}),
        ]
        mock_inputs.__iter__.return_value = mock_input_items
        
        mock_output_item = MagicMock()
        mock_outputs.create.return_value = mock_output_item
        
        # Define processor
        def processor(payload):
            return {"status": "success", "id": payload["id"]}
        
        # Process
        process_work_items(processor)
        
        # Verify all items were processed
        assert mock_outputs.create.call_count == 3
        assert mock_output_item.save.call_count == 3
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_with_functional_error(self, mock_outputs, mock_inputs):
        """Test handling FunctionalError from processor."""
        # Setup mocks
        mock_input_item = MagicMock()
        mock_input_item.payload = {"data": "test"}
        mock_inputs.__iter__.return_value = [mock_input_item]
        
        mock_output_item = MagicMock()
        mock_outputs.create.return_value = mock_output_item
        
        # Define processor that raises FunctionalError
        def processor(payload):
            raise FunctionalError("TEST_ERROR", "Test error message")
        
        # Process and verify FunctionalError is re-raised
        with pytest.raises(FunctionalError) as exc_info:
            process_work_items(processor)
        
        assert exc_info.value.get_code() == "TEST_ERROR"
        # Error output should be created before re-raising
        mock_outputs.create.assert_called()
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_with_exception_continues(self, mock_outputs, mock_inputs):
        """Test that non-FunctionalError exceptions allow continuation."""
        # Setup mocks
        mock_input_items = [
            MagicMock(payload={"id": 1}),
            MagicMock(payload={"id": 2}),
        ]
        mock_inputs.__iter__.return_value = mock_input_items
        
        mock_output_item = MagicMock()
        mock_outputs.create.return_value = mock_output_item
        
        call_count = [0]
        
        # Define processor that raises exception on first call
        def processor(payload):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Recoverable error")
            return {"status": "success"}
        
        # Process - should not raise, should continue
        process_work_items(processor)
        
        # Both items should have output created (one with error, one with success)
        assert mock_outputs.create.call_count == 2
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_no_input_items(self, mock_outputs, mock_inputs):
        """Test processing when no input items exist."""
        # Setup mocks
        mock_inputs.__iter__.return_value = []
        
        # Define processor
        def processor(payload):
            return {"status": "success"}
        
        # Process - should handle gracefully
        process_work_items(processor)
        
        # No outputs should be created
        mock_outputs.create.assert_not_called()
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_output_save_failure(self, mock_outputs, mock_inputs):
        """Test handling when output save fails."""
        # Setup mocks
        mock_input_item = MagicMock()
        mock_input_item.payload = {"data": "test"}
        mock_inputs.__iter__.return_value = [mock_input_item]
        
        mock_output_item = MagicMock()
        mock_output_item.save.side_effect = Exception("Save failed")
        mock_outputs.create.return_value = mock_output_item
        
        # Define processor
        def processor(payload):
            return {"status": "success"}
        
        # Process - should handle save failure gracefully
        process_work_items(processor)
        
        # Output should have been created even though save failed
        mock_outputs.create.assert_called()
    
    @patch('processcube_robot_agent.tools.work_items.inputs')
    @patch('processcube_robot_agent.tools.work_items.outputs')
    def test_process_functional_error_output_failure(self, mock_outputs, mock_inputs):
        """Test handling when FunctionalError output save fails."""
        # Setup mocks
        mock_input_item = MagicMock()
        mock_input_item.payload = {"data": "test"}
        mock_inputs.__iter__.return_value = [mock_input_item]
        
        mock_output_item = MagicMock()
        mock_output_item.save.side_effect = Exception("Save failed")
        mock_outputs.create.return_value = mock_output_item
        
        # Define processor that raises FunctionalError
        def processor(payload):
            raise FunctionalError("TEST_ERROR", "Test error")
        
        # Process and verify FunctionalError is re-raised even if save fails
        with pytest.raises(FunctionalError) as exc_info:
            process_work_items(processor)
        
        assert exc_info.value.get_code() == "TEST_ERROR"
