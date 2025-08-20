#!/usr/bin/env python3
"""
Simplified pytest configuration with modular fixture organization
Clean, maintainable test configuration using organized fixture modules
"""

# Import all fixtures from organized modules
from .fixtures.sdk_fixtures import *
from .fixtures.temp_fixtures import *
from .fixtures.sample_fixtures import *

# Import pytest hooks for parallel execution
from .hooks.parallel_hooks import *
