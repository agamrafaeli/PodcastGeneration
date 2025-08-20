#!/usr/bin/env python3
"""
Test helper functions for audio validation and common test patterns
Consolidates validation logic to avoid duplication across test files
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

from engines.utils.validation import validate_audio_file, ValidationConfig


def get_test_mode() -> str:
    """
    Get the current test mode from environment variables.
    
    Returns:
        str: 'mock', 'real', or 'hybrid' based on TEST_MODE or USE_REAL_ENGINES
    """
    test_mode = os.getenv('TEST_MODE', '').lower()
    if test_mode in ['mock', 'real', 'hybrid']:
        return test_mode
    
    # Fallback to legacy USE_REAL_ENGINES for backward compatibility
    if os.getenv('USE_REAL_ENGINES', 'false').lower() == 'true':
        return 'real'
    return 'mock'


def should_use_real_engines() -> bool:
    """
    Determine if tests should use real engines based on test mode.
    
    Returns:
        bool: True if real engines should be used
    """
    return get_test_mode() == 'real'


def should_use_mock_engines() -> bool:
    """
    Determine if tests should use mock engines based on test mode.
    
    Returns:
        bool: True if mock engines should be used
    """
    return get_test_mode() in ['mock', 'hybrid']


def assert_valid_audio_file(
    file_path: Union[str, Path], 
    min_duration_seconds: float = 0.1,
    max_duration_seconds: Optional[float] = None,
    min_file_size_bytes: int = 50,
    error_prefix: str = "Audio validation failed"
) -> None:
    """
    Assert that an audio file passes validation with given criteria
    
    Args:
        file_path: Path to audio file to validate
        min_duration_seconds: Minimum required duration (default: 0.1s)
        max_duration_seconds: Maximum allowed duration (None = no limit)
        min_file_size_bytes: Minimum required file size (default: 50 bytes)
        error_prefix: Prefix for error messages
        
    Raises:
        AssertionError: If validation fails
    """
    file_path = Path(file_path)
    
    config = ValidationConfig(
        min_duration_seconds=min_duration_seconds,
        max_duration_seconds=max_duration_seconds,
        min_file_size_bytes=min_file_size_bytes,
        require_metadata=False  # Don't require metadata for tests
    )
    
    validation_result = validate_audio_file(file_path, config)
    
    if not validation_result.is_valid:
        error_details = "; ".join(validation_result.errors)
        raise AssertionError(f"{error_prefix}: {error_details}")


def get_audio_validation_info(file_path: Union[str, Path]) -> str:
    """
    Get human-readable validation info for an audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        String with file size and duration info for logging
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return f"❌ File does not exist: {file_path}"
    
    validation_result = validate_audio_file(file_path)
    
    size_mb = file_path.stat().st_size / 1024 / 1024
    if size_mb >= 1:
        size_str = f"{size_mb:.1f}MB"
    else:
        size_str = f"{file_path.stat().st_size:,} bytes"
    
    if validation_result.duration_seconds:
        duration_str = f" ({validation_result.duration_seconds:.1f}s)"
    else:
        duration_str = ""
    
    status = "✅" if validation_result.is_valid else "❌"
    return f"{status} {size_str}{duration_str}"


def validate_audio_and_print_info(
    file_path: Union[str, Path],
    min_duration_seconds: float = 0.1,
    min_file_size_bytes: int = 50,
    test_name: str = "Audio"
) -> bool:
    """
    Validate audio file and print informative output
    
    Args:
        file_path: Path to audio file
        min_duration_seconds: Minimum duration requirement
        min_file_size_bytes: Minimum file size requirement
        test_name: Name for logging (e.g., "Generated audio", "Consolidated file")
        
    Returns:
        bool: True if validation passed, False otherwise
    """
    try:
        assert_valid_audio_file(
            file_path,
            min_duration_seconds=min_duration_seconds,
            min_file_size_bytes=min_file_size_bytes,
            error_prefix=f"{test_name} validation failed"
        )
        
        info = get_audio_validation_info(file_path)
        print(f"🔊 {test_name}: {info}")
        return True
        
    except AssertionError as e:
        print(f"❌ {test_name} validation failed: {e}")
        return False


class AudioValidationPresets:
    """Preset configurations for common audio validation scenarios"""
    
    @staticmethod
    def quick_test() -> dict:
        """Minimal validation for quick tests"""
        return {
            "min_duration_seconds": 0.1,
            "min_file_size_bytes": 50
        }
    
    @staticmethod
    def short_audio() -> dict:
        """Validation for short audio clips (1-10 seconds)"""
        return {
            "min_duration_seconds": 0.5,
            "max_duration_seconds": 15.0,
            "min_file_size_bytes": 500
        }
    
    @staticmethod
    def medium_audio() -> dict:
        """Validation for medium audio clips (5-60 seconds)"""
        return {
            "min_duration_seconds": 1.0,
            "max_duration_seconds": 90.0,
            "min_file_size_bytes": 1000
        }
    
    @staticmethod
    def long_audio() -> dict:
        """Validation for longer audio clips (10+ seconds)"""
        return {
            "min_duration_seconds": 5.0,
            "min_file_size_bytes": 3000
        }
    
    @staticmethod
    def consolidated_sample() -> dict:
        """Validation for consolidated voice samples"""
        return {
            "min_duration_seconds": 2.0,
            "min_file_size_bytes": 2000
        }


def assert_valid_audio_with_preset(file_path: Union[str, Path], preset_name: str) -> None:
    """
    Validate audio using a preset configuration
    
    Args:
        file_path: Path to audio file
        preset_name: Name of preset ('quick_test', 'short_audio', 'medium_audio', 'long_audio', 'consolidated_sample')
    """
    preset_method = getattr(AudioValidationPresets, preset_name, None)
    if not preset_method:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    preset_config = preset_method()
    assert_valid_audio_file(file_path, **preset_config)
