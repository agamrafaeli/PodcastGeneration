#!/usr/bin/env python3
"""
Pytest hooks for parallel execution optimization
Configures pytest-xdist for optimal parallel testing
"""

import os
import tempfile
import shutil
from pathlib import Path


def pytest_configure(config):
    """Configure pytest for optimal parallel execution"""
    # Set worker-specific temporary directory to avoid conflicts
    if hasattr(config, 'workerinput'):
        worker_id = config.workerinput['workerid']
        temp_base = Path(tempfile.gettempdir()) / f"tts_worker_{worker_id}"
        temp_base.mkdir(exist_ok=True)
        os.environ['PYTEST_TMP_DIR'] = str(temp_base)


def pytest_unconfigure(config):
    """Cleanup worker-specific resources"""
    if 'PYTEST_TMP_DIR' in os.environ:
        temp_dir = Path(os.environ['PYTEST_TMP_DIR'])
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
        del os.environ['PYTEST_TMP_DIR']


def pytest_collection_modifyitems(config, items):
    """
    Optimize test collection for better parallel distribution
    Groups tests by execution time for balanced worker load
    """
    if config.getoption("-n", default=None):  # Only when running in parallel
        # Sort tests by category for better worker distribution
        def sort_key(item):
            markers = [mark.name for mark in item.iter_markers()]
            if "slow" in markers:
                return (3, item.name)  # Slow tests last
            elif "integration" in markers:
                return (2, item.name)  # Integration tests middle
            elif "unit" in markers:
                return (1, item.name)  # Unit tests first
            else:
                return (2, item.name)  # Default to middle
        
        items[:] = sorted(items, key=sort_key)
