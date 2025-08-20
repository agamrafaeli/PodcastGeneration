#!/usr/bin/env python3
"""
E2E test for offline TTS models with random voice and language selection
"""

import asyncio
import subprocess
import sys
import random
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tts.converter import TextToSpeechConverter
from engines.core import EngineType


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.real_engine
@pytest.mark.e2e
async def test_offline_models_random_languages():
    """
    Single e2e test that:
    1. Gets offline models and their supported voices
    2. Picks a voice and language at random for each offline model
    3. Calls CLI with that voice
    4. Verifies no errors
    """
    # Create temp directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="tts_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "test.txt"
    sample_file.write_text("Hello world. This is a test of offline text to speech.")
    
    try:
        # Initialize converter to find offline engines
        # Use any valid engine name since it's required - we'll check all engines after initialization
        converter = TextToSpeechConverter(engine_name="pyttsx3", voice="default")
        await converter.initialize()
        
        # Get offline engines
        offline_engines = []
        for name, engine in converter.manager.engines.items():
            if engine.is_available and engine.engine_type == EngineType.OFFLINE:
                offline_engines.append((name, engine))
        
        if not offline_engines:
            print("❌ No offline engines available")
            return False
            
        print(f"🔧 Found offline engines: {[name for name, _ in offline_engines]}")
        
        # Test each offline engine
        all_passed = True
        for engine_name, engine in offline_engines:
            print(f"\n🎲 Testing {engine_name}...")
            
            # Get all available voices
            voices = await engine.list_voices()
            if not voices:
                print(f"⚠️  No voices for {engine_name}")
                continue
                
            # Pick a random voice
            random_voice = random.choice(voices)
            voice_name = random_voice.get('name', random_voice.get('id', 'unknown'))
            voice_language = random_voice.get('language', random_voice.get('Locale', 'unknown'))
            
            print(f"🎤 Selected random voice: {voice_name}")
            print(f"🌍 Voice language: {voice_language}")
            
            # Call CLI with the specific voice
            output_file = temp_path / f"output_{engine_name}.mp3"
            cmd = [
                sys.executable,
                str(Path(__file__).parent.parent / "src" / "cli.py"),
                str(sample_file),
                "--engine", engine_name,
                "-v", voice_name,
                "-o", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ CLI failed: {result.stderr}")
                all_passed = False
            elif not output_file.exists():
                print(f"❌ No output file created")
                all_passed = False
            elif output_file.stat().st_size == 0:
                print(f"❌ Empty output file")
                all_passed = False
            else:
                # Validate the generated audio file
                from .test_helpers import validate_audio_and_print_info
                
                if validate_audio_and_print_info(output_file, test_name="Generated audio"):
                    print(f"✅ Success!")
                else:
                    all_passed = False
        
        return all_passed
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    result = asyncio.run(test_offline_models_random_languages())
    print(f"\n{'✅ All tests passed!' if result else '❌ Some tests failed!'}")
    sys.exit(0 if result else 1) 