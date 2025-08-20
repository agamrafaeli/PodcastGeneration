"""
Prosody Enhancement Module

Simple prosody system that converts speaking styles to native TTS engine parameters.
No complex SSML - just direct engine parameter optimization.
"""

from prosody.prosody import (
    get_prosody_params, 
    list_styles, 
    get_style_info,
    validate_style,
    validate_intensity
)

__version__ = "0.3.0"
__all__ = [
    "get_prosody_params",
    "list_styles", 
    "get_style_info",
    "validate_style",
    "validate_intensity"
]