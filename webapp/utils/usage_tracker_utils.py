# Copyright 2025 Amazon.com, Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0

"""
Usage tracker utilities for Streamlit webapp.

This module provides utilities to manage session-specific usage tracking in the Streamlit webapp.
"""

import sys
import os

# Add the parent directory to sys.path so we can import from content_accessibility_utility_on_aws
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from content_accessibility_utility_on_aws.utils.usage_tracker import SessionUsageTracker
from .session_utils import SessionState


def get_session_usage_tracker() -> SessionUsageTracker:
    """
    Get the usage tracker for the current Streamlit session.
    
    Returns:
        SessionUsageTracker: Session-specific usage tracker instance
    """
    session_id = SessionState.get_session_id()
    return SessionUsageTracker.get_instance(session_id)


def clear_session_usage_tracker() -> None:
    """Clear the usage tracker for the current Streamlit session."""
    session_id = SessionState.get_session_id()
    SessionUsageTracker.clear_session(session_id)


def reset_session_processing() -> None:
    """
    Reset session processing state and clear usage tracking.
    
    This should be called when starting a new processing session.
    """
    # Clear the current session's usage tracker
    clear_session_usage_tracker()
    
    # Reset processing state
    SessionState.set(SessionState.PROCESSING_COMPLETE_KEY, False)
    SessionState.set(SessionState.RESULTS_KEY, None)
    SessionState.set(SessionState.HTML_PATH_KEY, None)
    SessionState.set(SessionState.AUDIT_RESULTS_KEY, None)
    SessionState.set(SessionState.REMEDIATED_PATH_KEY, None)