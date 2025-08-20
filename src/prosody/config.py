#!/usr/bin/env python3
"""
Prosody Configuration Loader

Loads and manages prosody style and voice calibration configurations
from YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Cache for loaded configurations
_styles_cache: Dict[str, Any] = {}
_calibrations_cache: Dict[str, Any] = {}


def get_config_path() -> Path:
    """Get the path to the prosody config directory"""
    return Path(__file__).parent / "config"


def load_styles() -> Dict[str, Any]:
    """
    Load prosody style configurations from styles.yaml
    
    Returns:
        Dictionary containing style configurations
    """
    global _styles_cache
    
    if _styles_cache:
        return _styles_cache
    
    styles_path = get_config_path() / "styles.yaml"
    
    try:
        with open(styles_path, 'r') as f:
            _styles_cache = yaml.safe_load(f)
        logger.info(f"Loaded prosody styles from {styles_path}")
        return _styles_cache
    except Exception as e:
        logger.error(f"Failed to load prosody styles from {styles_path}: {e}")
        # Return minimal fallback configuration
        return {
            "styles": {
                "conversational": {
                    "description": "Natural conversational style",
                    "parameters": {
                        "rate": "+0%",
                        "pitch": "+0Hz", 
                        "volume": "+0dB",
                        "emphasis_strength": "moderate"
                    }
                }
            },
            "defaults": {
                "style": "conversational",
                "intensity": 3
            },
            "intensity_levels": {
                "1": {"multiplier": 0.3},
                "2": {"multiplier": 0.6},
                "3": {"multiplier": 1.0},
                "4": {"multiplier": 1.4},
                "5": {"multiplier": 2.0}
            }
        }


def load_calibrations() -> Dict[str, Any]:
    """
    Load voice calibration configurations from calibration.yaml
    
    Returns:
        Dictionary containing voice calibration configurations
    """
    global _calibrations_cache
    
    if _calibrations_cache:
        return _calibrations_cache
    
    calibrations_path = get_config_path() / "calibration.yaml"
    
    try:
        with open(calibrations_path, 'r') as f:
            _calibrations_cache = yaml.safe_load(f)
        logger.info(f"Loaded voice calibrations from {calibrations_path}")
        return _calibrations_cache
    except Exception as e:
        logger.error(f"Failed to load voice calibrations from {calibrations_path}: {e}")
        # Return minimal fallback configuration
        return {
            "calibrations": {
                "_default": {
                    "description": "Default calibration for all voices",
                    "adjustments": {
                        "rate_modifier": 1.0,
                        "pitch_modifier": 1.0,
                        "volume_modifier": 1.0,
                        "emphasis_modifier": 1.0
                    }
                }
            }
        }


def reload_configs():
    """Reload all configuration files (clears cache)"""
    global _styles_cache, _calibrations_cache
    _styles_cache.clear()
    _calibrations_cache.clear()
    logger.info("Prosody configuration cache cleared")


def get_available_styles() -> list:
    """Get list of available prosody style names"""
    styles_config = load_styles()
    return list(styles_config.get("styles", {}).keys())


def get_style_info(style_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific style"""
    styles_config = load_styles()
    return styles_config.get("styles", {}).get(style_name, {})


def validate_style(style_name: str) -> bool:
    """Check if a style name is valid"""
    return style_name in get_available_styles()


def validate_intensity(intensity: int) -> bool:
    """Check if an intensity level is valid (1-5)"""
    return isinstance(intensity, int) and 1 <= intensity <= 5
