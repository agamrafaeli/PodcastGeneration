#!/usr/bin/env python3
"""
Command-line interface for Text-to-Speech conversion
Now with required explicit engine selection and parameter validation
"""

import asyncio
import argparse
import sys
import shutil
import os
from pathlib import Path
from typing import Optional

from config import logger, DEFAULT_VOICE, DEFAULT_RATE, DEFAULT_PITCH, DEFAULT_MAX_CONCURRENT
from tts.converter import TextToSpeechConverter

import logging
import tempfile
from pydub import AudioSegment
from pydub.silence import split_on_silence


def cleanup_all_generated():
    """Remove all files from generated/ directory"""
    generated_dir = Path("generated")
    if not generated_dir.exists():
        print("Generated directory doesn't exist.")
        return
    
    file_count = 0
    for item in generated_dir.rglob("*"):
        if item.is_file():
            file_count += 1
            item.unlink()
    
    # Remove empty directories
    for item in generated_dir.rglob("*"):
        if item.is_dir() and not any(item.iterdir()):
            item.rmdir()
    
    print(f"✅ Cleaned up generated directory: {file_count} files removed")


def cleanup_temp_files():
    """Remove files with 'temp' or 'test' in their names from generated/"""
    generated_dir = Path("generated")
    if not generated_dir.exists():
        print("Generated directory doesn't exist.")
        return
    
    removed_count = 0
    for item in generated_dir.rglob("*"):
        if item.is_file() and ('temp' in item.name.lower() or 'test' in item.name.lower()):
            item.unlink()
            removed_count += 1
    
    print(f"✅ Temp/test cleanup completed: {removed_count} files removed")


def show_disk_usage():
    """Show disk usage of audio directories"""
    dirs_to_check = ["generated", "."]
    
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if not path.exists():
            continue
            
        total_size = 0
        file_count = 0
        
        for item in path.rglob("*"):
            if item.is_file() and item.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                total_size += item.stat().st_size
                file_count += 1
        
        if file_count > 0:
            size_mb = total_size / (1024 * 1024)
            print(f"📁 {dir_path}: {file_count} audio files, {size_mb:.1f} MB")


def one_line_cleanup():
    """Delete all files/folders with 'temp' or 'test' in name (everywhere)"""
    print("⚠️  One-line cleanup: Searching for temp/test files...")
    
    current_dir = Path(".")
    total_cleaned = 0
    
    for item in current_dir.rglob("*"):
        try:
            if 'temp' in item.name.lower() or 'test' in item.name.lower():
                if item.is_file():
                    item.unlink()
                    total_cleaned += 1
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    total_cleaned += 1
        except:
            continue  # Skip files we can't access
    
    print(f"✅ One-line cleanup completed: {total_cleaned} items removed")


