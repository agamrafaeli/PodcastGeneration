#!/usr/bin/env python3
"""
Google Text-to-Speech (gTTS) Engine
Integrates gTTS with the BaseTTSEngine interface
Now with explicit parameter handling (no **kwargs)
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any

from config import logger
from engines.models import Voice
from engines.core import BaseTTSEngine, EngineType, ConversionParams

# Attempt to import gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class gTTSEngine(BaseTTSEngine):
    """Google Text-to-Speech engine with explicit parameter handling"""
    
    def __init__(self, name: str, language: str = "en", slow: bool = False, **kwargs):
        """
        Initialize gTTS Engine
        
        Args:
            name (str): Engine name/identifier  
            language (str): Default language code
            slow (bool): Default slow speech flag
        """
        super().__init__(name, EngineType.CLOUD)
        self.language = language
        self.slow = slow
    
    async def initialize(self) -> bool:
        """
        Initialize the engine and check gTTS availability
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not GTTS_AVAILABLE:
            logger.error("gTTS library not available. Install with: pip install gtts")
            self.last_error = "gTTS library not installed"
            self.is_available = False
            return False
        
        try:
            # Test gTTS connectivity with a minimal request
            await self._test_connectivity()
            self.is_available = True
            logger.info("gTTS initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize gTTS: {e}")
            self.last_error = str(e)
            self.is_available = False
            return False
    
    async def _test_connectivity(self):
        """Test gTTS connectivity by creating a minimal TTS object"""
        # Test with minimal text and default language
        test_text = "test"
        language = self.language or "en"
        
        try:
            tts = gTTS(text=test_text, lang=language, slow=False)
            # Create and immediately delete a temporary file to test
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tts.save(tmp.name)
        except Exception as e:
            raise Exception(f"gTTS connectivity test failed: {e}")
    
    def validate_params(self, params: ConversionParams) -> tuple[bool, str]:
        """
        Validate parameters for gTTS engine
        
        Args:
            params (ConversionParams): Parameters to validate
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # gTTS ONLY supports: language, slow
        # It does NOT support: voice, rate, rate_int, pitch, volume
        
        unsupported = []
        if params.voice is not None:
            unsupported.append("voice (gTTS uses language-based synthesis)")
        if params.rate is not None:
            unsupported.append("rate")
        if params.rate_int is not None:
            unsupported.append("rate_int")
        if params.pitch is not None:
            unsupported.append("pitch")
        if params.volume is not None:
            unsupported.append("volume")
        
        if unsupported:
            error_msg = f"gTTS doesn't support: {', '.join(unsupported)}. Only supports 'language' and 'slow' parameters."
            return False, error_msg
        
        # Validate language if provided
        if params.language and not self._is_valid_language(params.language):
            return False, f"Language '{params.language}' not supported by gTTS"
        
        return True, ""
    
    def _is_valid_language(self, language: str) -> bool:
        """Check if language code is supported by gTTS"""
        # gTTS supports a wide range of languages, but here are the most common ones
        # This is a simplified check - in practice, gTTS will error if language is invalid
        common_languages = {
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi',
            'nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'tr', 'th', 'vi', 'uk'
        }
        # Allow both base language and region variants
        base_lang = language.split('-')[0].lower()
        return base_lang in common_languages
    
    async def _perform_conversion(self, text: str, output_path: Path, params: ConversionParams) -> bool:
        """
        Convert text to speech using gTTS with explicit parameters
        
        Args:
            text (str): Text content to convert
            output_path (Path): Output file path for MP3
            params (ConversionParams): Explicit conversion parameters
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        # Determine parameters
        selected_language = self._determine_language(params.language)
        selected_slow = params.slow if params.slow is not None else self.slow
        
        logger.info(f"Converting text to speech using gTTS: {selected_language}, slow={selected_slow}")
        
        # Run conversion in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self._sync_convert, text, output_path, selected_language, selected_slow
        )
        
        logger.info(f"gTTS audio saved successfully to: {output_path}")
        return True
    
    def _sync_convert(self, text: str, output_path: Path, language: str, slow: bool):
        """
        Synchronous conversion method (run in thread pool)
        
        Args:
            text (str): Text to convert
            output_path (Path): Output file path
            language (str): Language code
            slow (bool): Slow speech flag
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to file
            tts.save(str(output_path))
            
        except Exception as e:
            # Re-raise to be caught by async wrapper
            raise Exception(f"gTTS conversion failed: {e}")
    
    def _determine_language(self, language_override: str = None) -> str:
        """
        Determine which language to use
        
        Args:
            language_override (str): Explicit language override
            
        Returns:
            str: Language code to use
        """
        if language_override:
            return language_override
        return self.language
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """
        List available "voices" for gTTS (really just languages)
        
        gTTS doesn't have traditional voices - it's language-based synthesis
        
        Returns:
            List[Dict]: List of supported languages formatted as voice info
        """
        # gTTS doesn't have traditional voices, but we can list supported languages
        # This is a simplified list of commonly supported languages
        languages = [
            {'name': 'English', 'language': 'en', 'id': 'en'},
            {'name': 'Spanish', 'language': 'es', 'id': 'es'},
            {'name': 'French', 'language': 'fr', 'id': 'fr'},
            {'name': 'German', 'language': 'de', 'id': 'de'},
            {'name': 'Italian', 'language': 'it', 'id': 'it'},
            {'name': 'Portuguese', 'language': 'pt', 'id': 'pt'},
            {'name': 'Russian', 'language': 'ru', 'id': 'ru'},
            {'name': 'Chinese', 'language': 'zh', 'id': 'zh'},
            {'name': 'Japanese', 'language': 'ja', 'id': 'ja'},
            {'name': 'Korean', 'language': 'ko', 'id': 'ko'},
            {'name': 'Arabic', 'language': 'ar', 'id': 'ar'},
            {'name': 'Hindi', 'language': 'hi', 'id': 'hi'},
            {'name': 'Dutch', 'language': 'nl', 'id': 'nl'},
            {'name': 'Swedish', 'language': 'sv', 'id': 'sv'},
            {'name': 'Norwegian', 'language': 'no', 'id': 'no'},
            {'name': 'Danish', 'language': 'da', 'id': 'da'},
            {'name': 'Finnish', 'language': 'fi', 'id': 'fi'},
            {'name': 'Polish', 'language': 'pl', 'id': 'pl'},
            {'name': 'Czech', 'language': 'cs', 'id': 'cs'},
            {'name': 'Turkish', 'language': 'tr', 'id': 'tr'},
        ]
        
        return languages
    
    def parse_voice_list(self, raw_output: str) -> List[Voice]:
        """
        Parse gTTS voice listing output into standardized Voice objects
        
        Args:
            raw_output (str): Raw CLI output from gTTS voice listing
            
        Returns:
            List[Voice]: Parsed voice objects
        """
        voices = []
        lines = raw_output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and info messages
            if not line or line.startswith('2025-') or '- INFO -' in line or line.startswith('🎤'):
                continue
            
            # gTTS format: "   1. English (Language: en)"
            if 'Language: ' in line:
                lang_start = line.find('Language: ') + len('Language: ')
                lang_end = line.find(')', lang_start)
                if lang_end != -1:
                    lang_code = line[lang_start:lang_end].strip()
                    lang_name = line.split('.', 1)[1].split('(')[0].strip() if '.' in line else "Unknown"
                    
                    voices.append(Voice(
                        id=lang_code,
                        name=lang_name,
                        language=lang_code,
                        engine="gtts"
                    ))
        
        return voices 