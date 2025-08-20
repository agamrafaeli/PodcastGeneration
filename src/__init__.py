#!/usr/bin/env python3
"""
Text-to-Speech Package
A modular text-to-speech application with multi-engine support and intelligent fallback
"""

from config import logger
from tts.converter import TextToSpeechConverter
from main import main
from engines import EngineManager, BaseTTSEngine, EngineType

__version__ = "2.0.0"  # Updated to reflect multi-engine architecture
__author__ = "TTS Script"

__all__ = [
    "logger",
    "TextToSpeechConverter", 
    "EngineManager",
    "BaseTTSEngine",
    "EngineType",
    "main"
] 