def split_text_for_samples(text: str, num_samples: int = 3) -> list[str]:
    """
    Split text into samples for voice comparison
    Uses basic truncation - first N words for each sample
    
    Args:
        text (str): Input text to split
        num_samples (int): Number of samples to create
        
    Returns:
        list[str]: List of text samples
    """
    words = text.split()
    if len(words) <= 10:
        # If text is short, use the same text for all samples
        return [text] * num_samples
    
    # Calculate words per sample (with some overlap for natural flow)
    total_words = len(words)
    words_per_sample = max(10, total_words // num_samples)
    
    samples = []
    for i in range(num_samples):
        start_idx = i * (words_per_sample // 2)  # 50% overlap
        end_idx = min(start_idx + words_per_sample, total_words)
        
        if start_idx >= total_words:
            # If we've run out of text, use the last portion
            sample_text = " ".join(words[-words_per_sample:])
        else:
            sample_text = " ".join(words[start_idx:end_idx])
        
        samples.append(sample_text)
    
    return samples


def select_sample_voices() -> list[dict]:
    """
    Select 3 different voices from available engines for sampling
    
    Returns:
        list[dict]: List of voice configurations with engine and voice info
    """
    # Use default configurations without specifying specific voices
    # This allows each engine to use its default voice
    voice_configs = [
        {"engine": "edge_tts"},  # Will use default Edge TTS voice
        {"engine": "gtts", "language": "en"},  # gTTS with English
        {"engine": "pyttsx3"}  # Will use default pyttsx3 voice
    ]
    
    return voice_configs


async def handle_voice_sample(text: str):
    """
    Handle the voice sample generation command - Phase 2 Implementation
    Generates a single consolidated MP3 with narrator labels
    
    Args:
        text (str): Input text to use for samples
    """
    print(f"🎤 Generating consolidated voice samples for: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Split text into samples
    text_samples = split_text_for_samples(text, 3)
    logger.info(f"Split text into {len(text_samples)} samples")
    
    # Select voices
    voice_configs = select_sample_voices()
    
    # Create output directory
    generated_dir = Path("generated/voice_samples")
    generated_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary directory for individual samples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        narrator_files = []
        sample_files = []
        
        try:
            # Generate narrator voice clips
            narrator_converter = TextToSpeechConverter(engine_name='edge_tts')  # Use default voice
            
            for i, label in enumerate(["One", "Two", "Three"], 1):
                print(f"🔄 Generating narrator label '{label}'...")
                narrator_file = temp_path / f"narrator_{i}.mp3"
                await narrator_converter.convert_text_to_speech(f"{label}:", narrator_file)
                narrator_files.append(narrator_file)
                print(f"✅ Narrator '{label}' completed")
            
            # Generate voice samples
            successful_samples = 0
            for i, (sample_text, voice_config) in enumerate(zip(text_samples, voice_configs), 1):
                try:
                    print(f"🔄 Generating voice sample {i}/3 with {voice_config['engine']}...")
                    
                    # Create converter with specific configuration
                    converter_kwargs = {
                        'engine_name': voice_config['engine'],
                    }
                    
                    if voice_config.get('voice'):
                        converter_kwargs['voice'] = voice_config['voice']
                    if voice_config.get('language'):
                        converter_kwargs['language'] = voice_config['language']
                    
                    converter = TextToSpeechConverter(**converter_kwargs)
                    
                    # Generate to temporary file
                    sample_file = temp_path / f"sample_{i}_{voice_config['engine']}.mp3"
                    await converter.convert_text_to_speech(sample_text, sample_file)
                    
                    sample_files.append(sample_file)
                    print(f"✅ Sample {i} completed with {voice_config['engine']}")
                    successful_samples += 1
                    
                except Exception as e:
                    print(f"❌ Sample {i} failed with {voice_config['engine']}: {e}")
                    logger.error(f"Voice sample {i} failed: {e}")
                    sample_files.append(None)  # Placeholder for failed sample
            
            if successful_samples == 0:
                print("❌ All voice samples failed to generate")
                return
            
            # Concatenate audio files using pydub
            print("🎵 Concatenating audio files...")
            final_audio = AudioSegment.empty()
            silence = AudioSegment.silent(duration=1000)  # 1 second silence
            
            for i, (narrator_file, sample_file) in enumerate(zip(narrator_files, sample_files)):
                if sample_file and sample_file.exists():
                    try:
                        # Add narrator label
                        if narrator_file.exists():
                            narrator_audio = AudioSegment.from_mp3(str(narrator_file))
                            final_audio += narrator_audio + AudioSegment.silent(duration=500)  # 0.5s pause after narrator
                        
                        # Add voice sample
                        sample_audio = AudioSegment.from_mp3(str(sample_file))
                        final_audio += sample_audio
                        
                        # Add spacing between samples (except after the last one)
                        if i < len(narrator_files) - 1:
                            final_audio += silence
                        
                        print(f"✅ Added sample {i+1} to consolidated audio")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not add sample {i+1} to consolidated audio: {e}")
                        logger.warning(f"Failed to add sample {i+1}: {e}")
            
            # Export final consolidated MP3
            output_file = generated_dir / "voice_samples_consolidated.mp3"
            final_audio.export(str(output_file), format="mp3")
            
            print(f"🎯 Consolidated voice samples completed!")
            print(f"📁 Output file: {output_file}")
            print(f"📊 Duration: {len(final_audio) / 1000:.1f} seconds")
            print(f"🔢 Samples included: {successful_samples}/3")
            
        except Exception as e:
            print(f"❌ Consolidation failed: {e}")
            logger.error(f"Voice sample consolidation failed: {e}")
            # Fallback: show where individual files would have been
            print(f"📁 Individual samples would be in: {generated_dir}")


async def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Convert text files to audio using TTS engines with explicit parameter control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic conversion with Edge TTS and specific voice
    python src/cli.py script.txt --engine edge_tts -v "en-US-JennyNeural"
    
    # Use gTTS with language parameter
    python src/cli.py script.txt --engine gtts -l en
    python src/cli.py script.txt --engine gtts -l fr --slow
    
    # Use pyttsx3 with specific voice and rate
    python src/cli.py script.txt --engine pyttsx3 -v "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0" --rate-int 250
    
    # Adjust Edge TTS speech rate and pitch
    python src/cli.py script.txt --engine edge_tts -v "en-US-AriaNeural" -r "+25%" -p "+2Hz"
    
    # Enhanced prosody examples (uses optimal method per engine automatically)
    python src/cli.py script.txt --engine edge_tts --prosody-style newscast --prosody-intensity 3
    python src/cli.py script.txt --engine edge_tts --prosody-style dramatic --prosody-intensity 4
    
    # Prosody discovery commands
    python src/cli.py --prosody-list
    python src/cli.py --prosody-info dramatic
    
    # List voices for specific engine
    python src/cli.py --engine edge_tts --list-voices
    python src/cli.py --engine pyttsx3 --list-voices
    python src/cli.py --engine gtts --list-voices
    
    # Get engine information
    python src/cli.py --engine edge_tts --engine-info
    
    # Generate voice samples (no engine selection needed)
    python src/cli.py --voice-sample "Hello world, this is a test sentence for voice comparison."
    
    # Cleanup commands (unchanged)
    python src/cli.py --cleanup-all
    python src/cli.py --cleanup-temp
        """
    )
    
    parser.add_argument("input_file", nargs="?", help="Input text file path")
    parser.add_argument("--engine", choices=['edge_tts', 'gtts', 'pyttsx3'],
                       help="TTS engine to use (REQUIRED for conversions, optional for voice sampling)")
    parser.add_argument("-o", "--output", help="Output audio file path (default: generated/input_filename.mp3)")
    
    # Voice/Language parameters (engine-dependent)
    parser.add_argument("-v", "--voice", help="Voice name/ID to use (engine-specific)")
    parser.add_argument("-l", "--language", help="Language code (e.g., 'en', 'fr') - mainly for gTTS")
    
    # Rate parameters (engine-dependent)
    parser.add_argument("-r", "--rate", help="Speech rate for EdgeTTS (e.g., '+50%%', '-25%%')")
    parser.add_argument("--rate-int", type=int, help="Speech rate for pyttsx3 (words per minute, e.g., 200)")
    
    # Other parameters (engine-dependent) 
    parser.add_argument("-p", "--pitch", help="Pitch adjustment for EdgeTTS (e.g., '+10Hz', '-5Hz')")
    parser.add_argument("--volume", type=float, help="Volume for pyttsx3 (0.0-1.0)")
    parser.add_argument("--slow", action="store_true", help="Slow speech for gTTS")
    
    # Prosody enhancement parameters (unified interface)
    parser.add_argument("--prosody-style", help="Prosody style for enhanced speech synthesis (e.g., 'newscast', 'conversational', 'dramatic')")
    parser.add_argument("--prosody-intensity", type=int, metavar="1-5", help="Prosody style intensity level (1=subtle, 3=normal, 5=dramatic)")
    
    # Prosody discovery commands  
    parser.add_argument("--prosody-list", action="store_true", help="List all available prosody styles")
    parser.add_argument("--prosody-info", metavar="STYLE", help="Show detailed information about a specific prosody style")
    
    # Information commands
    parser.add_argument("--list-voices", action="store_true", help="List voices for specified engine")
    parser.add_argument("--engine-info", action="store_true", help="Show information about specified engine")
    
    # Voice sampling command
    parser.add_argument("--voice-sample", metavar="TEXT", help="Generate 3 audio samples with different voices using provided text")
    
    # Cleanup commands (unchanged)
    parser.add_argument("--cleanup-all", action="store_true",
                       help="Remove all files from generated/ directory")
    parser.add_argument("--cleanup-temp", action="store_true", 
                       help="Remove files with 'temp' or 'test' in their names")
    parser.add_argument("--disk-usage", action="store_true",
                       help="Show disk usage of audio directories")
    parser.add_argument("--one-line-cleanup", action="store_true",
                       help="Delete all files/folders with 'temp' or 'test' in name (everywhere)")
    
    args = parser.parse_args()
    
    # Handle cleanup commands (no engine required)
    if args.cleanup_all:
        cleanup_all_generated()
        return
    
    if args.cleanup_temp:
        cleanup_temp_files()
        return
    
    if args.disk_usage:
        show_disk_usage()
        return
        
    if args.one_line_cleanup:
        one_line_cleanup()
        return
    
    # Handle voice sampling command (no engine required)
    if args.voice_sample:
        await handle_voice_sample(args.voice_sample)
        return
    
    # Handle prosody discovery commands (no engine required)
    if args.prosody_list:
        from prosody import list_styles
        styles = list_styles()
        print(f"\n🎭 Available prosody styles ({len(styles)} total):")
        for i, style in enumerate(styles, 1):
            from prosody import get_style_info
            style_info = get_style_info(style)
            description = style_info.get('description', 'No description') if style_info else 'No description'
            print(f"  {i:2}. {style:<15} - {description}")
        print("\nUse --prosody-info STYLE for detailed information about a specific style.")
        return
    
    if args.prosody_info:
        from prosody import get_style_info, list_styles
        style_info = get_style_info(args.prosody_info)
        if not style_info:
            print(f"❌ Unknown prosody style: '{args.prosody_info}'")
            print(f"Available styles: {', '.join(list_styles())}")
            return
        
        print(f"\n🎭 Prosody Style: {args.prosody_info}")
        print(f"📝 Description: {style_info.get('description', 'No description')}")
        
        params = style_info.get('parameters', {})
        if params:
            print("⚙️  Parameters:")
            for param, value in params.items():
                print(f"   • {param}: {value}")
        
        use_cases = style_info.get('use_cases', [])
        if use_cases:
            print("💡 Use cases:")
            for use_case in use_cases:
                print(f"   • {use_case}")
        
        # Show engine support (hardcoded since prosody is now engine-agnostic)
        engine_support = {
            'edge_tts': ['rate', 'pitch'],
            'gtts': ['rate (slow only)'],
            'pyttsx3': ['rate', 'volume']
        }
        print("🔧 Engine support:")
        for engine, features in engine_support.items():
            if features:
                print(f"   • {engine}: {', '.join(features)}")
            else:
                print(f"   • {engine}: No prosody support")
        return
    
    # All other commands require an engine
    if not args.engine:
        parser.error("--engine is required for this operation")
    
    try:
        # Initialize converter with explicit parameters (only pass non-default values)
        converter_kwargs = {
            'engine_name': args.engine,
        }
        
        # Only include parameters that were explicitly provided
        if args.voice is not None:
            converter_kwargs['voice'] = args.voice
        if args.language is not None:
            converter_kwargs['language'] = args.language
        if args.rate is not None:
            converter_kwargs['rate'] = args.rate
        if args.rate_int is not None:
            converter_kwargs['rate_int'] = args.rate_int
        if args.pitch is not None:
            converter_kwargs['pitch'] = args.pitch
        if args.volume is not None:
            converter_kwargs['volume'] = args.volume
        if args.slow:  # Only include if True (explicitly provided)
            converter_kwargs['slow'] = args.slow
        
        # Handle prosody parameters (unified interface - automatically uses best method per engine)
        if args.prosody_style is not None or args.prosody_intensity is not None:
            # Validate prosody intensity range
            if args.prosody_intensity is not None and not (1 <= args.prosody_intensity <= 5):
                print(f"❌ Invalid prosody intensity: {args.prosody_intensity}. Must be between 1-5.")
                sys.exit(1)
            
            # Validate prosody style
            if args.prosody_style is not None:
                from prosody import validate_style, list_styles
                if not validate_style(args.prosody_style):
                    print(f"❌ Invalid prosody style: '{args.prosody_style}'")
                    print(f"Available styles: {', '.join(list_styles())}")
                    sys.exit(1)
            
            # Pass prosody parameters to converter (new unified approach)
            converter_kwargs['prosody_style'] = args.prosody_style
            converter_kwargs['prosody_intensity'] = args.prosody_intensity
        
        converter = TextToSpeechConverter(**converter_kwargs)
        
        # Handle information commands
        if args.engine_info:
            await converter.initialize()
            engine_info = converter.get_engine_info()
            print(f"\n🔧 Engine Information: {args.engine}")
            print(f"  • Name: {engine_info.get('name', 'Unknown')}")
            print(f"  • Type: {engine_info.get('type', 'Unknown')}")
            print(f"  • Available: {engine_info.get('available', False)}")
            print(f"  • Error Count: {engine_info.get('error_count', 0)}")
            if engine_info.get('last_error'):
                print(f"  • Last Error: {engine_info['last_error']}")
            return
        
        if args.list_voices:
            await converter.initialize()
            voices = await converter.list_voices()
            print(f"\n🎤 Available voices for {args.engine}:")
            if not voices:
                print("  No voices available or engine not accessible")
            else:
                for i, voice in enumerate(voices[:20]):  # Show first 20
                    if args.engine == 'edge_tts':
                        name = voice.get('Name', 'Unknown')
                        locale = voice.get('Locale', 'Unknown')
                        gender = voice.get('Gender', 'Unknown')
                        print(f"  {i+1:2}. {name} ({locale}, {gender})")
                    elif args.engine == 'pyttsx3':
                        name = voice.get('name', voice.get('id', 'Unknown'))
                        langs = voice.get('languages', [])
                        lang_str = ', '.join(langs) if langs else 'Unknown'
                        print(f"  {i+1:2}. {name} ({lang_str})")
                    elif args.engine == 'gtts':
                        name = voice.get('name', 'Unknown')
                        lang = voice.get('language', 'Unknown')
                        print(f"  {i+1:2}. {name} (Language: {lang})")
                
                if len(voices) > 20:
                    print(f"  ... and {len(voices) - 20} more voices")
            return
        
        # Handle conversion
        if not args.input_file:
            parser.error("input_file is required for conversion")
        
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ Input file not found: {input_path}")
            sys.exit(1)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Default output in generated/ directory
            generated_dir = Path("generated")
            generated_dir.mkdir(exist_ok=True)
            output_path = generated_dir / f"{input_path.stem}.mp3"
        
        # Warn if output file exists
        if output_path.exists():
            logger.info(f"Output file '{output_path}' already exists. Overwriting...")
        
        # Validate parameters before starting conversion
        is_valid, validation_error = await converter.validate_request()
        if not is_valid:
            print(f"❌ Parameter validation failed: {validation_error}")
            sys.exit(1)
        
        # Read and convert
        logger.info(f"Reading text from: {input_path}")
        text_content = converter.read_text_file(input_path)
        
        # Show content preview
        preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
        logger.info(f"Text preview: {preview}")
        logger.info(f"Total characters: {len(text_content)}")
        
        # Convert to speech
        await converter.convert_text_to_speech(text_content, output_path)
        
        print(f"\n✅ Conversion completed successfully!")
        print(f"📁 Input: {input_path}")
        print(f"🎵 Output: {output_path}")
        print(f"🔧 Engine: {args.engine}")
        if args.voice:
            print(f"🎙️ Voice: {args.voice}")
        if args.language:
            print(f"🌍 Language: {args.language}")
        if args.prosody_style:
            print(f"🎭 Prosody Style: {args.prosody_style}")
        if args.prosody_intensity:
            print(f"🎚️ Prosody Intensity: {args.prosody_intensity}")
        if args.rate:
            print(f"📈 Rate: {args.rate}")
        if args.pitch:
            print(f"🎵 Pitch: {args.pitch}")
        print(f"📊 Characters processed: {len(text_content)}")
        
    except ValueError as e:
        print(f"❌ Invalid request: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 