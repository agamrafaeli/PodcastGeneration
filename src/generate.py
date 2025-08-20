import asyncio
import argparse
from pathlib import Path
from typing import Optional

from config import logger
from tts.converter import TextToSpeechConverter

# Existing CLI conversion logic extracted from cli.py

async def run(args: argparse.Namespace) -> None:
    """Handle the generate subcommand."""
    converter_kwargs = {
        'engine_name': args.engine,
    }
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
    if args.slow:
        converter_kwargs['slow'] = args.slow

    if args.prosody_style is not None or args.prosody_intensity is not None:
        if args.prosody_intensity is not None and not (1 <= args.prosody_intensity <= 5):
            print(f"❌ Invalid prosody intensity: {args.prosody_intensity}. Must be between 1-5.")
            return
        if args.prosody_style is not None:
            from prosody import validate_style, list_styles
            if not validate_style(args.prosody_style):
                print(f"❌ Invalid prosody style: '{args.prosody_style}'")
                print(f"Available styles: {', '.join(list_styles())}")
                return
        converter_kwargs['prosody_style'] = args.prosody_style
        converter_kwargs['prosody_intensity'] = args.prosody_intensity

    converter = TextToSpeechConverter(**converter_kwargs)

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
            for i, voice in enumerate(voices[:20]):
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

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return

    if args.output:
        output_path = Path(args.output)
    else:
        generated_dir = Path('generated')
        generated_dir.mkdir(exist_ok=True)
        output_path = generated_dir / f"{input_path.stem}.mp3"

    if output_path.exists():
        logger.info(f"Output file '{output_path}' already exists. Overwriting...")

    is_valid, validation_error = await converter.validate_request()
    if not is_valid:
        print(f"❌ Parameter validation failed: {validation_error}")
        return

    text_content = converter.read_text_file(input_path)
    preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
    logger.info(f"Text preview: {preview}")
    logger.info(f"Total characters: {len(text_content)}")

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


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the generate subcommand."""
    parser = subparsers.add_parser(
        'generate',
        help='Convert a text script into podcast-ready narration',
        description='Generate narrated audio from a text file using a selected TTS engine.',
        epilog='Example: main generate script.txt --engine edge_tts -v "en-US-JennyNeural"',
    )
    parser.add_argument('input_file', help='Input text file path')
    parser.add_argument('--engine', choices=['edge_tts', 'gtts', 'pyttsx3'], required=True,
                        help='TTS engine to use')
    parser.add_argument('-o', '--output', help='Output audio file path')
    parser.add_argument('-v', '--voice', help='Voice name/ID to use')
    parser.add_argument('-l', '--language', help='Language code (e.g., "en", "fr")')
    parser.add_argument('-r', '--rate', help='Speech rate for EdgeTTS (e.g., "+50%", "-25%")')
    parser.add_argument('--rate-int', type=int, help='Speech rate for pyttsx3 (words per minute)')
    parser.add_argument('-p', '--pitch', help='Pitch adjustment for EdgeTTS (e.g., "+10Hz", "-5Hz")')
    parser.add_argument('--volume', type=float, help='Volume for pyttsx3 (0.0-1.0)')
    parser.add_argument('--slow', action='store_true', help='Slow speech for gTTS')
    parser.add_argument('--prosody-style', help="Prosody style for enhanced speech synthesis")
    parser.add_argument('--prosody-intensity', type=int, metavar='1-5', help='Prosody intensity level')
    parser.add_argument('--list-voices', action='store_true', help='List voices for specified engine')
    parser.add_argument('--engine-info', action='store_true', help='Show information about specified engine')
    parser.set_defaults(func=run)
