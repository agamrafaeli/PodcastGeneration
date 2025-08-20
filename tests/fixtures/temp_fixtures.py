#!/usr/bin/env python3
"""
Temporary directory fixtures for tests.
Provides worker-isolated directories that are cleaned up after use.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def isolated_temp_dir():
    """Create an isolated temporary directory for a test.

    Uses the worker-specific base directory configured by the pytest
    hooks (``PYTEST_TMP_DIR``) when available so parallel test runs do
    not interfere with each other. The directory is removed after the
    test finishes.
    """
    base_dir = Path(os.environ.get("PYTEST_TMP_DIR", tempfile.gettempdir()))
    temp_dir = Path(tempfile.mkdtemp(prefix="tts_test_", dir=base_dir))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
