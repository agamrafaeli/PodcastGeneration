#!/usr/bin/env python3
"""
SDK and engine fixtures for test sessions
Provides session-scoped SDK instances and mock engines
"""

import pytest
import sys
from pathlib import Path

from tts.sdk import TTSSDK
from tests.mocks import MockTTSSDK, MockEngineFactory
from tests.test_helpers import should_use_mock_engines, get_test_mode


@pytest.fixture(scope="session")
def session_sdk():
    """
    Session-scoped SDK instance - automatically uses mock or real engines
    Shared across all tests to reduce initialization overhead
    """
    if should_use_mock_engines():
        print(f"🎭 Session SDK: Using MOCK engines (TEST_MODE={get_test_mode()})")
        sdk = MockTTSSDK(timeout=60.0)
    else:
        print(f"🎤 Session SDK: Using REAL engines (TEST_MODE={get_test_mode()})")
        sdk = TTSSDK(timeout=60.0)
    
    yield sdk
    # No explicit cleanup needed


@pytest.fixture(scope="session") 
def session_mock_engines():
    """
    Session-scoped mock engines - shared across all mock-based tests
    Avoids repeated creation of mock engine instances
    """
    engines = MockEngineFactory.get_all_mock_engines()
    print(f"🏭 Session mock engines: {list(engines.keys())}")
    return engines


@pytest.fixture(scope="function")
def worker_sdk(session_sdk):
    """
    Worker-safe SDK instance for tests that need isolation
    Creates individual instances when needed to avoid state conflicts
    """
    if should_use_mock_engines():
        return MockTTSSDK(timeout=30.0)
    else:
        return TTSSDK(timeout=30.0)
