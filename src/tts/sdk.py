#!/usr/bin/env python3
"""
TTS SDK - Clean Python interface for text-to-speech operations
Provides a simplified SDK for TTS conversions and voice management
"""

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from enum import Enum
import tempfile
import json

from engines.models import Voice
from engines.implementations.cloud.edge_tts import EdgeTTSEngine
from engines.implementations.cloud.gtts import gTTSEngine
from engines.implementations.offline.pyttsx3 import PyTTSx3Engine

class Engine(Enum):
    EDGE_TTS = "edge_tts"
    GTTS = "gtts" 
    PYTTSX3 = "pyttsx3"

@dataclass
class ConversionResult:
    """Result of a TTS conversion"""
    success: bool
    output_file: Optional[Path] = None
    file_size: int = 0
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None

@dataclass
class VoiceSampleResult:
    """Result of voice sample generation"""
    success: bool
    consolidated_file: Optional[Path] = None  # Single consolidated MP3 file
    output_directory: Optional[Path] = None
    engines_used: List[str] = field(default_factory=list)
    samples_generated: int = 0
    total_duration_seconds: float = 0.0
    error_message: Optional[str] = None
    

class TTSSDK:
    """SDK for text-to-speech operations with clean Python interface"""
    
    def __init__(self, timeout: float = 60.0, script_path: Optional[Path] = None):
        """
        Initialize TTS client
        
        Args:
            timeout: Default timeout for operations in seconds
            script_path: Path to src/cli.py script (auto-detected if None)
        """
        self.timeout = timeout
        self.script_path = script_path or self._find_script_path()
        
        # Mapping from Engine enum to engine classes for voice parsing
        self._engine_classes = {
            Engine.EDGE_TTS: EdgeTTSEngine,
            Engine.GTTS: gTTSEngine,
            Engine.PYTTSX3: PyTTSx3Engine
        }
    
    def _find_script_path(self) -> Path:
        """Auto-detect the src/cli.py script location"""
        # Try common locations relative to this file
        current_dir = Path(__file__).parent
        candidates = [
            current_dir / "cli.py",  # Same as src/tts/sdk.py -> src/cli.py  
            current_dir.parent / "cli.py",  # From src/tts -> src/cli.py
            current_dir.parent.parent / "src" / "cli.py",  # From project root
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        raise FileNotFoundError("Could not locate src/cli.py script")
    
    async def _run_cli_command(self, args: List[str], input_text: Optional[str] = None) -> tuple[int, str, str]:
        """Execute CLI command and return (exit_code, stdout, stderr)"""
        cmd = [sys.executable, str(self.script_path)] + args
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_text else None
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_text.encode() if input_text else None),
                timeout=self.timeout
            )
            
            return process.returncode, stdout.decode(), stderr.decode()
            
        except asyncio.TimeoutError:
            if 'process' in locals():
                process.kill()
                await process.wait()
            raise asyncio.TimeoutError(f"Command timed out after {self.timeout}s")
    
    async def convert(
        self,
        text: Union[str, Path],
        output_path: Path,
        engine: Engine,
        voice: Optional[str] = None,
        language: Optional[str] = None,
        rate: Optional[str] = None,        # EdgeTTS: "+50%", "-25%" 
        rate_int: Optional[int] = None,    # pyttsx3: 200 wpm
        pitch: Optional[str] = None,       # EdgeTTS: "+10Hz", "-5Hz"
        volume: Optional[float] = None,    # pyttsx3: 0.0-1.0
        slow: bool = False                 # gTTS: slow speech
    ) -> ConversionResult:
        """Convert text to speech"""
        
        # Handle text input - create temp file if needed
        if isinstance(text, str):
            temp_file = Path(tempfile.mktemp(suffix=".txt"))
            temp_file.write_text(text)
            input_file = temp_file
            cleanup_temp = True
        else:
            input_file = text
            cleanup_temp = False
        
        try:
            # Build CLI arguments
            args = [str(input_file), "--engine", engine.value, "-o", str(output_path)]
            
            # Add engine-specific parameters
            if voice:
                if engine == Engine.GTTS:
                    args.extend(["-l", voice])  # gTTS uses language parameter
                else:
                    args.extend(["-v", voice])  # Other engines use voice parameter
            
            if language:
                args.extend(["-l", language])
            
            if rate:
                args.extend(["-r", rate])
            
            if rate_int:
                args.extend(["--rate-int", str(rate_int)])
            
            if pitch:
                args.extend(["-p", pitch])
            
            if volume is not None:
                args.extend(["--volume", str(volume)])
            
            if slow:
                args.append("--slow")
            
            # Execute conversion
            exit_code, stdout, stderr = await self._run_cli_command(args)
            
            # Check results
            success = exit_code == 0 and output_path.exists()
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            return ConversionResult(
                success=success,
                output_file=output_path if success else None,
                file_size=file_size,
                error_message=stderr if not success else None
            )
        
        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
        
        finally:
            # Cleanup temp file if we created one
            if cleanup_temp and input_file.exists():
                input_file.unlink()
    
    async def list_voices(self, engine: Engine) -> List[Voice]:
        """Get available voices for an engine"""
        try:
            args = ["--engine", engine.value, "--list-voices"]
            exit_code, stdout, stderr = await self._run_cli_command(args)
            
            if exit_code != 0:
                return []
            
            # Use the engine's own parsing method
            engine_class = self._engine_classes.get(engine)
            if not engine_class:
                return []
            
            # Create a temporary engine instance for parsing
            # We don't need to fully initialize it since we're only using parse_voice_list
            if engine == Engine.EDGE_TTS:
                temp_engine = engine_class("temp", voice="en-US-JennyNeural")
            elif engine == Engine.GTTS:
                temp_engine = engine_class("temp", language="en")
            elif engine == Engine.PYTTSX3:
                temp_engine = engine_class("temp", rate=200, volume=0.9)
            else:
                return []
            
            return temp_engine.parse_voice_list(stdout)
        
        except Exception:
            return []
    

    
    async def get_engine_info(self, engine: Engine) -> Dict[str, Any]:
        """Get information about an engine"""
        try:
            args = ["--engine", engine.value, "--engine-info"]
            exit_code, stdout, stderr = await self._run_cli_command(args)
            
            if exit_code == 0:
                return {"engine": engine.value, "available": True, "info": stdout.strip()}
            else:
                return {"engine": engine.value, "available": False, "error": stderr}
        
        except Exception as e:
            return {"engine": engine.value, "available": False, "error": str(e)}
    
    async def get_available_engines(self) -> List[Engine]:
        """Get list of available/working engines"""
        available = []
        
        for engine in Engine:
            try:
                # Try to list voices as a quick availability test
                voices = await self.list_voices(engine)
                if voices:  # If we got voices back, engine is working
                    available.append(engine)
            except Exception:
                continue  # Engine not available
        
        return available
    
    async def generate_voice_samples(self, text: str, output_dir: Optional[Path] = None) -> VoiceSampleResult:
        """
        Generate voice comparison samples using different engines
        Phase 2: Returns a single consolidated MP3 file with narrator labels
        
        Args:
            text: Text to use for voice sampling
            output_dir: Directory to store samples (default: generated/voice_samples)
            
        Returns:
            VoiceSampleResult with information about the consolidated sample file
        """
        try:
            # Call CLI voice sample command
            args = ["--voice-sample", text]
            exit_code, stdout, stderr = await self._run_cli_command(args)
            
            # Parse results from CLI output
            if exit_code != 0:
                return VoiceSampleResult(
                    success=False,
                    error_message=f"Voice sample generation failed: {stderr}"
                )
            
            # Determine output directory (CLI creates this structure)
            if output_dir is None:
                output_dir = Path("generated/voice_samples")
            
            # Check if directory exists
            if not output_dir.exists():
                return VoiceSampleResult(
                    success=False,
                    error_message="Voice samples directory was not created"
                )
            
            # Find the consolidated MP3 file
            consolidated_file = output_dir / "voice_samples_consolidated.mp3"
            
            if not consolidated_file.exists():
                return VoiceSampleResult(
                    success=False,
                    error_message="Consolidated voice sample file was not created"
                )
            
            # Get file info
            file_size = consolidated_file.stat().st_size
            
            # Extract information from CLI output
            engines_used = []
            samples_generated = 0
            duration = 0.0
            
            # Parse CLI output for metadata
            output_lines = stdout.split('\n')
            for line in output_lines:
                if 'Duration:' in line:
                    try:
                        duration_str = line.split('Duration:')[1].split('seconds')[0].strip()
                        duration = float(duration_str)
                    except:
                        pass
                elif 'Samples included:' in line:
                    try:
                        samples_str = line.split('Samples included:')[1].split('/')[0].strip()
                        samples_generated = int(samples_str)
                    except:
                        pass
                elif 'completed with' in line:
                    # Extract engine name from success messages
                    try:
                        engine = line.split('completed with')[1].split()[0]
                        if engine not in engines_used:
                            engines_used.append(engine)
                    except:
                        pass
            
            return VoiceSampleResult(
                success=True,
                consolidated_file=consolidated_file,
                output_directory=output_dir,
                engines_used=engines_used,
                samples_generated=samples_generated,
                total_duration_seconds=duration,
            )
            
        except Exception as e:
            return VoiceSampleResult(
                success=False,
                error_message=f"Unexpected error during voice sample generation: {str(e)}"
            )
    
    async def test_engine(self, engine: Engine) -> bool:
        """Test if an engine is working"""
        try:
            voices = await self.list_voices(engine)
            return len(voices) > 0
        except Exception:
            return False
    
    # Context manager support
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass 