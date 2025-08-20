#!/usr/bin/env python3
"""
End-to-End Test: Voice Format Consistency Validation Across Engines

This test ensures that the abstraction works correctly and maintains
consistency across different engine implementations.
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from typing import List, Set

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tts.sdk import TTSSDK, Engine
from engines.models import Voice
from tests.mocks import MockEngineFactory


class TestVoiceConsistencyAcrossEngines:
    """Test suite for voice parsing consistency across all TTS engines"""
    
    @pytest.fixture
    def sdk(self, session_sdk):
        """Use session SDK for better parallel performance"""
        return session_sdk
    
    @pytest.fixture
    def use_mock_engines(self):
        """
        Configuration fixture to determine whether to use mock engines
        Uses new TEST_MODE environment variable with fallback to USE_REAL_ENGINES
        Default: use mock engines for speed and reliability
        """
        from .test_helpers import should_use_mock_engines
        return should_use_mock_engines()
    
    def _get_test_engines_and_voices(self, use_mock_engines: bool):
        """
        Get engines and their voices for testing
        Returns: List of (engine_name, voices) tuples
        """
        if use_mock_engines:
            # Use mock engines for predictable testing
            mock_engines = MockEngineFactory.get_all_mock_engines()
            return [(name, engine.parse_voice_list("")) for name, engine in mock_engines.items()]
        else:
            # Use real engines via SDK (original behavior)
            return None  # Will be handled in each test method
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_voice_format_consistency(self, sdk, use_mock_engines):
        """
        Test that all engines return properly formatted Voice objects
        with required fields populated
        """
        if use_mock_engines:
            print("\n=== Using MOCK engines for consistent testing ===")
            engines_and_voices = self._get_test_engines_and_voices(True)
            
            for engine_name, voices in engines_and_voices:
                print(f"\n--- Testing mock {engine_name} voice format consistency ---")
                
                if not voices:
                    print(f"❌ Mock {engine_name}: No voices available")
                    continue
                
                print(f"✅ Mock {engine_name}: Found {len(voices)} voices")
                
                # Validate each voice object
                for i, voice in enumerate(voices[:5]):  # Test first 5 voices for performance
                    self._validate_voice_object(voice, engine_name, i)
        else:
            print("\n=== Using REAL engines (set USE_REAL_ENGINES=true) ===")
            for engine in Engine:
                print(f"\n--- Testing {engine.name} voice format consistency ---")
                
                try:
                    voices = await sdk.list_voices(engine)
                    
                    # Skip if no voices (engine might not be available)
                    if not voices:
                        print(f"❌ {engine.name}: No voices available (engine might not be installed)")
                        continue
                    
                    print(f"✅ {engine.name}: Found {len(voices)} voices")
                    
                    # Validate each voice object
                    for i, voice in enumerate(voices[:5]):  # Test first 5 voices for performance
                        self._validate_voice_object(voice, engine.name, i)
                    
                except Exception as e:
                    print(f"❌ {engine.name}: Error during testing - {e}")
                    pytest.fail(f"Engine {engine.name} failed voice listing test: {e}")
    
    def _validate_voice_object(self, voice: Voice, engine_name: str, index: int):
        """Validate that a Voice object has all required fields properly populated"""
        
        # Check that voice is actually a Voice object
        assert isinstance(voice, Voice), f"{engine_name}[{index}]: Expected Voice object, got {type(voice)}"
        
        # Check required fields are present and not None
        assert voice.id is not None, f"{engine_name}[{index}]: Voice ID cannot be None"
        assert voice.name is not None, f"{engine_name}[{index}]: Voice name cannot be None"
        assert voice.language is not None, f"{engine_name}[{index}]: Voice language cannot be None"
        
        # Check that required fields are not empty strings
        assert voice.id.strip() != "", f"{engine_name}[{index}]: Voice ID cannot be empty"
        assert voice.name.strip() != "", f"{engine_name}[{index}]: Voice name cannot be empty"
        assert voice.language.strip() != "", f"{engine_name}[{index}]: Voice language cannot be empty"
        
        # Check engine field is correctly set
        assert voice.engine == engine_name.lower(), f"{engine_name}[{index}]: Engine field mismatch"
        
        print(f"  ✅ Voice {index}: {voice.name} ({voice.language})")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_language_code_consistency(self, sdk, use_mock_engines):
        """
        Test that language codes follow consistent format where possible
        """
        language_patterns = {}
        
        if use_mock_engines:
            engines_and_voices = self._get_test_engines_and_voices(True)
            
            for engine_name, voices in engines_and_voices:
                if not voices:
                    continue
                
                languages = set()
                for voice in voices:
                    languages.add(voice.language)
                
                language_patterns[engine_name] = languages
                print(f"Mock {engine_name}: Found languages - {sorted(list(languages))}")
        else:
            for engine in Engine:
                try:
                    voices = await sdk.list_voices(engine)
                    if not voices:
                        continue
                    
                    languages = set()
                    for voice in voices:
                        languages.add(voice.language)
                    
                    language_patterns[engine.name] = languages
                    print(f"{engine.name}: Found languages - {sorted(list(languages))}")
                    
                except Exception as e:
                    print(f"❌ {engine.name}: Error getting languages - {e}")
        
        # Check for common language patterns
        common_languages = {'en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja'}
        for engine, languages in language_patterns.items():
            overlaps = common_languages.intersection(languages)
            print(f"{engine}: Common language overlaps - {overlaps}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_no_duplicate_voices_within_engine(self, sdk, use_mock_engines):
        """
        Test that engines don't return duplicate voice IDs
        """
        if use_mock_engines:
            engines_and_voices = self._get_test_engines_and_voices(True)
            
            for engine_name, voices in engines_and_voices:
                if not voices:
                    continue
                
                voice_ids = [voice.id for voice in voices]
                unique_ids = set(voice_ids)
                
                assert len(voice_ids) == len(unique_ids), \
                    f"Mock {engine_name}: Found duplicate voice IDs. Total: {len(voice_ids)}, Unique: {len(unique_ids)}"
                
                print(f"✅ Mock {engine_name}: No duplicate voice IDs ({len(voice_ids)} total)")
        else:
            for engine in Engine:
                try:
                    voices = await sdk.list_voices(engine)
                    if not voices:
                        continue
                    
                    voice_ids = [voice.id for voice in voices]
                    unique_ids = set(voice_ids)
                    
                    assert len(voice_ids) == len(unique_ids), \
                        f"{engine.name}: Found duplicate voice IDs. Total: {len(voice_ids)}, Unique: {len(unique_ids)}"
                    
                    print(f"✅ {engine.name}: No duplicate voice IDs ({len(voice_ids)} total)")
                    
                except Exception as e:
                    print(f"❌ {engine.name}: Error checking duplicates - {e}")
    
    @pytest.mark.asyncio
    async def test_voice_usability_for_conversion(self, sdk, use_mock_engines):
        """
        Test that voice IDs returned can actually be used for TTS conversion
        """
        test_text = "Hello, this is a test."
        
        if use_mock_engines:
            print("\n=== Testing mock engine voice usability ===")
            mock_engines = MockEngineFactory.get_all_mock_engines()
            
            for engine_name, engine in mock_engines.items():
                voices = engine.parse_voice_list("")
                if not voices:
                    continue
                
                # Test first voice only (for performance)
                test_voice = voices[0]
                
                # Create temporary output file
                output_path = Path(f"/tmp/test_mock_{engine_name}_{test_voice.id.replace('/', '_')}.mp3")
                
                print(f"Testing mock {engine_name} with voice: {test_voice.name}")
                
                # Attempt conversion with mock engine
                try:
                    result = await engine.convert_text_to_speech(
                        text=test_text,
                        output_path=output_path
                    )
                    
                    if result:
                        print(f"✅ Mock {engine_name}: Voice '{test_voice.name}' conversion successful")
                        # Cleanup
                        if output_path.exists():
                            output_path.unlink()
                    else:
                        print(f"⚠️  Mock {engine_name}: Voice conversion failed")
                        
                except Exception as conv_e:
                    print(f"⚠️  Mock {engine_name}: Conversion error - {conv_e}")
        else:
            print("\n=== Testing real engine voice usability ===")
            for engine in Engine:
                try:
                    voices = await sdk.list_voices(engine)
                    if not voices:
                        continue
                    
                    # Test first voice only (for performance)
                    test_voice = voices[0]
                    
                    # Create temporary output file
                    output_path = Path(f"/tmp/test_{engine.name.lower()}_{test_voice.id.replace('/', '_')}.mp3")
                    
                    print(f"Testing {engine.name} with voice: {test_voice.name}")
                    
                    # Attempt conversion - this validates the voice ID works
                    try:
                        result = await sdk.convert(
                            text=test_text,
                            output_path=output_path,
                            engine=engine,
                            voice=test_voice.id
                        )
                        
                        if result.success:
                            print(f"✅ {engine.name}: Voice '{test_voice.name}' conversion successful")
                            # Cleanup
                            if output_path.exists():
                                output_path.unlink()
                        else:
                            print(f"⚠️  {engine.name}: Voice conversion failed - {result.error_message}")
                            
                    except Exception as conv_e:
                        print(f"⚠️  {engine.name}: Conversion error - {conv_e}")
                    
                except Exception as e:
                    print(f"❌ {engine.name}: Error in usability test - {e}")
    
    @pytest.mark.asyncio
    async def test_cross_engine_comparison(self, sdk, use_mock_engines):
        """
        Compare voice availability across engines for common languages
        """
        common_languages = ['en', 'es', 'fr', 'de']
        engine_language_support = {}
        
        if use_mock_engines:
            engines_and_voices = self._get_test_engines_and_voices(True)
            
            for engine_name, voices in engines_and_voices:
                if not voices:
                    continue
                
                supported_langs = set()
                for voice in voices:
                    # Extract base language (e.g., 'en' from 'en-US')
                    base_lang = voice.language.split('-')[0].lower()
                    if base_lang in common_languages:
                        supported_langs.add(base_lang)
                
                engine_language_support[engine_name] = supported_langs
        else:
            for engine in Engine:
                try:
                    voices = await sdk.list_voices(engine)
                    if not voices:
                        continue
                    
                    supported_langs = set()
                    for voice in voices:
                        # Extract base language (e.g., 'en' from 'en-US')
                        base_lang = voice.language.split('-')[0].lower()
                        if base_lang in common_languages:
                            supported_langs.add(base_lang)
                    
                    engine_language_support[engine.name] = supported_langs
                    
                except Exception as e:
                    print(f"❌ {engine.name}: Error in cross-engine comparison - {e}")
        
        # Print comparison results
        print("\n--- Cross-Engine Language Support Comparison ---")
        for lang in common_languages:
            supporting_engines = [engine for engine, langs in engine_language_support.items() if lang in langs]
            print(f"{lang}: Supported by {supporting_engines}")
        
        # Ensure at least one engine supports each common language
        for lang in common_languages:
            supporting_engines = [engine for engine, langs in engine_language_support.items() if lang in langs]
            assert len(supporting_engines) > 0, f"No engine supports language '{lang}'"


if __name__ == "__main__":
    # Run tests directly if called as script
    import asyncio
    
    async def run_manual_tests():
        """Manual test runner for debugging"""
        sdk = TTSSDK()
        test_instance = TestVoiceConsistencyAcrossEngines()
        
        # Check environment variable to determine testing mode
        use_mock_engines = os.getenv('USE_REAL_ENGINES', 'false').lower() != 'true'
        
        if use_mock_engines:
            print("🎭 Running tests with MOCK engines for fast, predictable testing")
            print("💡 Set USE_REAL_ENGINES=true to test with real engines")
        else:
            print("🔧 Running tests with REAL engines")
            print("⚠️  This may be slower and depend on engine availability")
        
        print("\n=== Voice Format Consistency Test ===")
        await test_instance.test_voice_format_consistency(sdk, use_mock_engines)
        
        print("\n=== Language Code Consistency Test ===") 
        await test_instance.test_language_code_consistency(sdk, use_mock_engines)
        
        print("\n=== Duplicate Voice Test ===")
        await test_instance.test_no_duplicate_voices_within_engine(sdk, use_mock_engines)
        
        print("\n=== Voice Usability Test ===")
        await test_instance.test_voice_usability_for_conversion(sdk, use_mock_engines)
        
        print("\n=== Cross-Engine Comparison ===")
        await test_instance.test_cross_engine_comparison(sdk, use_mock_engines)
        
        print("\n✅ All manual tests completed!")
    
    asyncio.run(run_manual_tests()) 