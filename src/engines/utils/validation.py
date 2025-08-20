#!/usr/bin/env python3
"""
Audio Validation Utilities
Contains utilities and constants for validating audio output
"""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

# Import for audio validation
try:
    from pydub import AudioSegment
    import subprocess
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AudioValidationResult:
    """Result of audio validation with detailed information"""
    is_valid: bool
    file_path: Path
    file_exists: bool = False
    file_size_bytes: int = 0
    duration_ms: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get duration in seconds"""
        return self.duration_ms / 1000.0 if self.duration_ms is not None else None
    
    def has_errors(self) -> bool:
        """Check if validation has any errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if validation has any warnings"""
        return len(self.warnings) > 0


@dataclass 
class ValidationConfig:
    """Configuration for audio validation"""
    min_duration_seconds: float = 0.1  # Minimum audio duration
    max_duration_seconds: Optional[float] = None  # Maximum audio duration (None = no limit)
    min_file_size_bytes: int = 100  # Minimum file size in bytes
    allowed_formats: List[str] = None  # Allowed audio formats (None = any)
    require_metadata: bool = False  # Whether to require sample rate/channel info
    
    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = ['mp3', 'wav', 'ogg', 'm4a', 'flac']


def validate_audio_file(file_path: Path, config: ValidationConfig = None) -> AudioValidationResult:
    """
    Validate an audio file with comprehensive checks
    
    Args:
        file_path (Path): Path to the audio file to validate
        config (ValidationConfig): Validation configuration (uses defaults if None)
    
    Returns:
        AudioValidationResult: Detailed validation results
    """
    if config is None:
        config = ValidationConfig()
    
    result = AudioValidationResult(
        is_valid=True,
        file_path=file_path
    )
    
    # Check if validation is available
    if not VALIDATION_AVAILABLE:
        result.warnings.append("Audio validation libraries not available (pydub not installed)")
        return result
    
    try:
        # Check file existence
        if not file_path.exists():
            result.file_exists = False
            result.errors.append(f"Audio file does not exist: {file_path}")
            result.is_valid = False
            return result
        
        result.file_exists = True
        result.file_size_bytes = file_path.stat().st_size
        
        # Check minimum file size
        if result.file_size_bytes < config.min_file_size_bytes:
            result.errors.append(f"File too small: {result.file_size_bytes} bytes < {config.min_file_size_bytes} bytes")
            result.is_valid = False
        
        # Load and analyze audio
        try:
            audio = AudioSegment.from_file(str(file_path))
            
            # Extract audio properties
            result.duration_ms = len(audio)
            result.sample_rate = audio.frame_rate
            result.channels = audio.channels
            result.format = file_path.suffix.lower().lstrip('.')
            
            # Validate duration
            if result.duration_seconds < config.min_duration_seconds:
                result.errors.append(f"Audio too short: {result.duration_seconds:.3f}s < {config.min_duration_seconds}s")
                result.is_valid = False
            
            if config.max_duration_seconds and result.duration_seconds > config.max_duration_seconds:
                result.errors.append(f"Audio too long: {result.duration_seconds:.3f}s > {config.max_duration_seconds}s")
                result.is_valid = False
            
            # Validate format
            if result.format not in config.allowed_formats:
                result.errors.append(f"Unsupported format: {result.format}. Allowed: {config.allowed_formats}")
                result.is_valid = False
            
            # Check for silent audio
            if audio.max_possible_amplitude > 0:
                max_amplitude = audio.max
                if max_amplitude == 0:
                    result.warnings.append("Audio appears to be completely silent")
                elif max_amplitude < audio.max_possible_amplitude * 0.01:  # Less than 1% of max
                    result.warnings.append("Audio appears to be very quiet (possible generation issue)")
            
            # Metadata requirements
            if config.require_metadata:
                if not result.sample_rate:
                    result.errors.append("Sample rate information missing")
                    result.is_valid = False
                if not result.channels:
                    result.errors.append("Channel information missing") 
                    result.is_valid = False
                    
        except Exception as audio_error:
            result.errors.append(f"Failed to load/analyze audio: {audio_error}")
            result.is_valid = False
            
    except Exception as e:
        result.errors.append(f"Validation failed with unexpected error: {e}")
        result.is_valid = False
    
    return result


def validate_audio_properties(file_path: Path) -> Dict[str, Any]:
    """
    Extract basic audio properties without validation
    
    Args:
        file_path (Path): Path to audio file
        
    Returns:
        Dict with audio properties or error information
    """
    if not VALIDATION_AVAILABLE:
        return {"error": "Audio validation libraries not available"}
    
    if not file_path.exists():
        return {"error": f"File does not exist: {file_path}"}
    
    try:
        audio = AudioSegment.from_file(str(file_path))
        return {
            "duration_ms": len(audio),
            "duration_seconds": len(audio) / 1000.0,
            "sample_rate": audio.frame_rate,
            "channels": audio.channels,
            "format": file_path.suffix.lower().lstrip('.'),
            "file_size_bytes": file_path.stat().st_size,
            "max_amplitude": audio.max if audio.max_possible_amplitude > 0 else None
        }
    except Exception as e:
        return {"error": f"Failed to analyze audio: {e}"}


def quick_audio_check(file_path: Path) -> Tuple[bool, str]:
    """
    Quick validation check for basic audio file validity
    
    Args:
        file_path (Path): Path to audio file
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    result = validate_audio_file(file_path, ValidationConfig(min_duration_seconds=0.01))
    
    if result.is_valid:
        return True, ""
    else:
        # Return first error as the primary issue
        primary_error = result.errors[0] if result.errors else "Unknown validation error"
        return False, primary_error 