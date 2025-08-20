# Testing Guide

Comprehensive testing strategy for the TTS system supporting three engines: edge_tts, gtts, and pyttsx3.

## Test Strategy Overview

The test suite is designed with two main approaches:
- **Mock Tests**: Fast, reliable tests using simulated engines (recommended for development)
- **Real Engine Tests**: Integration tests with actual TTS providers (for validation)

## Quick Start

Before running any tests, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

The test suite automatically adds the `src` directory to `PYTHONPATH`, so no additional package installation is required.

**Development Testing (Recommended)**
```bash
# Fast mock tests - use during development
python -m pytest tests/ -v
```

**Integration Testing**
```bash
# All tests with real engines - slower but comprehensive
USE_REAL_ENGINES=true python -m pytest tests/ -v
```

## Test Categories

### Mock Tests (Fast & Reliable)

Mock tests simulate engine behavior locally, providing:
- ✅ **Fast execution** - no network dependencies
- ✅ **Deterministic results** - consistent across environments  
- ✅ **No external dependencies** - work offline

```bash
# All mock tests
python -m pytest tests/ -v

# Specific mock integration tests
python -m pytest tests/test_voice_mock_integration.py -v

# Mock engine behavior tests
python -m pytest tests/test_invalid_voice_error.py -v
```

### Real Engine Tests (Integration)

Real engine tests interact with actual TTS providers:
- ⚠️ **Network required** - need internet connectivity
- ⚠️ **Variable performance** - dependent on service availability
- ⚠️ **Platform-specific** - may have OS dependencies

```bash
# All real engine tests
USE_REAL_ENGINES=true python -m pytest tests/ -v

# Voice consistency across all engines
USE_REAL_ENGINES=true python -m pytest tests/test_voice_consistency_across_engines.py -v

# Real engine spot checks
python -m pytest tests/test_voice_real_engine_spot_check.py -v

# End-to-end tests
python -m pytest tests/test_offline_e2e.py -v
python -m pytest tests/test_voice_sample_e2e.py -v
```

### Specialized Tests

```bash
# Random voice selection testing
python -m pytest tests/test_random_voices_across_engines.py -v

# Test helper utilities
python -m pytest tests/test_helpers.py -v
```

## Development Workflow

### 1. Development Phase
```bash
# Quick feedback during active development
python -m pytest tests/test_voice_mock_integration.py -v
```

### 2. Pre-commit Testing
```bash
# Comprehensive mock testing before commits
python -m pytest tests/ -v
```

### 3. Pre-release Validation
```bash
# Full integration testing before releases
USE_REAL_ENGINES=true python -m pytest tests/ -v
```

## Test File Structure

```
tests/
├── conftest.py                           # Test configuration and fixtures
├── fixtures/                            # Test data and helper fixtures
│   ├── sample_fixtures.py               # Sample text and audio fixtures
│   ├── sdk_fixtures.py                  # SDK-specific test fixtures  
│   └── temp_fixtures.py                 # Temporary test data
├── hooks/                              # Test execution hooks
│   └── parallel_hooks.py               # Parallel test execution setup
├── mocks/                              # Mock implementations
│   ├── engine.py                       # Mock TTS engines
│   └── sdk.py                          # Mock SDK components
├── test_helpers.py                      # Utility functions for tests
├── test_invalid_voice_error.py          # Error handling validation
├── test_offline_e2e.py                  # End-to-end offline tests
├── test_random_voices_across_engines.py # Random voice selection tests
├── test_voice_consistency_across_engines.py # Cross-engine consistency
├── test_voice_mock_integration.py       # Mock integration tests
├── test_voice_real_engine_spot_check.py # Real engine validation
└── test_voice_sample_e2e.py            # Voice sample generation tests
```

## Running Specific Engine Tests

```bash
# Test only edge_tts integration
USE_REAL_ENGINES=true python -c "
import pytest
pytest.main(['-v', '-k', 'edge_tts', 'tests/'])
"

# Test only gtts integration  
USE_REAL_ENGINES=true python -c "
import pytest
pytest.main(['-v', '-k', 'gtts', 'tests/'])
"

# Test only pyttsx3 integration
USE_REAL_ENGINES=true python -c "
import pytest
pytest.main(['-v', '-k', 'pyttsx3', 'tests/'])
"
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `USE_REAL_ENGINES` | Enable real engine testing | `USE_REAL_ENGINES=true` |
| `PYTEST_VERBOSE` | Increase test verbosity | `PYTEST_VERBOSE=1` |

## Troubleshooting

### Common Issues

**Mock tests failing:**
- Ensure all dependencies are installed: `pip install -r requirements-dev.txt`
- Check Python version compatibility (3.7+)

**Real engine tests failing:**
- Verify internet connectivity
- Check if TTS services are accessible in your region
- Ensure all engine-specific dependencies are installed

**Slow test execution:**
- Use mock tests for development: `python -m pytest tests/test_voice_mock_integration.py`
- Run specific test files instead of the entire suite
- Consider parallel execution with `pytest-xdist`

For more detailed troubleshooting, see the main [README.md](README.md).
