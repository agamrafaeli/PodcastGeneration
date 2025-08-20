#!/usr/bin/env python3
"""
E2E test for voice sample generation functionality
Tests the SDK voice sampling method to ensure it generates audio files with different engines
"""

import asyncio
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tts.sdk import TTSSDK
from .test_helpers import should_use_mock_engines, get_test_mode
from .mocks import MockTTSSDK


class TestVoiceSampleGeneration:
    """Test suite for voice sample generation functionality"""
    
    @pytest.fixture
    def sdk(self, session_sdk):
        """Use session SDK for better parallel performance"""
        return session_sdk

    @pytest.fixture
    def temp_dir(self, isolated_temp_dir):
        """Use isolated temp directory for parallel-safe testing"""
        return isolated_temp_dir

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_voice_sample_generation_basic(self, sdk, temp_dir):
        """
        Test that voice sample generation:
        1. Generates a single consolidated audio file successfully
        2. Uses different engines (at least 2 different engines)
        3. Creates file with reasonable size
        4. Returns proper result structure
        """
        test_text = "This is a test sentence for voice comparison across multiple engines."
        
        # Change to temp directory for isolated testing
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            print(f"🧪 Testing voice samples with text: {test_text[:50]}...")
            
            # Generate voice samples
            result = await sdk.generate_voice_samples(test_text)
            
            # Verify operation succeeded
            assert result.success, f"Voice sample generation failed: {result.error_message}"
            
            # Verify we have at least 2 samples included
            assert result.samples_generated >= 2, f"Expected at least 2 samples, got {result.samples_generated}"
            
            # Verify output directory exists
            assert result.output_directory is not None, "Output directory not set"
            assert result.output_directory.exists(), f"Output directory {result.output_directory} doesn't exist"
            
            # Verify consolidated file exists and is non-empty
            assert result.consolidated_file is not None, "Consolidated file not set"
            assert result.consolidated_file.exists(), f"Consolidated file {result.consolidated_file} doesn't exist"
            
            file_size = result.consolidated_file.stat().st_size
            assert file_size > 5000, f"Consolidated file {result.consolidated_file.name} is too small ({file_size} bytes)"
            print(f"📁 {result.consolidated_file.name}: {file_size:,} bytes")
            
            # Validate the consolidated audio file
            from .test_helpers import assert_valid_audio_with_preset
            assert_valid_audio_with_preset(result.consolidated_file, "medium_audio")
            
            # Verify we have different engines
            assert len(result.engines_used) >= 2, f"Expected at least 2 different engines, got {result.engines_used}"
            
            # Verify duration is reasonable
            assert result.total_duration_seconds > 0, f"Duration should be positive, got {result.total_duration_seconds}"
            print(f"⏱️ Duration: {result.total_duration_seconds:.1f} seconds")
            print(f"🎛️ Engines: {result.engines_used}")
            print(f"📊 Samples: {result.samples_generated}")
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_voice_sample_generation_short_text(self, sdk, temp_dir):
        """Test voice sample generation with very short text"""
        test_text = "Hello world!"
        
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            print(f"🧪 Testing short text: {test_text}")
            
            result = await sdk.generate_voice_samples(test_text)
            
            assert result.success, f"Short text sample generation failed: {result.error_message}"
            assert result.consolidated_file is not None and result.consolidated_file.exists()
            
            file_size = result.consolidated_file.stat().st_size
            assert file_size > 1000, f"Even short text should produce reasonable audio size, got {file_size} bytes"
            
            # Validate short audio
            from .test_helpers import assert_valid_audio_with_preset
            assert_valid_audio_with_preset(result.consolidated_file, "short_audio")
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_voice_sample_generation_long_text(self, sdk, temp_dir):
        """Test voice sample generation with longer text to verify proper text splitting"""
        test_text = """
        This is a much longer text sample that should be split intelligently across multiple voice samples.
        The system should handle text splitting gracefully and create distinct samples for each voice engine.
        This allows users to compare how different voices handle longer passages and make informed decisions
        about which voice works best for their specific use case and content type.
        """
        
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            print(f"🧪 Testing long text: {len(test_text)} characters")
            
            result = await sdk.generate_voice_samples(test_text)
            
            assert result.success, f"Long text sample generation failed: {result.error_message}"
            assert result.consolidated_file is not None and result.consolidated_file.exists()
            
            file_size = result.consolidated_file.stat().st_size
            # Longer text should produce larger audio files
            assert file_size > 8000, f"Long text should produce larger audio, got {file_size} bytes"
            
            # Validate long audio  
            from .test_helpers import assert_valid_audio_with_preset
            assert_valid_audio_with_preset(result.consolidated_file, "long_audio")
            
            # Duration should be longer for more text
            assert result.total_duration_seconds > 10, f"Long text should have longer duration, got {result.total_duration_seconds}"
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_voice_sample_result_structure(self, sdk, temp_dir):
        """Test that VoiceSampleResult structure is properly populated"""
        test_text = "Testing the result structure and data validation."
        
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = await sdk.generate_voice_samples(test_text)
            
            assert result.success is True
            assert isinstance(result.consolidated_file, Path)
            assert isinstance(result.output_directory, Path) 
            assert isinstance(result.engines_used, list)
            assert isinstance(result.samples_generated, int)
            assert isinstance(result.total_duration_seconds, (int, float))
            assert result.error_message is None
            
            # Verify consolidated file path structure
            assert result.consolidated_file.name == "voice_samples_consolidated.mp3"
            assert result.output_directory.name == "voice_samples"
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    # Allow running this test directly
    import asyncio
    import sys
    
    async def run_tests():
        sdk = TTSSDK(timeout=60.0)
        temp_dir = Path(tempfile.mkdtemp(prefix="tts_voice_sample_direct_test_"))
        
        try:
            test_instance = TestVoiceSampleGeneration()
            await test_instance.test_voice_sample_generation_basic(sdk, temp_dir)
            await test_instance.test_voice_sample_generation_short_text(sdk, temp_dir)
            print("✅ All direct tests passed!")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up {temp_dir}: {e}")
    
    asyncio.run(run_tests()) 