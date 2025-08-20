#!/usr/bin/env python3
"""
TTS Engine Type Definitions
Contains enums, dataclasses, and type definitions used across the TTS engine system
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class EngineType(Enum):
    """Engine type classification"""
    CLOUD = "cloud"
    OFFLINE = "offline"


@dataclass
class ConversionParams:
    """
    Explicit parameters for text-to-speech conversion
    No more **kwargs - all parameters are explicit
    """
    # Universal parameters (all engines should handle gracefully)
    voice: Optional[str] = None
    language: Optional[str] = None
    
    # Rate/speed parameters (engines interpret as they can)
    rate: Optional[str] = None  # For EdgeTTS: "+50%", "-25%"
    rate_int: Optional[int] = None  # For pyttsx3: 200, 300
    
    # Pitch parameters (engines that support it)
    pitch: Optional[str] = None  # For EdgeTTS: "+10Hz", "-5Hz"
    
    # Volume parameters
    volume: Optional[float] = None  # For pyttsx3: 0.0-1.0
    
    # Engine-specific flags
    slow: Optional[bool] = None  # For gTTS
    
    # Prosody enhancement parameters
    style: Optional[str] = None  # Prosody style name (e.g., "newscast", "warm_coach")
    style_intensity: Optional[int] = None  # Style intensity (1-5)
    reference_audio: Optional[str] = None  # Path to reference audio for style adaptation
    prosody_enabled: Optional[bool] = None  # Whether to apply prosody enhancement 