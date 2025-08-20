#!/usr/bin/env python3
"""
TTS Module
Core text-to-speech conversion functionality
"""

from tts.converter import TextToSpeechConverter
from tts.sdk import TTSSDK, Engine, ConversionResult, VoiceSampleResult

__all__ = [
    'TextToSpeechConverter',
    'TTSSDK', 
    'Engine',
    'ConversionResult',
    'VoiceSampleResult'
]
