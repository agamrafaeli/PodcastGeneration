#!/usr/bin/env python3
"""
Simplified pytest configuration with modular fixture organization
Clean, maintainable test configuration using organized fixture modules
"""

# Explicitly register pytest-asyncio so async tests have an event loop
# available even when pytest's auto-discovery misses the plugin.
pytest_plugins = ("pytest_asyncio",)

# Import all fixtures from organized modules
from .fixtures.sdk_fixtures import *
from .fixtures.temp_fixtures import *
from .fixtures.sample_fixtures import *

# Import pytest hooks for parallel execution
from .hooks.parallel_hooks import *
