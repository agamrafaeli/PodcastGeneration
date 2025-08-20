#!/usr/bin/env python3
"""
Mock TTS SDK for testing voice sample generation

Provides predictable SDK behavior without external dependencies.
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .engine import MockEngineFactory


class MockTTSSDK:
    """Mock SDK for voice sample generation testing"""
    
    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout
        self.mock_engines = MockEngineFactory.get_all_mock_engines()
    
    async def generate_voice_samples(self, text: str, output_dir: Optional[Path] = None):
        """Mock voice sample generation that creates predictable test files"""
        from tts.sdk import VoiceSampleResult
        import tempfile
        import shutil
        
        # Create output directory
        if output_dir is None:
            output_dir = Path("generated/voice_samples")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create individual sample files for each mock engine
        engines_used = []
        samples_generated = 0
        total_duration = 0.0
        
        # Calculate mock duration based on text length (roughly 150 words per minute)
        text_length = len(text.split())
        base_duration_per_engine = max(1.5, text_length / 150 * 60)  # At least 1.5s per engine
        
        for engine_name, engine in self.mock_engines.items():
            # Create individual sample file with duration scaled to text length
            sample_file = output_dir / f"voice_sample_{engine_name}.mp3"
            mock_mp3_data = engine._create_mock_mp3_with_duration(base_duration_per_engine)
            sample_file.write_bytes(mock_mp3_data)
            
            engines_used.append(engine_name)
            samples_generated += 1
            total_duration += base_duration_per_engine
        
        # Create consolidated file by combining all samples
        consolidated_file = output_dir / "voice_samples_consolidated.mp3"
        consolidated_data = b""
        
        for engine_name in engines_used:
            sample_file = output_dir / f"voice_sample_{engine_name}.mp3"
            if sample_file.exists():
                consolidated_data += sample_file.read_bytes()
                # Add some silence between samples (minimal MP3 data)
                consolidated_data += b"\x00" * 100
        
        consolidated_file.write_bytes(consolidated_data)
        
        return VoiceSampleResult(
            success=True,
            consolidated_file=consolidated_file,
            output_directory=output_dir,
            engines_used=engines_used,
            samples_generated=samples_generated,
            total_duration_seconds=total_duration,
        )
    
    async def list_voices(self, engine):
        """Mock voice listing"""
        from tts.sdk import Engine
        from engines.models import Voice
        
        engine_name = engine.value if hasattr(engine, 'value') else str(engine)
        if engine_name in self.mock_engines:
            return self.mock_engines[engine_name].parse_voice_list("")
        return []
    
    async def get_available_engines(self):
        """Mock available engines"""
        from tts.sdk import Engine
        return [Engine.EDGE_TTS, Engine.GTTS, Engine.PYTTSX3]
    
    async def convert(self, text: str, output_path: Path, engine, voice: str):
        """Mock TTS conversion"""
        from tts.sdk import ConversionResult
        
        engine_name = engine.value if hasattr(engine, 'value') else str(engine)
        if engine_name in self.mock_engines:
            mock_engine = self.mock_engines[engine_name]
            success = await mock_engine._perform_conversion(text, output_path)
            
            if success and output_path.exists():
                file_size = output_path.stat().st_size
                return ConversionResult(
                    success=True,
                    output_file=output_path,
                    file_size=file_size,
                    duration_ms=3500  # Mock 3.5 second duration
                )
            else:
                return ConversionResult(
                    success=False,
                    error_message=f"Mock conversion failed for {engine_name}"
                )
        
        return ConversionResult(
            success=False,
            error_message=f"Unknown mock engine: {engine_name}"
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass 
