#!/usr/bin/env python3
"""
pyttsx3 Text-to-Speech Engine
Integrates pyttsx3 with the BaseTTSEngine interface  
Now with explicit parameter handling (no **kwargs)
"""

import asyncio
import logging
import threading
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import logger
from engines.models import Voice
from engines.core import BaseTTSEngine, EngineType, ConversionParams

# Import for proper audio format conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Attempt to import pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

logger = logging.getLogger(__name__)


class PyTTSx3Engine(BaseTTSEngine):
    """pyttsx3 offline TTS engine with explicit parameter handling"""
    
    def __init__(self, name: str, rate: int = 200, volume: float = 0.9, 
                 voice_id: str = None, **kwargs):
        """
        Initialize pyttsx3 Engine
        
        Args:
            name (str): Engine name/identifier
            rate (int): Default speech rate (words per minute)
            volume (float): Default volume (0.0-1.0)
            voice_id (str): Default voice ID
        """
        super().__init__(name, EngineType.OFFLINE)
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id

        self.engine = None
        self._available_voices = []
    
    async def initialize(self) -> bool:
        """
        Initialize the engine and check pyttsx3 availability
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not PYTTSX3_AVAILABLE:
            logger.error("pyttsx3 library not available. Install with: pip install pyttsx3")
            self.last_error = "pyttsx3 library not installed"
            self.is_available = False
            return False
        
        try:
            # Initialize pyttsx3 engine
            self.engine = pyttsx3.init()
            
            if self.engine is None:
                logger.error("Failed to initialize pyttsx3 engine")
                self.last_error = "pyttsx3 engine initialization failed"
                self.is_available = False
                return False
            
            # Configure engine settings
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set specific voice if requested
            if self.voice_id:
                voices = self.engine.getProperty('voices')
                if voices:
                    voice_found = False
                    for voice in voices:
                        if voice.id == self.voice_id or voice.name == self.voice_id:
                            self.engine.setProperty('voice', voice.id)
                            voice_found = True
                            break
                    
                    if not voice_found:
                        logger.warning(f"Voice '{self.voice_id}' not found, using default")
            
            # Cache available voices
            try:
                self._available_voices = self.engine.getProperty('voices') or []
            except:
                self._available_voices = []
            
            self.is_available = True
            logger.info(f"pyttsx3 initialized successfully with {len(self._available_voices)} voices")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.last_error = str(e)
            self.is_available = False
            return False
    
    def validate_params(self, params: ConversionParams) -> tuple[bool, str]:
        """
        Validate parameters for pyttsx3 engine
        
        Args:
            params (ConversionParams): Parameters to validate
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # pyttsx3 supports: voice (as voice_id), rate_int, volume
        # It does NOT support: language, rate (string format), pitch, slow
        
        unsupported = []
        if params.language is not None:
            unsupported.append("language (use specific voice IDs instead)")
        if params.rate is not None:
            unsupported.append("rate (use 'rate_int' for pyttsx3)")
        if params.pitch is not None:
            unsupported.append("pitch")
        if params.slow is not None:
            unsupported.append("slow")
        
        if unsupported:
            error_msg = f"pyttsx3 doesn't support: {', '.join(unsupported)}. Supports 'voice', 'rate_int', and 'volume'."
            return False, error_msg
        
        # Validate volume range if provided
        if params.volume is not None and not (0.0 <= params.volume <= 1.0):
            return False, f"Volume must be between 0.0 and 1.0, got: {params.volume}"
        
        # Validate rate range if provided  
        if params.rate_int is not None and not (1 <= params.rate_int <= 1000):
            return False, f"Rate must be between 1 and 1000 words per minute, got: {params.rate_int}"
        
        return True, ""
    
    async def _perform_conversion(self, text: str, output_path: Path, params: ConversionParams) -> bool:
        """
        Convert text to speech using pyttsx3 with explicit parameters
        
        Args:
            text (str): Text content to convert
            output_path (Path): Output file path for audio
            params (ConversionParams): Explicit conversion parameters
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        logger.info("Converting text to speech using pyttsx3")
        
        # Run conversion in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None, self._sync_convert, text, output_path, params
        )
        
        if success:
            logger.info(f"pyttsx3 audio saved successfully to: {output_path}")
            return True
        else:
            logger.error("pyttsx3 conversion failed")
            return False
    
    def _sync_convert(self, text: str, output_path: Path, params: ConversionParams) -> bool:
        """
        Synchronous conversion method (run in thread pool)
        
        Args:
            text (str): Text to convert
            output_path (Path): Output file path
            params (ConversionParams): Conversion parameters
            
        Returns:
            bool: True if successful
        """
        try:
            # Configure engine with provided parameters
            if params.voice is not None:
                self._set_voice(params.voice)
            
            if params.rate_int is not None:
                self.engine.setProperty('rate', params.rate_int)
            
            if params.volume is not None:
                self.engine.setProperty('volume', params.volume)
            
            # Create a temporary audio file (pyttsx3 format varies by platform)
            # On macOS, pyttsx3 may create AIFF files despite .wav extension
            with tempfile.NamedTemporaryFile(suffix='.audio', delete=False) as temp_audio:
                temp_audio_path = Path(temp_audio.name)
            
            try:
                # Save to temporary file - let pyttsx3 determine the format
                self.engine.save_to_file(text, str(temp_audio_path))
                self.engine.runAndWait()
                
                if not temp_audio_path.exists() or temp_audio_path.stat().st_size == 0:
                    raise Exception("pyttsx3 failed to create output file")
                
                logger.info(f"pyttsx3 created temp file: {temp_audio_path} ({temp_audio_path.stat().st_size} bytes)")
                
                # Always use format conversion since pyttsx3 output format is unpredictable
                # On macOS it often creates AIFF-C files even with .wav extension
                self._convert_audio_format(temp_audio_path, output_path)
                
                return True
                
            finally:
                # Clean up temporary file if it still exists
                if temp_audio_path.exists():
                    temp_audio_path.unlink(missing_ok=True)
                    
        except Exception as e:
            raise Exception(f"pyttsx3 conversion failed: {e}")
    
    def _set_voice(self, voice_identifier: str):
        """Set the voice by ID or name"""
        voices = self.engine.getProperty('voices')
        if not voices:
            return
        
        for voice in voices:
            if voice.id == voice_identifier or voice.name == voice_identifier:
                self.engine.setProperty('voice', voice.id)
                return
        
        # If not found, log warning but don't fail
        logger.warning(f"Voice '{voice_identifier}' not found in pyttsx3")
    
    def _convert_audio_format(self, input_path: Path, output_path: Path):
        """
        Convert audio format from native pyttsx3 output to target format
        Uses pydub for proper format conversion (handles macOS AIFF-C, WAV, etc.)
        """
        if not PYDUB_AVAILABLE:
            logger.warning("pydub not available, using file rename as fallback")
            input_path.rename(output_path)
            return
        
        try:
            # Detect input format - pyttsx3 on macOS may output AIFF-C instead of WAV
            logger.info(f"Converting audio from {input_path.suffix} to {output_path.suffix}")
            
            # Load audio using pydub (auto-detects format)
            audio = AudioSegment.from_file(str(input_path))
            
            # Convert to target format
            output_format = output_path.suffix.lower().lstrip('.')
            if output_format == 'mp3':
                # Export as MP3 with reasonable quality settings
                audio.export(str(output_path), format="mp3", bitrate="128k")
            elif output_format == 'wav':
                # Export as WAV
                audio.export(str(output_path), format="wav")
            else:
                # Try to export in requested format
                audio.export(str(output_path), format=output_format)
            
            logger.info(f"Successfully converted audio to {output_path} ({output_path.stat().st_size} bytes)")
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            # Fallback to simple rename if conversion fails
            logger.warning("Falling back to file rename")
            input_path.rename(output_path)
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """
        List all available pyttsx3 voices
        
        Returns:
            List[Dict]: List of voice information dictionaries
        """
        voices_info = []
        
        try:
            for voice in self._available_voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voices_info.append(voice_info)
                
        except Exception as e:
            logger.error(f"Error listing pyttsx3 voices: {e}")
        
        return voices_info
    
    def parse_voice_list(self, raw_output: str) -> List[Voice]:
        """
        Parse pyttsx3 voice listing output into standardized Voice objects
        
        Args:
            raw_output (str): Raw CLI output from pyttsx3 voice listing
            
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
            
            # Pyttsx3 format: "   1. Albert (en_US)"
            if '. ' in line and '(' in line:
                parts = line.split('. ', 1)
                if len(parts) > 1:
                    voice_part = parts[1].split(' (')[0].strip()
                    lang_part = parts[1].split(' (')[1].replace(')', '').strip() if ' (' in parts[1] else "unknown"
                    
                    voices.append(Voice(
                        id=voice_part,
                        name=voice_part,
                        language=lang_part,
                        engine="pyttsx3"
                    ))
        
        return voices 