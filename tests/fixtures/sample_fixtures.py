#!/usr/bin/env python3
"""
Sample text fixtures for consistent test data
Provides standardized test texts across all tests
"""

import pytest


@pytest.fixture(scope="session")
def sample_texts():
    """
    Session-scoped sample texts for consistent testing
    Standardized test data to ensure reproducible results
    """
    return {
        "short": "Hello world!",
        "medium": "This is a test sentence for voice comparison across multiple engines.",
        "long": """
        This is a much longer text sample that should be split intelligently across multiple voice samples.
        The system should handle text splitting gracefully and create distinct samples for each voice engine.
        This allows users to compare how different voices handle longer passages and make informed decisions
        about which voice works best for their specific use case and content type.
        """,
        "conversation": "Hello, this is a test conversation. How are you doing today? I'm testing the text-to-speech system.",
        "technical": "The pytest-xdist plugin enables parallel test execution across multiple CPU cores for faster testing."
    }
