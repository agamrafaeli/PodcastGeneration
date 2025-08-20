#!/usr/bin/env python3
"""
Configuration module for Text-to-Speech application
Contains logging setup and other configuration constants
"""

import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default TTS settings (for backward compatibility)
DEFAULT_VOICE = "en-US-AriaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "+0Hz"
DEFAULT_MAX_CONCURRENT = 10

# TTS Engine Configuration
TTS_ENGINES = {
    'edge_tts': {
        'enabled': True,
        'voice': 'en-US-JennyNeural',
        'rate': '+0%',
        'pitch': '+0Hz'
    },
    'gtts': {
        'enabled': True,
        'slow': False,
        'language': 'en'
    },
    'pyttsx3': {
        'enabled': True,
        'rate': 200,
        'volume': 0.9
    }
}

# Engine fallback priority order
TTS_FALLBACK_ORDER = ['edge_tts', 'gtts', 'pyttsx3']

# Default preferred engine
DEFAULT_TTS_ENGINE = 'edge_tts' 