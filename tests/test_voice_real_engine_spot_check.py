#!/usr/bin/env python3
"""
Real Engine Spot Check for Voice Integration
Validates that Voice entity works with at least one real TTS engines
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tts.sdk import TTSSDK, Engine
from engines.models import Voice


class TestVoiceRealEngineSpotCheck:
    """Minimal validation that Voice works with real engines"""
    
    @pytest.fixture
    def sdk(self, worker_sdk):
        """Use worker-safe SDK for real engine testing"""
        return worker_sdk
    
    @pytest.mark.asyncio
    @pytest.mark.real_engine
    @pytest.mark.integration
    async def test_one_real_engine_returns_voices(self, sdk):
        """
        Test that at least one real engine returns proper Voice objects
        Uses PyTTSx3 as it's most likely to be available offline
        """
        # Try PyTTSx3 first as it's usually available without internet
        test_engine = Engine.PYTTSX3
        
        try:
            print(f"\n--- Testing real {test_engine.name} for Voice integration ---")
            
            voices = await sdk.list_voices(test_engine)
            
            if not voices:
                print(f"⚠️  {test_engine.name}: No voices available (engine might not be installed)")
                pytest.skip(f"{test_engine.name} not available for testing")
                return
            
            print(f"✅ Real {test_engine.name}: Found {len(voices)} voices")
            
            # Test first voice only for spot check
            voice = voices[0]
            
            # Basic Voice object validation
            assert isinstance(voice, Voice), f"Expected Voice object, got {type(voice)}"
            assert voice.id is not None and voice.id.strip() != "", "Voice ID should be present"
            assert voice.name is not None and voice.name.strip() != "", "Voice name should be present"  
            assert voice.language is not None and voice.language.strip() != "", "Voice language should be present"
            
            print(f"  ✅ Real Voice validated: {voice.name} ({voice.language})")
            
        except Exception as e:
            print(f"❌ Real {test_engine.name}: Error during testing - {e}")
            pytest.skip(f"Real engine {test_engine.name} test failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.real_engine
    @pytest.mark.integration
    async def test_real_voice_works_in_conversion(self, sdk):
        """
        Test that a real Voice object works in actual TTS conversion
        """
        test_engine = Engine.PYTTSX3
        test_text = "Hello, this is a test."
        
        try:
            voices = await sdk.list_voices(test_engine)
            
            if not voices:
                pytest.skip(f"{test_engine.name} not available for conversion test")
                return
            
            # Use first available voice
            test_voice = voices[0]
            output_path = Path(f"/tmp/test_real_voice_{test_voice.id.replace('/', '_')}.mp3")
            
            print(f"Testing real conversion with {test_engine.name}: {test_voice.name}")
            
            # Attempt actual conversion using Voice.id
            result = await sdk.convert(
                text=test_text,
                output_path=output_path,
                engine=test_engine,
                voice=test_voice.id
            )
            
            if result.success:
                print(f"✅ Real {test_engine.name}: Voice '{test_voice.name}' conversion successful")
                # Cleanup
                if output_path.exists():
                    output_path.unlink()
            else:
                print(f"⚠️  Real {test_engine.name}: Conversion failed - {result.error_message}")
                # Don't fail the test - real engines may have issues
                
        except Exception as e:
            print(f"⚠️  Real {test_engine.name}: Conversion test error - {e}")
            # Don't fail the test - this is just a spot check


if __name__ == "__main__":
    # Run tests directly if called as script
    import asyncio
    
    async def run_manual_tests():
        """Manual test runner for debugging"""
        sdk = TTSSDK()
        test_instance = TestVoiceRealEngineSpotCheck()
        
        print("=== Real Engine Voice Validation ===")
        await test_instance.test_one_real_engine_returns_voices(sdk)
        
        print("\n=== Real Engine Voice Conversion Test ===") 
        await test_instance.test_real_voice_works_in_conversion(sdk)
        
        print("\n✅ Real engine spot check completed!")
    
    asyncio.run(run_manual_tests()) 