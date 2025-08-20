#!/usr/bin/env python3
"""
TTS Engine Manager
Manages engine registration and direct conversion (no fallbacks)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from engines.core.base_engine import BaseTTSEngine
from engines.core.types import ConversionParams

logger = logging.getLogger(__name__)


class EngineManager:
    """Manages engine registration and direct conversion (no fallbacks)"""
    
    def __init__(self):
        self.engines: Dict[str, BaseTTSEngine] = {}
        self.logger = logger
    
    def register_engine(self, engine: BaseTTSEngine):
        """Register a TTS engine"""
        self.engines[engine.name] = engine
        self.logger.info(f"Registered engine: {engine.name}")
    
    async def initialize(self, engine_configs: Dict[str, Dict[str, Any]]):
        """Initialize all registered engines"""
        for name, engine in self.engines.items():
            if name not in engine_configs or not engine_configs[name].get('enabled', True):
                self.logger.info(f"Skipping disabled engine: {name}")
                continue
                
            try:
                success = await engine.initialize()
                if success:
                    self.logger.info(f"Successfully initialized engine: {name}")
                else:
                    self.logger.warning(f"Failed to initialize engine: {name}")
            except Exception as e:
                self.logger.error(f"Error initializing engine {name}: {e}")
    
    async def convert_with_engine(self, engine_name: str, text: str, output_path: Path, params: ConversionParams) -> tuple[bool, str]:
        """
        Convert text to speech using specified engine (no fallback)
        
        Args:
            engine_name (str): Exact engine name to use
            text (str): Text to convert
            output_path (Path): Output file path
            params (ConversionParams): Explicit conversion parameters
            
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        # Check if engine exists
        if engine_name not in self.engines:
            available = list(self.engines.keys())
            error_msg = f"Engine '{engine_name}' not found. Available engines: {available}"
            self.logger.error(error_msg)
            return False, error_msg
        
        engine = self.engines[engine_name]
        
        # Check if engine is available
        if not engine.is_available:
            error_msg = f"Engine '{engine_name}' is not available. Last error: {engine.last_error}"
            self.logger.error(error_msg)
            return False, error_msg
        
        # Validate parameters for this engine
        is_valid, validation_error = engine.validate_params(params)
        if not is_valid:
            error_msg = f"Invalid parameters for {engine_name}: {validation_error}"
            self.logger.error(error_msg)
            return False, error_msg
        
        # Attempt conversion
        try:
            self.logger.info(f"Converting with {engine_name}")
            success = await engine.convert_text_to_speech(text, output_path, params)
            
            if success and output_path.exists():
                self.logger.info(f"Successfully converted with {engine_name}")
                return True, ""
            else:
                error_msg = f"Conversion failed with {engine_name}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Engine {engine_name} failed: {e}"
            self.logger.error(error_msg)
            engine.error_count += 1
            engine.last_error = str(e)
            return False, error_msg
    
    def list_available_engines(self) -> List[str]:
        """List names of all available engines"""
        return [name for name, engine in self.engines.items() if engine.is_available]
    
    async def validate_voice_for_engine(self, engine_name: str, voice: str) -> tuple[bool, str]:
        """
        Validate if a voice is available for a specific engine
        
        Args:
            engine_name (str): Engine name to check
            voice (str): Voice name to validate
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if engine_name not in self.engines:
            return False, f"Engine '{engine_name}' not found"
        
        engine = self.engines[engine_name]
        if not engine.is_available:
            return False, f"Engine '{engine_name}' not available"
        
        try:
            voices = await engine.list_voices()
            voice_names = []
            
            for v in voices:
                # Handle different voice data structures
                name = v.get('name', v.get('Name', v.get('id', '')))
                voice_names.append(name)
            
            if voice in voice_names:
                return True, ""
            else:
                # Show available voices for this engine
                sample_voices = sorted(voice_names)[:10]
                error_msg = f"Voice '{voice}' not available in {engine_name}. Available voices: {', '.join(sample_voices)}"
                if len(voice_names) > 10:
                    error_msg += f" (and {len(voice_names) - 10} more)"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error listing voices for {engine_name}: {e}" 