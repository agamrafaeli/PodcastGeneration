#!/usr/bin/env python3
"""
Test for invalid voice selection error handling
"""

import asyncio
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tts.converter import TextToSpeechConverter


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.real_engine
@pytest.mark.integration
async def test_invalid_voice_selection():
    """
    Test that the CLI handles invalid voice names gracefully with the new explicit system:
    1. Provides a clear error message during parameter validation
    2. Lists available voices for the engine
    3. Exits with non-zero code (failure) 
    4. Doesn't crash or create empty files
    """
    # Create temp directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="tts_invalid_voice_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "test.txt"
    sample_file.write_text("Hello world. This is a test.")
    
    try:
        # Initialize converter to find available engines
        # Use Edge TTS since it has the most comprehensive voice validation
        converter = TextToSpeechConverter(engine_name="edge_tts", voice="valid-placeholder")
        await converter.initialize()
        
        available_engines = converter.get_available_engines()
        if "edge_tts" not in available_engines:
            print("❌ EdgeTTS not available for testing")
            return False
            
        print(f"🔧 Testing invalid voice with engine: edge_tts")
        
        # Use an obviously invalid voice name
        invalid_voice_name = "ThisVoiceDefinitelyDoesNotExist123"
        output_file = temp_path / "should_not_be_created.mp3"
        
        # Call CLI with invalid voice using new explicit parameter system
        # Only pass parameters that EdgeTTS supports
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent / "src" / "cli.py"),
            str(sample_file),
            "--engine", "edge_tts",  # Required explicit engine
            "-v", invalid_voice_name,  # Invalid voice (should cause validation failure)
            "-o", str(output_file)
        ]
        
        print(f"🎤 Testing with invalid voice: {invalid_voice_name}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Test expectations for proper error handling
        test_passed = True
        
        # 1. Should exit with non-zero code (indicating failure)
        if result.returncode == 0:
            print("❌ CLI should have failed but returned success (code 0)")
            test_passed = False
        else:
            print(f"✅ CLI properly failed with exit code: {result.returncode}")
        
        # 2. Should not create output file
        if output_file.exists():
            print("❌ Output file was created despite invalid voice")
            test_passed = False
        else:
            print("✅ No output file created (as expected)")
        
        # 3. Should provide meaningful error message about voice validation
        error_output = result.stderr.lower()
        stdout_output = result.stdout.lower()
        combined_output = error_output + stdout_output
        
        # Look for voice-specific validation errors
        voice_error_indicators = [
            "voice", "not available", "not found", 
            "parameter validation failed", "thisvoicedefinitelydoesnotexist123"
        ]
        
        has_voice_error = any(indicator in combined_output for indicator in voice_error_indicators)
        
        if not has_voice_error:
            print("❌ Error message doesn't mention voice validation issue")
            print(f"   Stderr: {result.stderr[:200]}")  # Show first 200 chars
            print(f"   Stdout: {result.stdout[:200]}")  # Show first 200 chars
            test_passed = False
        else:
            print("✅ Error message mentions voice validation issue")
        
        # 4. Should ideally list available voices (bonus check)
        if "available voices" in combined_output:
            print("✅ Bonus: Error message suggests available voices")
        else:
            print("ℹ️  Note: Could improve by listing available voices in error")
        
        print(f"\nFull error output:\n{result.stderr}")
        print(f"Full stdout output:\n{result.stdout}")
        
        return test_passed
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    result = asyncio.run(test_invalid_voice_selection())
    print(f"\n{'✅ Invalid voice test passed!' if result else '❌ Invalid voice test failed!'}")
    sys.exit(0 if result else 1) 