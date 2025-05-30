# Copyright 2025 Amazon.com, Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for the Streamlit webapp functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# Add the webapp directory to the path so we can import from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'webapp')))

# Import the modules we want to test
from content_accessibility_utility_on_aws.utils.usage_tracker import SessionUsageTracker


class TestWebApp(unittest.TestCase):
    """Test cases for the webapp functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the singleton instance before each test
        SessionUsageTracker._instance = None
        
        # Create a mock for streamlit
        self.st_mock = MagicMock()
        sys.modules['streamlit'] = self.st_mock
        
        # Create a mock for the session state
        self.session_state_mock = MagicMock()
        self.st_mock.session_state = self.session_state_mock

    @patch('webapp.utils.file_utils.detect_file_type')
    @patch('webapp.utils.file_utils.save_uploaded_file')
    @patch('webapp.utils.session_utils.SessionState.create_temp_dir')
    @patch('webapp.processors.pdf_processor.process_pdf_file')
    @patch('webapp.utils.session_utils.SessionState.save_results')
    def test_process_uploaded_file_resets_usage_tracker(
        self, mock_save_results, mock_process_pdf, mock_create_temp_dir, 
        mock_save_uploaded_file, mock_detect_file_type
    ):
        """Test that process_uploaded_file resets the usage tracker."""
        # Import here to use the mocked streamlit
        from webapp.app import process_uploaded_file
        
        # Set up the mocks
        mock_detect_file_type.return_value = "pdf"
        mock_create_temp_dir.return_value = "/tmp/test_dir"
        mock_save_uploaded_file.return_value = "/tmp/test_dir/test.pdf"
        mock_process_pdf.return_value = (True, {"test": "result"})
        
        # Create a mock uploaded file
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "test.pdf"
        
        # Create a mock config
        mock_config = MagicMock()
        
        # Add some usage data to the tracker
        tracker = SessionUsageTracker.get_instance()
        tracker.track_bedrock_call("model1", "test", 100, 50)
        self.assertEqual(tracker.bedrock_usage["total_calls"], 1)
        
        # Call the function under test with appropriate patches
        with patch('webapp.app.app_config', mock_config):
            process_uploaded_file(mock_uploaded_file, {})
        
        # Verify the usage tracker was reset
        tracker = SessionUsageTracker.get_instance()
        self.assertEqual(tracker.bedrock_usage["total_calls"], 0)
        
        # Verify the mocks were called as expected
        mock_detect_file_type.assert_called_once_with("test.pdf")
        mock_create_temp_dir.assert_called_once()
        mock_save_uploaded_file.assert_called_once_with(mock_uploaded_file, "/tmp/test_dir")
        mock_process_pdf.assert_called_once()
        mock_save_results.assert_called_once_with({"test": "result"})


if __name__ == "__main__":
    unittest.main()