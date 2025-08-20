#!/usr/bin/env python3
"""
Simple Prosody System - Convert styles to native TTS parameters
"""

from typing import Dict, List, Optional
from prosody.config import load_styles


def get_prosody_params(style: str = None, intensity: int = 3) -> Dict[str, str]:
    """
    Convert prosody style and intensity to standard prosody parameters.
    
    Args:
        style: Prosody style name (e.g., "newscast", "dramatic")
        intensity: Intensity level (1-5, where 3 is normal)
        
    Returns:
        Dictionary of standard prosody parameters (e.g., {"rate": "+10%", "pitch": "+5Hz", "volume": "+2dB"})
    """
    if not style:
        return {}
    
    # Load style configuration
    styles_config = load_styles()
    styles = styles_config.get('styles', {})
    style_params = styles.get(style, {}).get('parameters', {})
    
    if not style_params:
        return {}
    
    # Get intensity multiplier
    intensity_levels = styles_config.get('intensity_levels', {})
    multiplier = intensity_levels.get(str(intensity), {}).get('multiplier', 1.0)
    
    # Convert to standard prosody parameters
    result = {}
    
    # Apply intensity to rate parameter
    if 'rate' in style_params:
        adjusted_rate = _apply_intensity_to_rate(style_params['rate'], multiplier)
        if adjusted_rate:
            result['rate'] = adjusted_rate
    
    # Apply intensity to pitch parameter
    if 'pitch' in style_params:
        adjusted_pitch = _apply_intensity_to_pitch(style_params['pitch'], multiplier)
        if adjusted_pitch:
            result['pitch'] = adjusted_pitch
    
    # Apply intensity to volume parameter
    if 'volume' in style_params:
        adjusted_volume = _apply_intensity_to_volume(style_params['volume'], multiplier)
        if adjusted_volume:
            result['volume'] = adjusted_volume
    
    return result


def list_styles() -> List[str]:
    """Get list of available prosody styles"""
    try:
        styles_config = load_styles()
        return list(styles_config.get('styles', {}).keys())
    except Exception:
        return ['conversational', 'newscast', 'dramatic', 'meditation', 'energetic']


def get_style_info(style: str) -> Optional[Dict]:
    """Get detailed information about a specific style"""
    try:
        styles_config = load_styles()
        return styles_config.get('styles', {}).get(style)
    except Exception:
        return None





def validate_style(style: str) -> bool:
    """Check if a prosody style is valid"""
    return style in list_styles()


def validate_intensity(intensity: int) -> bool:
    """Check if an intensity level is valid"""
    return isinstance(intensity, int) and 1 <= intensity <= 5


# Helper functions for parameter conversion
def _apply_intensity_to_rate(rate_str: str, multiplier: float) -> Optional[str]:
    """Apply intensity multiplier to rate parameter"""
    if not rate_str or rate_str == "+0%":
        return None
        
    try:
        # Parse rate string (e.g., '+10%' -> 10, '-5%' -> -5)
        sign = 1 if rate_str.startswith('+') else -1
        if rate_str.startswith(('+', '-')):
            rate_str = rate_str[1:]
        
        if rate_str.endswith('%'):
            rate_value = float(rate_str[:-1])
        else:
            rate_value = float(rate_str)
        
        # Apply intensity multiplier
        adjusted_value = rate_value * multiplier * sign
        
        # Clamp to reasonable bounds (-50% to +100%)
        adjusted_value = max(-50, min(100, adjusted_value))
        
        # Format back to string
        sign_char = '+' if adjusted_value >= 0 else ''
        return f"{sign_char}{adjusted_value:.0f}%"
        
    except (ValueError, IndexError):
        return None


def _apply_intensity_to_pitch(pitch_str: str, multiplier: float) -> Optional[str]:
    """Apply intensity multiplier to pitch parameter"""
    if not pitch_str or pitch_str == "+0Hz":
        return None
        
    try:
        # Parse pitch string (e.g., '+5Hz' -> 5, '-3Hz' -> -3)
        sign = 1 if pitch_str.startswith('+') else -1
        if pitch_str.startswith(('+', '-')):
            pitch_str = pitch_str[1:]
        
        if pitch_str.endswith('Hz'):
            pitch_value = float(pitch_str[:-2])
        else:
            pitch_value = float(pitch_str)
        
        # Apply intensity multiplier
        adjusted_value = pitch_value * multiplier * sign
        
        # Clamp to reasonable bounds (-20Hz to +50Hz)
        adjusted_value = max(-20, min(50, adjusted_value))
        
        # Format back to string
        sign_char = '+' if adjusted_value >= 0 else ''
        return f"{sign_char}{adjusted_value:.0f}Hz"
        
    except (ValueError, IndexError):
        return None


def _apply_intensity_to_volume(volume_str: str, multiplier: float) -> Optional[str]:
    """Apply intensity multiplier to volume parameter"""
    if not volume_str or volume_str == "+0dB":
        return None
        
    try:
        # Parse volume string (e.g., '+3dB' -> 3, '-2dB' -> -2)
        sign = 1 if volume_str.startswith('+') else -1
        if volume_str.startswith(('+', '-')):
            volume_str = volume_str[1:]
        
        if volume_str.endswith('dB'):
            volume_value = float(volume_str[:-2])
        else:
            volume_value = float(volume_str)
        
        # Apply intensity multiplier
        adjusted_value = volume_value * multiplier * sign
        
        # Clamp to reasonable bounds (-10dB to +10dB)
        adjusted_value = max(-10, min(10, adjusted_value))
        
        # Format back to string
        sign_char = '+' if adjusted_value >= 0 else ''
        return f"{sign_char}{adjusted_value:.0f}dB"
        
    except (ValueError, IndexError):
        return None
