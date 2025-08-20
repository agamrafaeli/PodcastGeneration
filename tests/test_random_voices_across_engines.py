#!/usr/bin/env python3
"""
Test for random voice selection across all available engines
Uses TTSClient SDK for clean, engine-agnostic testing
"""

import asyncio
import random
import tempfile
import shutil
import sys
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tts.sdk import TTSSDK, Engine
from .test_helpers import should_use_mock_engines, get_test_mode
from .mocks import MockTTSSDK


@pytest.mark.asyncio
@pytest.mark.integration
async def test_random_voices_across_engines():
    """Test text conversion using random voices from each available engine"""
    test_text = "Hello world. Comprehensive TTS engine test across multiple voices."
    temp_dir = Path(tempfile.mkdtemp(prefix="tts_test_"))
    
    try:
        print(f"🧪 Testing: {test_text}")
        
        # Use mock or real SDK based on TEST_MODE
        if should_use_mock_engines():
            print(f"🎭 Using MOCK engines (TEST_MODE={get_test_mode()})")
            client_class = MockTTSSDK
        else:
            print(f"🎤 Using REAL engines (TEST_MODE={get_test_mode()})")
            client_class = TTSSDK
        
        async with client_class() as client:
            # Get available engines
            engines = await client.get_available_engines()
            if not engines:
                pytest.skip("No TTS engines available")
            
            print(f"🔧 Testing {len(engines)} engines: {[e.value for e in engines]}")
            
            # Test all engines in parallel
            tasks = [_test_engine(client, engine, test_text, temp_dir) for engine in engines]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            total = len(engines)
            min_required = max(1, total // 2)
            
            print(f"📊 Results: {successful}/{total} engines succeeded")
            for i, result in enumerate(results):
                if isinstance(result, dict) and result.get('success'):
                    print(f"   ✅ {result['engine']} + {result['voice'][:30]}")
                else:
                    print(f"   ❌ {engines[i].value} failed")
            
            assert successful >= min_required, f"Only {successful}/{total} succeeded (need ≥{min_required})"
            print(f"🎉 TEST PASSED: {successful}/{total} engines")
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def _test_engine(client: TTSSDK, engine: Engine, test_text: str, temp_dir: Path) -> dict:
    """Test single engine with random voice"""
    try:
        # Get voices and select random one
        voices = await client.list_voices(engine)
        if not voices:
            return {'success': False, 'engine': engine.value, 'error': 'no voices'}
        
        voice = random.choice(voices)
        output_file = temp_dir / f"{engine.value}_{voice.id[:8]}.mp3"
        
        # Convert text to speech
        result = await client.convert(
            text=test_text,
            output_path=output_file,
            engine=engine,
            voice=voice.id
        )
        
        return {
            'success': result.success,
            'engine': engine.value,
            'voice': voice.name,
            'size': result.file_size,
            'error': result.error_message if not result.success else None
        }
        
    except Exception as e:
        return {'success': False, 'engine': engine.value, 'error': str(e)}


if __name__ == "__main__":
    asyncio.run(test_random_voices_across_engines()) 