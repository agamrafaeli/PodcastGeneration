#!/usr/bin/env python3
"""
E2E test for basic prosody CLI integration
Tests that CLI prosody flags generate enhanced audio output
"""

import asyncio
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import os
import pytest

from tests.test_helpers import should_use_mock_engines, get_test_mode, validate_audio_and_print_info


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_prosody_cli_basic_enhancement():
    """
    Test that CLI with prosody flags generates enhanced audio output.
    
    This test verifies:
    1. CLI accepts prosody flags without error
    2. Generated audio file exists and has valid properties
    3. Prosody information is included in CLI output
    4. Text conversion completes successfully with prosody enhancement
    """
    # Create temporary directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="prosody_cli_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "prosody_test.txt"
    sample_text = "Breaking news: Scientists have discovered a new method for enhanced speech synthesis that makes artificial voices sound more natural and expressive."
    sample_file.write_text(sample_text)
    
    output_file = temp_path / "prosody_output.mp3"
    
    try:
        # Test basic prosody enhancement with newscast style
        # Set PYTHONPATH for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")
        
        cmd = [
            sys.executable,
            "-m", "cli",
            str(sample_file),
            "--engine", "edge_tts",
            "--prosody-style", "newscast",
            "--prosody-intensity", "3",
            "-o", str(output_file)
        ]
        
        # Run CLI command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        
        # Check command execution
        if result.returncode != 0:
            print(f"❌ CLI command failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            pytest.fail(f"CLI command failed with return code {result.returncode}")
        
        # Verify output file was created
        assert output_file.exists(), f"Output file not created: {output_file}"
        assert output_file.stat().st_size > 0, "Output file is empty"
        
        # Verify CLI output contains prosody information
        assert "🎭 Prosody Style: newscast" in result.stdout, "Prosody style not shown in output"
        assert "🎚️ Prosody Intensity: 3" in result.stdout, "Prosody intensity not shown in output"
        assert "✅ Conversion completed successfully!" in result.stdout, "Success message not found"
        
        # Validate audio file properties
        is_valid_audio = validate_audio_and_print_info(
            output_file, 
            test_name="Prosody CLI Basic Enhancement"
        )
        assert is_valid_audio, "Generated audio file failed validation"
        
        print("✅ Basic prosody CLI enhancement test passed!")
        return True
        
    except subprocess.TimeoutExpired:
        pytest.fail("CLI command timed out after 60 seconds")
    except Exception as e:
        pytest.fail(f"Unexpected error during prosody CLI test: {e}")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
@pytest.mark.e2e  
async def test_prosody_cli_dramatic_style():
    """
    Test CLI with dramatic prosody style for variety.
    
    Verifies that different prosody styles can be applied via CLI.
    """
    # Create temporary directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="prosody_dramatic_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "dramatic_test.txt"
    sample_text = "In the depths of the ancient forest, something extraordinary was about to unfold."
    sample_file.write_text(sample_text)
    
    output_file = temp_path / "dramatic_output.mp3"
    
    try:
        # Test dramatic prosody enhancement
        # Set PYTHONPATH for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")
        
        cmd = [
            sys.executable,
            "-m", "cli",
            str(sample_file),
            "--engine", "edge_tts", 
            "--prosody-style", "dramatic",
            "--prosody-intensity", "4",
            "-o", str(output_file)
        ]
        
        # Run CLI command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        
        # Check command execution
        if result.returncode != 0:
            print(f"❌ Dramatic prosody CLI command failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            pytest.fail(f"CLI command failed with return code {result.returncode}")
        
        # Verify output file and CLI information
        assert output_file.exists(), f"Output file not created: {output_file}"
        assert output_file.stat().st_size > 0, "Output file is empty"
        assert "🎭 Prosody Style: dramatic" in result.stdout, "Dramatic style not shown in output"
        assert "Applied prosody - Standard:" in result.stderr, "Prosody parameters not applied"
        assert "🎚️ Prosody Intensity: 4" in result.stdout, "Prosody intensity 4 not shown in output"
        
        # Validate audio file
        is_valid_audio = validate_audio_and_print_info(
            output_file,
            test_name="Prosody CLI Dramatic Style"
        )
        assert is_valid_audio, "Generated dramatic audio file failed validation"
        
        print("✅ Dramatic prosody CLI test passed!")
        return True
        
    except subprocess.TimeoutExpired:
        pytest.fail("Dramatic prosody CLI command timed out after 60 seconds")
    except Exception as e:
        pytest.fail(f"Unexpected error during dramatic prosody CLI test: {e}")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_prosody_cli_intensity_validation():
    """
    Test that CLI properly validates prosody intensity range (1-5).
    """
    # Create temporary directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="prosody_validation_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "validation_test.txt"
    sample_file.write_text("Test prosody intensity validation.")
    
    try:
        # Test invalid intensity (too high)
        # Set PYTHONPATH for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")
        
        cmd = [
            sys.executable,
            "-m", "cli",
            str(sample_file),
            "--engine", "edge_tts",
            "--prosody-style", "conversational", 
            "--prosody-intensity", "6",  # Invalid - too high
            "-o", str(temp_path / "test_output.mp3")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Should fail with validation error
        assert result.returncode != 0, "CLI should have failed with invalid intensity"
        assert "Invalid prosody intensity: 6. Must be between 1-5." in result.stdout, "Intensity validation error not shown"
        
        # Test invalid intensity (too low)
        cmd[cmd.index("6")] = "0"  # Change to invalid low value
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        assert result.returncode != 0, "CLI should have failed with invalid low intensity"
        assert "Invalid prosody intensity: 0. Must be between 1-5." in result.stdout, "Low intensity validation error not shown"
        
        print("✅ Prosody intensity validation test passed!")
        return True
        
    except subprocess.TimeoutExpired:
        pytest.fail("Prosody validation CLI command timed out")
    except Exception as e:
        pytest.fail(f"Unexpected error during prosody validation test: {e}")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio 
@pytest.mark.e2e
async def test_prosody_cli_without_flags():
    """
    Test that CLI works normally without prosody flags (no regression).
    """
    # Create temporary directory and sample file
    temp_dir = tempfile.mkdtemp(prefix="prosody_no_flags_test_")
    temp_path = Path(temp_dir)
    sample_file = temp_path / "no_prosody_test.txt"
    sample_file.write_text("This text should be processed without prosody enhancement.")
    
    output_file = temp_path / "no_prosody_output.mp3"
    
    try:
        # Test normal CLI operation without prosody flags
        # Set PYTHONPATH for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")
        
        cmd = [
            sys.executable,
            "-m", "cli",
            str(sample_file),
            "--engine", "pyttsx3",
            "-o", str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        
        # Should succeed normally
        if result.returncode != 0:
            print(f"❌ Non-prosody CLI command failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            pytest.fail(f"CLI command failed with return code {result.returncode}")
        
        # Verify output file was created and no prosody info in output
        assert output_file.exists(), f"Output file not created: {output_file}"
        assert output_file.stat().st_size > 0, "Output file is empty"
        assert "🎭 Prosody Style:" not in result.stdout, "Prosody style should not appear in output"
        assert "🎚️ Prosody Intensity:" not in result.stdout, "Prosody intensity should not appear in output"
        assert "✅ Conversion completed successfully!" in result.stdout, "Success message not found"
        
        print("✅ Non-prosody CLI operation test passed!")
        return True
        
    except subprocess.TimeoutExpired:
        pytest.fail("Non-prosody CLI command timed out after 60 seconds")
    except Exception as e:
        pytest.fail(f"Unexpected error during non-prosody CLI test: {e}")
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    async def run_tests():
        """Run all prosody CLI tests"""
        print("🧪 Running Prosody CLI E2E Tests...")
        
        tests = [
            test_prosody_cli_basic_enhancement(),
            test_prosody_cli_dramatic_style(),
            test_prosody_cli_intensity_validation(),
            test_prosody_cli_without_flags()
        ]
        
        results = []
        for i, test_coro in enumerate(tests, 1):
            try:
                print(f"\n--- Test {i}/{len(tests)} ---")
                result = await test_coro
                results.append(result)
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
                results.append(False)
        
        passed = sum(results)
        total = len(results)
        
        print(f"\n🏁 Test Results: {passed}/{total} passed")
        return passed == total
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
