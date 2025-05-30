# Copyright 2025 Amazon.com, Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for the usage tracker module.
"""

import unittest
from datetime import datetime
from content_accessibility_utility_on_aws.utils.usage_tracker import SessionUsageTracker


class TestUsageTracker(unittest.TestCase):
    """Test cases for the SessionUsageTracker class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the singleton instance before each test
        SessionUsageTracker._instance = None

    def test_singleton_pattern(self):
        """Test that get_instance returns the same instance."""
        tracker1 = SessionUsageTracker.get_instance()
        tracker2 = SessionUsageTracker.get_instance()
        self.assertIs(tracker1, tracker2, "get_instance should return the same instance")

    def test_reset_instance(self):
        """Test that reset_instance creates a new instance."""
        tracker1 = SessionUsageTracker.get_instance()
        # Track some usage to modify the state
        tracker1.track_bedrock_call("model1", "test", 100, 50)
        self.assertEqual(tracker1.bedrock_usage["total_calls"], 1)
        
        # Reset the instance
        tracker2 = SessionUsageTracker.reset_instance()
        # Verify it's a new instance with fresh state
        self.assertEqual(tracker2.bedrock_usage["total_calls"], 0)
        # Verify get_instance returns the new instance
        tracker3 = SessionUsageTracker.get_instance()
        self.assertIs(tracker2, tracker3)

    def test_track_bedrock_call(self):
        """Test tracking Bedrock API calls."""
        tracker = SessionUsageTracker.get_instance()
        tracker.track_bedrock_call("model1", "test", 100, 50)
        
        self.assertEqual(tracker.bedrock_usage["total_calls"], 1)
        self.assertEqual(tracker.bedrock_usage["total_input_tokens"], 100)
        self.assertEqual(tracker.bedrock_usage["total_output_tokens"], 50)
        self.assertEqual(tracker.bedrock_usage["calls_by_model"]["model1"]["total_calls"], 1)
        self.assertEqual(tracker.bedrock_usage["calls_by_purpose"]["test"]["total_calls"], 1)

    def test_track_bda_processing(self):
        """Test tracking BDA document processing."""
        tracker = SessionUsageTracker.get_instance()
        tracker.track_bda_processing("arn:aws:bda:project", "doc1", 10)
        
        self.assertEqual(tracker.bda_usage["total_documents_processed"], 1)
        self.assertEqual(tracker.bda_usage["total_pages_processed"], 10)
        self.assertEqual(tracker.bda_usage["project_arn"], "arn:aws:bda:project")
        self.assertEqual(len(tracker.bda_usage["processing_details"]), 1)
        self.assertEqual(tracker.bda_usage["processing_details"][0]["document_id"], "doc1")

    def test_finalize_session(self):
        """Test finalizing a session."""
        tracker = SessionUsageTracker.get_instance()
        # Ensure end_time is None initially
        tracker.end_time = None
        tracker.finalize_session()
        self.assertIsNotNone(tracker.end_time)
        self.assertIsInstance(tracker.end_time, datetime)

    def test_get_usage_data(self):
        """Test getting complete usage data."""
        tracker = SessionUsageTracker.get_instance()
        tracker.track_bedrock_call("model1", "test", 100, 50)
        tracker.track_bda_processing("arn:aws:bda:project", "doc1", 10)
        
        usage_data = tracker.get_usage_data()
        
        self.assertIn("session_id", usage_data)
        self.assertIn("start_time", usage_data)
        self.assertIn("end_time", usage_data)
        self.assertIn("bda_usage", usage_data)
        self.assertIn("bedrock_usage", usage_data)
        self.assertEqual(usage_data["bda_usage"]["total_documents_processed"], 1)
        self.assertEqual(usage_data["bedrock_usage"]["total_calls"], 1)

    def test_multiple_document_processing(self):
        """Test usage tracking for multiple document processing sessions."""
        # First document processing
        tracker1 = SessionUsageTracker.reset_instance()
        tracker1.track_bedrock_call("model1", "test", 100, 50)
        tracker1.track_bda_processing("arn:aws:bda:project", "doc1", 10)
        usage_data1 = tracker1.get_usage_data()
        
        # Second document processing (reset tracker)
        tracker2 = SessionUsageTracker.reset_instance()
        tracker2.track_bedrock_call("model2", "test", 200, 100)
        tracker2.track_bda_processing("arn:aws:bda:project", "doc2", 20)
        usage_data2 = tracker2.get_usage_data()
        
        # Verify each session has its own data
        self.assertEqual(usage_data1["bedrock_usage"]["total_input_tokens"], 100)
        self.assertEqual(usage_data1["bda_usage"]["total_pages_processed"], 10)
        
        self.assertEqual(usage_data2["bedrock_usage"]["total_input_tokens"], 200)
        self.assertEqual(usage_data2["bda_usage"]["total_pages_processed"], 20)
        
        # Verify the second session doesn't include data from the first
        self.assertNotIn("model1", usage_data2["bedrock_usage"]["calls_by_model"])
        self.assertEqual(len(usage_data2["bda_usage"]["processing_details"]), 1)
        self.assertEqual(usage_data2["bda_usage"]["processing_details"][0]["document_id"], "doc2")


if __name__ == "__main__":
    unittest.main()