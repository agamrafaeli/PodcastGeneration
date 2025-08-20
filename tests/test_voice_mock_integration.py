#!/usr/bin/env python3
"""
Voice Integration Tests with Mock Engines
Tests Voice entity behavior using predictable mock engines
"""

import asyncio
import pytest
import sys
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.models import Voice
from tests.mocks import MockEngineFactory
from engines.core.types import ConversionParams


class TestVoiceIntegrationWithMocks:
    """Test Voice entity integration using mock engines for predictable testing"""
    
    @pytest.fixture
    def mock_engines(self, session_mock_engines):
        """Use session mock engines for better parallel performance"""
        return session_mock_engines
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_voice_integration_with_mocks(self, mock_engines):
        """
        Test that mock engines return proper Voice objects with all required fields
        This validates the Voice entity works correctly in the integration flow
        """
        for engine_name, engine in mock_engines.items():
            print(f"\n--- Testing mock {engine_name} integration ---")
            
            # Test that engine returns Voice objects via parse_voice_list
            voices = engine.parse_voice_list("")  # Mock ignores input
            
            # Verify we got voices back
            assert len(voices) > 0, f"Mock {engine_name}: Should return voices"
            print(f"✅ Mock {engine_name}: Found {len(voices)} voices")
            
            # Validate each voice object  
            for i, voice in enumerate(voices):
                # Check that voice is actually a Voice object
                assert isinstance(voice, Voice), f"Mock {engine_name}[{i}]: Expected Voice object, got {type(voice)}"
                
                # Check required fields are present and not None
                assert voice.id is not None, f"Mock {engine_name}[{i}]: Voice ID cannot be None"
                assert voice.name is not None, f"Mock {engine_name}[{i}]: Voice name cannot be None" 
                assert voice.language is not None, f"Mock {engine_name}[{i}]: Voice language cannot be None"
                
                # Check that required fields are not empty strings
                assert voice.id.strip() != "", f"Mock {engine_name}[{i}]: Voice ID cannot be empty"
                assert voice.name.strip() != "", f"Mock {engine_name}[{i}]: Voice name cannot be empty"
                assert voice.language.strip() != "", f"Mock {engine_name}[{i}]: Voice language cannot be empty"
                
                # Check engine field is correctly set
                assert voice.engine == engine_name, f"Mock {engine_name}[{i}]: Engine field mismatch"
                
                print(f"  ✅ Voice {i}: {voice.name} ({voice.language})")
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_voice_conversion_workflow_with_mocks(self, mock_engines):
        """
        Test that Voice objects work in conversion workflow using mock engines
        """
        test_text = "Hello, this is a test."
        
        for engine_name, engine in mock_engines.items():
            print(f"\n--- Testing mock {engine_name} conversion workflow ---")
            
            # Get voices from mock engine
            voices = engine.parse_voice_list("")
            assert len(voices) > 0, f"Mock {engine_name}: Should have voices for testing"
            
            # Test first voice
            test_voice = voices[0]
            output_path = Path(f"/tmp/test_mock_{engine_name}_{test_voice.id.replace('/', '_')}.mp3")
            
            print(f"Testing {engine_name} with voice: {test_voice.name}")
            
            # Test conversion using Voice.id
            try:
                params = ConversionParams(voice=test_voice.id)
                result = await engine.convert_text_to_speech(
                    text=test_text,
                    output_path=output_path,
                    params=params
                )
                
                if result:
                    print(f"✅ Mock {engine_name}: Voice '{test_voice.name}' conversion successful")
                    # Cleanup
                    if output_path.exists():
                        output_path.unlink()
                else:
                    print(f"❌ Mock {engine_name}: Conversion failed")
                    pytest.fail(f"Mock {engine_name} conversion should succeed")
                    
            except Exception as e:
                print(f"❌ Mock {engine_name}: Conversion error - {e}")
                pytest.fail(f"Mock {engine_name} conversion failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_voice_cross_mock_engine_consistency(self, mock_engines):
        """
        Test that all mock engines return consistently structured Voice objects
        """
        all_voices = {}
        
        for engine_name, engine in mock_engines.items():
            voices = engine.parse_voice_list("")
            all_voices[engine_name] = voices
        
        # Check that all engines have similar language coverage
        common_languages = {'en-US', 'es-ES', 'fr-FR'}  # Languages our mocks provide
        
        for engine_name, voices in all_voices.items():
            available_languages = {voice.language for voice in voices}
            overlap = common_languages.intersection(available_languages)
            
            print(f"Mock {engine_name}: Languages {available_languages}")
            assert len(overlap) >= 2, f"Mock {engine_name}: Should support multiple common languages"
        
        print("✅ All mock engines provide consistent language coverage")


if __name__ == "__main__":
    # Run tests directly if called as script
    import asyncio
    
    async def run_manual_tests():
        """Manual test runner for debugging"""
        test_instance = TestVoiceIntegrationWithMocks()
        mock_engines = MockEngineFactory.get_all_mock_engines()
        
        print("=== Mock Voice Integration Test ===")
        await test_instance.test_voice_integration_with_mocks(mock_engines)
        
        print("\n=== Mock Voice Conversion Workflow Test ===") 
        await test_instance.test_voice_conversion_workflow_with_mocks(mock_engines)
        
        print("\n=== Mock Voice Cross-Engine Consistency Test ===")
        await test_instance.test_voice_cross_mock_engine_consistency(mock_engines)
        
        print("\n✅ All mock integration tests completed!")
    
    asyncio.run(run_manual_tests()) 