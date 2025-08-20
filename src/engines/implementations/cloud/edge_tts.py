#!/usr/bin/env python3
"""
Enhanced Edge-TTS Engine
Integrates edge-tts with the BaseTTSEngine interface
Now with explicit parameter handling (no **kwargs)
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import logger
from engines.models import Voice
from engines.core import BaseTTSEngine, EngineType, ConversionParams

# Attempt to import edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EdgeTTSEngine(BaseTTSEngine):
    """Enhanced Edge-TTS engine with explicit parameter handling"""
    
    def __init__(self, name: str, voice: str = "en-US-JennyNeural", 
                 rate: str = "+0%", pitch: str = "+0Hz", **kwargs):
        """
        Initialize Enhanced Edge-TTS Engine
        
        Args:
            name (str): Engine name/identifier
            voice (str): Default voice name
            rate (str): Default rate adjustment
            pitch (str): Default pitch adjustment
        """
        super().__init__(name, EngineType.CLOUD)
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self._available_voices_cache = []
        
        # Language to voice mapping (embedded from voice_config.py)
        self.LANGUAGE_VOICE_MAPPING = {
            "en": ["en-US-JennyNeural", "en-US-AriaNeural"],
            "en-us": ["en-US-JennyNeural", "en-US-AriaNeural"],
            "fr": ["fr-FR-DeniseNeural", "fr-FR-EliseNeural"], 
            "de": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
            "es": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
            "it": ["it-IT-ElsaNeural", "it-IT-DiegoNeural"],
            "pt": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
            "zh": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunyangNeural"],
            "ja": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
            "ko": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the engine and check edge-tts availability
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not EDGE_TTS_AVAILABLE:
            logger.error("edge-tts library not available. Install with: pip install edge-tts")
            self.last_error = "edge-tts library not installed"
            self.is_available = False
            return False
        
        try:
            # Test basic functionality and cache available voices
            voices = await edge_tts.list_voices()
            self._available_voices_cache = voices
            
            if not voices:
                logger.error("No voices available from edge-tts")
                self.last_error = "No voices available"
                self.is_available = False
                return False
            
            self.is_available = True
            logger.info(f"Edge TTS initialized with {len(voices)} voices available")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Edge-TTS: {e}")
            self.last_error = str(e)
            self.is_available = False
            return False
    
    def validate_params(self, params: ConversionParams) -> tuple[bool, str]:
        """
        Validate parameters for Edge-TTS engine
        
        Args:
            params (ConversionParams): Parameters to validate
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Edge-TTS supports: voice, language, rate, pitch
        # It does NOT support: rate_int, volume, slow
        
        unsupported = []
        if params.rate_int is not None:
            unsupported.append("rate_int (use 'rate' with percentage format like '+25%')")
        if params.volume is not None:
            unsupported.append("volume")
        if params.slow is not None:
            unsupported.append("slow")
        
        if unsupported:
            error_msg = f"EdgeTTS doesn't support: {', '.join(unsupported)}"
            return False, error_msg
        
        # Validate rate format if provided
        if params.rate and not self._is_valid_rate_format(params.rate):
            return False, f"Invalid rate format: '{params.rate}'. Use format like '+50%' or '-25%'"
        
        # Validate pitch format if provided  
        if params.pitch and not self._is_valid_pitch_format(params.pitch):
            return False, f"Invalid pitch format: '{params.pitch}'. Use format like '+10Hz' or '-5Hz'"
        
        # Note: Prosody parameters are validated at the TTS converter level, not here
        
        return True, ""
    
    def _is_valid_rate_format(self, rate: str) -> bool:
        """Check if rate string has valid format like '+50%' or '-25%'"""
        import re
        return bool(re.match(r'^[+-]\d+%$', rate))
    
    def _is_valid_pitch_format(self, pitch: str) -> bool:
        """Check if pitch string has valid format like '+10Hz' or '-5Hz'"""
        import re
        return bool(re.match(r'^[+-]\d+Hz$', pitch))
    
    async def _perform_conversion(self, text: str, output_path: Path, params: ConversionParams) -> bool:
        """
        Convert text to speech using Edge-TTS with explicit parameters
        
        Args:
            text (str): Text content to convert (plain text or SSML)
            output_path (Path): Output file path for audio
            params (ConversionParams): Explicit conversion parameters
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        # Determine voice to use
        selected_voice = self._determine_voice(params.voice, params.language)
        selected_rate = params.rate or self.rate
        selected_pitch = params.pitch or self.pitch
        
        # Check if input is SSML or plain text
        is_ssml = text.strip().startswith('<speak')
        
        logger.info(f"Converting {'SSML' if is_ssml else 'text'} to speech using Edge-TTS voice: {selected_voice}")
        
        # Create TTS communication - Edge TTS handles both plain text and SSML
        # If SSML is provided, don't apply rate/pitch parameters as they're in the SSML
        communicate = edge_tts.Communicate(
            text, 
            selected_voice,
            rate="+0%" if is_ssml else selected_rate,  # Don't apply rate if SSML contains prosody
            pitch="+0Hz" if is_ssml else selected_pitch  # Don't apply pitch if SSML contains prosody
        )
        
        # Generate and save audio
        await communicate.save(str(output_path))
        logger.info(f"Audio saved successfully to: {output_path} ({'SSML with prosody' if is_ssml else 'plain text'})")
        
        return True
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """
        List all available Edge-TTS voices
        
        Returns:
            List[Dict]: List of voice information dictionaries
        """
        try:
            if self._available_voices_cache:
                return self._available_voices_cache
            
            voices = await edge_tts.list_voices()
            self._available_voices_cache = voices
            return voices
            
        except Exception as e:
            logger.error(f"Error listing Edge-TTS voices: {e}")
            return []
    
    def _determine_voice(self, voice_override: str = None, language: str = None) -> str:
        """
        Determine which voice to use based on parameters
        
        Args:
            voice_override (str): Explicit voice override
            language (str): Language code for automatic voice selection
            
        Returns:
            str: Voice name to use
        """
        # If explicit voice override is provided, use it
        if voice_override:
            return voice_override
        
        # If language is provided, try to find appropriate voice
        if language:
            language_voice = self.get_voice_for_language(language, self._available_voices_cache)
            if language_voice:
                return language_voice
        
        # Fall back to configured voice
        return self.voice
    
    def get_voice_for_language(self, language_code: str, 
                              available_voices: List[Dict] = None) -> Optional[str]:
        """
        Get the best available voice for a given language code
        (Embedded from voice_config.py)
        
        Args:
            language_code (str): Language code (e.g., "en", "en-US", "fr", "de-DE")
            available_voices (list): List of available voice dictionaries (optional)
            
        Returns:
            str: Voice name to use, or None if not found
        """
        language_code = language_code.lower()
        
        # Try exact match first
        if language_code in self.LANGUAGE_VOICE_MAPPING:
            preferred_voices = self.LANGUAGE_VOICE_MAPPING[language_code]
        else:
            # Try language without region (e.g., "en" from "en-US")
            base_language = language_code.split('-')[0]
            if base_language in self.LANGUAGE_VOICE_MAPPING:
                preferred_voices = self.LANGUAGE_VOICE_MAPPING[base_language]
            else:
                return None
        
        # If we have available voices, check which preferred voice is actually available
        if available_voices:
            available_voice_names = {voice.get('Name', '').lower() for voice in available_voices}
            for voice in preferred_voices:
                if voice.lower() in available_voice_names:
                    return voice
            return None
        
        # Otherwise, return the first preferred voice
        return preferred_voices[0] if preferred_voices else None
    
    def parse_voice_list(self, raw_output: str) -> List[Voice]:
        """
        Parse EdgeTTS voice listing output into standardized Voice objects
        
        Args:
            raw_output (str): Raw CLI output from EdgeTTS voice listing
            
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
            
            # EdgeTTS format: "   1. Microsoft Server Speech Text to Speech Voice (af-ZA, AdriNeural) (af-ZA, Female)"
            if '. ' in line:
                parts = line.split('. ', 1)
                if len(parts) > 1:
                    content = parts[1]
                    # Extract voice name up to first closing parenthesis
                    paren_pos = content.find(')')
                    if paren_pos != -1:
                        voice_name = content[:paren_pos+1].strip()
                        # Extract language from voice name if possible
                        lang_code = "unknown"
                        gender = None
                        
                        if '(' in voice_name and ',' in voice_name:
                            lang_start = voice_name.rfind('(') + 1
                            lang_end = voice_name.find(',', lang_start)
                            if lang_end != -1:
                                lang_code = voice_name[lang_start:lang_end].strip()
                        
                        # Extract gender from the end of the line if available
                        if '(af-ZA, Female)' in content or 'Female' in content:
                            gender = 'Female'
                        elif '(af-ZA, Male)' in content or 'Male' in content:
                            gender = 'Male'
                        
                        voices.append(Voice(
                            id=voice_name,
                            name=voice_name,
                            language=lang_code,
                            gender=gender,
                            engine="edge_tts"
                        ))
        
        return voices
    
    # Note: Prosody enhancement methods removed - all prosody logic is now handled
    # at the TTS converter level via the ProsodySDK in the @prosody/ folder