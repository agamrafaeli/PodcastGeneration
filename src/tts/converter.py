#!/usr/bin/env python3
"""
Text-to-Speech Converter Module
Contains the main TextToSpeechConverter class for handling TTS operations
Now with explicit engine selection and parameter handling (no fallbacks)
"""

import asyncio
import sys
from pathlib import Path
import time

from config import logger, DEFAULT_VOICE, TTS_ENGINES, DEFAULT_TTS_ENGINE
from engines.core import EngineManager, ConversionParams
from engines.implementations.cloud.edge_tts import EdgeTTSEngine
from engines.implementations.cloud.gtts import gTTSEngine
from engines.implementations.offline.pyttsx3 import PyTTSx3Engine
from prosody import get_prosody_params


class TextToSpeechConverter:
    """Text-to-Speech converter with explicit engine selection (no fallbacks)"""
    
    def __init__(self, engine_name: str, voice: str = None, language: str = None, 
                 rate: str = None, rate_int: int = None, pitch: str = None, 
                 volume: float = None, slow: bool = None,
                 prosody_style: str = None, prosody_intensity: int = None):
        """
        Initialize the TTS converter with explicit engine and parameters
        
        Args:
            engine_name (str): Required - name of engine to use ('edge_tts', 'gtts', 'pyttsx3')
            voice (str): Voice name/ID to use
            language (str): Language code for synthesis
            rate (str): Speech rate adjustment (e.g., "+50%", "-25%") - for EdgeTTS
            rate_int (int): Speech rate in words per minute - for pyttsx3
            pitch (str): Pitch adjustment (e.g., "+10Hz", "-5Hz") - for EdgeTTS
            volume (float): Volume level (0.0-1.0) - for pyttsx3
            slow (bool): Slow speech flag - for gTTS
            prosody_style (str): Prosody style name (e.g., 'newscast', 'conversational')
            prosody_intensity (int): Prosody intensity level (1-5)
        """
        self.engine_name = engine_name
        
        # Create explicit parameters object
        self.params = ConversionParams(
            voice=voice,
            language=language,
            rate=rate,
            rate_int=rate_int,
            pitch=pitch,
            volume=volume,
            slow=slow,
            style=prosody_style,
            style_intensity=prosody_intensity
        )
        
        # Store prosody parameters for new API integration
        self.prosody_style = prosody_style
        self.prosody_intensity = prosody_intensity
        
        self.manager = None
        self._initialized = False
        
        # Apply prosody parameters if provided
        if self.prosody_style or self.prosody_intensity:
            self._apply_prosody_to_params()
    
    async def initialize(self):
        """Initialize the engine manager and register engines"""
        self.manager = EngineManager()
        
        # Register all engines with their default configurations
        edge_tts = EdgeTTSEngine(
            name="edge_tts",
            voice=TTS_ENGINES['edge_tts']['voice'],
            rate=TTS_ENGINES['edge_tts']['rate'],
            pitch=TTS_ENGINES['edge_tts']['pitch']
        )
        
        gtts = gTTSEngine(
            name="gtts",
            language=TTS_ENGINES['gtts']['language'],
            slow=TTS_ENGINES['gtts']['slow']
        )
        
        pyttsx3 = PyTTSx3Engine(
            name="pyttsx3",
            rate=TTS_ENGINES['pyttsx3']['rate'],
            volume=TTS_ENGINES['pyttsx3']['volume']
        )
        
        # Register engines
        self.manager.register_engine(edge_tts)
        self.manager.register_engine(gtts)
        self.manager.register_engine(pyttsx3)
        
        # Initialize all engines
        await self.manager.initialize(TTS_ENGINES)
        
        self._initialized = True
        logger.info(f"TTS Converter initialized for engine: {self.engine_name}")
    
    def _apply_prosody_to_params(self):
        """Apply prosody style to engine parameters using simplified prosody system"""
        try:
            # Get standard prosody parameters (engine-agnostic)
            standard_params = get_prosody_params(
                style=self.prosody_style,
                intensity=self.prosody_intensity or 3
            )
            
            if standard_params:
                # Convert standard parameters to engine-specific formats
                engine_params = self._convert_prosody_to_engine_params(standard_params)
                
                if engine_params:
                    logger.info(f"Applied prosody - Standard: {standard_params}, Engine-specific: {engine_params}")
                
        except Exception as e:
            logger.warning(f"Failed to apply prosody parameters: {e}")
    
    def _convert_prosody_to_engine_params(self, standard_params: dict) -> dict:
        """Convert standard prosody parameters to engine-specific formats"""
        converted = {}
        
        if self.engine_name == "edge_tts":
            # Edge TTS uses rate and pitch directly from standard format
            if "rate" in standard_params and not self.params.rate:
                self.params.rate = standard_params["rate"]
                converted["rate"] = standard_params["rate"]
            
            if "pitch" in standard_params and not self.params.pitch:
                self.params.pitch = standard_params["pitch"]
                converted["pitch"] = standard_params["pitch"]
                
        elif self.engine_name == "gtts":
            # gTTS only supports slow flag - convert negative rate to slow=True
            if "rate" in standard_params and self.params.slow is None:
                if standard_params["rate"].startswith('-'):
                    self.params.slow = True
                    converted["slow"] = True
                    
        elif self.engine_name == "pyttsx3":
            # pyttsx3 uses different parameter formats
            if "rate" in standard_params and not self.params.rate_int:
                wpm = self._convert_rate_to_wpm(standard_params["rate"])
                if wpm:
                    self.params.rate_int = wpm
                    converted["rate"] = wpm
            
            if "volume" in standard_params and not self.params.volume:
                vol = self._convert_volume_to_float(standard_params["volume"])
                if vol is not None:
                    self.params.volume = vol
                    converted["volume"] = vol
                    
        return converted
    
    def _convert_rate_to_wpm(self, rate_str: str) -> int:
        """Convert percentage rate to words per minute for pyttsx3"""
        try:
            # Base WPM for pyttsx3 is typically around 200
            base_wpm = 200
            
            sign = 1 if rate_str.startswith('+') else -1
            if rate_str.startswith(('+', '-')):
                rate_str = rate_str[1:]
            
            if rate_str.endswith('%'):
                rate_percent = float(rate_str[:-1]) * sign
                return int(base_wpm * (1 + rate_percent / 100))
                
        except (ValueError, AttributeError):
            pass
        return None
    
    def _convert_volume_to_float(self, volume_str: str) -> float:
        """Convert dB volume to float for pyttsx3"""
        try:
            if volume_str.endswith('dB'):
                # Rough conversion: 0dB = 0.5, +6dB = 1.0, -6dB = 0.25
                db_value = float(volume_str[:-2].lstrip('+'))
                # Approximate conversion (not acoustically accurate)
                volume_float = 0.5 * (10 ** (db_value / 20))
                return max(0.0, min(1.0, volume_float))
        except (ValueError, AttributeError):
            pass
        return None
    
    async def _ensure_initialized(self):
        """Ensure the converter is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def validate_request(self) -> tuple[bool, str]:
        """
        Validate the conversion request before attempting conversion
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        await self._ensure_initialized()
        
        # Check if requested engine exists and is available
        available_engines = self.manager.list_available_engines()
        if self.engine_name not in available_engines:
            all_engines = list(self.manager.engines.keys())
            error_msg = f"Engine '{self.engine_name}' not available. Available engines: {available_engines}. All registered engines: {all_engines}"
            return False, error_msg
        
        # Validate parameters for the specific engine
        engine = self.manager.engines[self.engine_name]
        is_valid, param_error = engine.validate_params(self.params)
        if not is_valid:
            error_msg = f"Parameter validation failed for {self.engine_name}: {param_error}"
            return False, error_msg
        
        # If a voice is specified, validate it exists for this engine
        if self.params.voice:
            is_valid, voice_error = await self.manager.validate_voice_for_engine(
                self.engine_name, self.params.voice
            )
            if not is_valid:
                return False, voice_error
        
        return True, ""
    
    async def convert_text_to_speech(self, text, output_path):
        """
        Convert text to speech using the specified engine and parameters
        
        Args:
            text (str): Text content to convert
            output_path (Path): Output file path for audio
        """
        await self._ensure_initialized()
        
        # Validate the request first
        is_valid, error_message = await self.validate_request()
        if not is_valid:
            logger.error(f"Conversion request validation failed: {error_message}")
            raise ValueError(f"Invalid conversion request: {error_message}")
        
        try:
            # Simple prosody system: parameters are already applied to self.params
            # No need for text enhancement - engines use native parameters directly
            if self.prosody_style or self.prosody_intensity:
                logger.info(f"Using prosody - Style: {self.prosody_style}, Intensity: {self.prosody_intensity or 3}")
            
            # Use engine manager for direct conversion (no fallback)
            success, error_msg = await self.manager.convert_with_engine(
                self.engine_name, 
                text,  # Use original text - no SSML enhancement needed
                output_path,
                self.params
            )
            
            if success:
                logger.info(f"Conversion successful using {self.engine_name}")
            else:
                logger.error(f"Conversion failed: {error_msg}")
                raise RuntimeError(f"Text-to-speech conversion failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
    
    async def list_voices(self):
        """List voices for the specified engine"""
        await self._ensure_initialized()
        
        if self.engine_name not in self.manager.engines:
            raise ValueError(f"Engine '{self.engine_name}' not found")
        
        engine = self.manager.engines[self.engine_name]
        if not engine.is_available:
            raise RuntimeError(f"Engine '{self.engine_name}' not available")
        
        return await engine.list_voices()
    
    def read_text_file(self, file_path):
        """Read text content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
    
    def get_engine_info(self) -> dict:
        """Get information about the selected engine"""
        if not self._initialized:
            return {"error": "Not initialized"}
        
        if self.engine_name not in self.manager.engines:
            return {"error": f"Engine '{self.engine_name}' not found"}
        
        engine = self.manager.engines[self.engine_name]
        return {
            "name": engine.name,
            "type": engine.engine_type.value,
            "available": engine.is_available,
            "error_count": engine.error_count,
            "last_error": engine.last_error,
        }
    
    def get_available_engines(self) -> list:
        """Get list of available engine names"""
        if not self._initialized:
            return []
        return self.manager.list_available_engines() 