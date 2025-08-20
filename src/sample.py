import argparse
import tempfile
from pathlib import Path

from config import logger
from tts.converter import TextToSpeechConverter
from pydub import AudioSegment


def split_text_for_samples(text: str, num_samples: int = 3) -> list[str]:
    words = text.split()
    if len(words) <= 10:
        return [text] * num_samples
    total_words = len(words)
    words_per_sample = max(10, total_words // num_samples)
    samples = []
    for i in range(num_samples):
        start_idx = i * (words_per_sample // 2)
        end_idx = min(start_idx + words_per_sample, total_words)
        if start_idx >= total_words:
            sample_text = " ".join(words[-words_per_sample:])
        else:
            sample_text = " ".join(words[start_idx:end_idx])
        samples.append(sample_text)
    return samples


def select_sample_voices() -> list[dict]:
    return [
        {"engine": "edge_tts"},
        {"engine": "gtts", "language": "en"},
        {"engine": "pyttsx3"},
    ]


async def run(args: argparse.Namespace) -> None:
    text = args.text
    print(f"🎤 Generating consolidated voice samples for: {text[:50]}{'...' if len(text) > 50 else ''}")
    text_samples = split_text_for_samples(text, 3)
    voice_configs = select_sample_voices()
    generated_dir = Path("generated/voice_samples")
    generated_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        narrator_files = []
        sample_files = []
        try:
            narrator_converter = TextToSpeechConverter(engine_name='edge_tts')
            for i, label in enumerate(["One", "Two", "Three"], 1):
                narrator_file = temp_path / f"narrator_{i}.mp3"
                await narrator_converter.convert_text_to_speech(f"{label}:", narrator_file)
                narrator_files.append(narrator_file)
            successful_samples = 0
            for i, (sample_text, voice_config) in enumerate(zip(text_samples, voice_configs), 1):
                try:
                    converter_kwargs = {'engine_name': voice_config['engine']}
                    if voice_config.get('voice'):
                        converter_kwargs['voice'] = voice_config['voice']
                    if voice_config.get('language'):
                        converter_kwargs['language'] = voice_config['language']
                    converter = TextToSpeechConverter(**converter_kwargs)
                    sample_file = temp_path / f"sample_{i}_{voice_config['engine']}.mp3"
                    await converter.convert_text_to_speech(sample_text, sample_file)
                    sample_files.append(sample_file)
                    successful_samples += 1
                except Exception as e:
                    logger.error(f"Voice sample {i} failed: {e}")
                    sample_files.append(None)
            if successful_samples == 0:
                print("❌ All voice samples failed to generate")
                return
            final_audio = AudioSegment.empty()
            silence = AudioSegment.silent(duration=1000)
            for narrator_file, sample_file in zip(narrator_files, sample_files):
                if sample_file and sample_file.exists():
                    if narrator_file.exists():
                        narrator_audio = AudioSegment.from_mp3(str(narrator_file))
                        final_audio += narrator_audio + AudioSegment.silent(duration=500)
                    sample_audio = AudioSegment.from_mp3(str(sample_file))
                    final_audio += sample_audio + silence
            output_file = generated_dir / "voice_samples_consolidated.mp3"
            final_audio.export(str(output_file), format="mp3")
            print(f"🎯 Consolidated voice samples completed!")
            print(f"📁 Output file: {output_file}")
        except Exception as e:
            print(f"❌ Consolidation failed: {e}")
            logger.error(f"Voice sample consolidation failed: {e}")


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        'sample',
        help='Create voice comparisons for your podcast script',
        description='Generate a single MP3 containing several voices reading your text.',
        epilog='Example: main sample "Welcome to our show."',
    )
    parser.add_argument('text', help='Sample text to compare voices')
    parser.set_defaults(func=run)
