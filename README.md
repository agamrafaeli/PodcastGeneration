# Text-to-Speech Script

A Python script that converts text files to high-quality MP3 audio using Microsoft Edge TTS. Perfect for creating podcast narrations, audiobooks, or any audio content from written scripts.

## 🎯 Features

- **High-Quality Audio**: Uses Microsoft Edge TTS for natural-sounding voices
- **Language-Based Voice Selection**: Simply specify a language code and get the best voice automatically
- **Easy to Use**: Simple command-line interface
- **Multiple Voices**: Support for dozens of voices in different languages
- **Customizable**: Adjust speech rate and pitch
- **MP3 Output**: Generates ready-to-use MP3 files
- **Python SDK**: Programmatic interface for integration into other projects
- **Prosody Enhancement**: Intelligent prosody control with configurable speaking styles
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Quick Start

### 1. Installation

```bash
# Install runtime dependencies
pip install -r requirements-core.txt -r requirements-tts.txt

# Install test dependencies (includes runtime)
pip install -r requirements-dev.txt
```

### 2. Command Overview

| Subcommand | Purpose |
|------------|---------|
| `generate` | Convert a text file into an MP3 using the selected engine and voice options. |
| `sample`   | Create consolidated voice samples to compare different narrators. |
| `cleanup`  | Remove generated audio files (`--temp` for temporary files, `--all` for everything). |

### 3. Basic Usage

**Option 1: Using the convenience script (recommended)**
```bash
# Convert a text file to MP3 with default English voice (creates sample_script.mp3)
./tts-cli generate sample_script.txt --engine edge_tts

# Use language-based voice selection (automatically picks best voice for the language)
./tts-cli generate sample_script.txt --engine edge_tts -v "en-US-JennyNeural"
./tts-cli generate sample_script.txt --engine gtts -l fr
./tts-cli generate sample_script.txt --engine edge_tts -v "de-DE-KatjaNeural"

# Specify custom output file
./tts-cli generate sample_script.txt --engine edge_tts -o my_podcast.mp3

# Use a specific voice (traditional method)
./tts-cli generate sample_script.txt --engine edge_tts -v "en-US-JennyNeural"
```

**Option 2: Using PYTHONPATH directly**
```bash
# Set PYTHONPATH to include src directory
export PYTHONPATH=src

# Run CLI module directly
python -m cli generate sample_script.txt --engine edge_tts

# Or run the script directly
python src/cli.py generate sample_script.txt --engine edge_tts
```

**Option 3: One-liner with PYTHONPATH**
```bash
# For quick one-off commands
PYTHONPATH=src python -m cli --help
PYTHONPATH=src python -m cli generate sample_script.txt --engine edge_tts
```

## 🎤 Voice Sample Generator

**PROFESSIONAL VOICE SAMPLES**: Generate a single consolidated MP3 with narrator labels to help you choose the best voice for your project!

```bash
# Generate consolidated voice samples with narrator labels ("One:", "Two:", "Three:")
./tts-cli sample "Hello world, this is a test sentence for voice comparison."

# Use longer text for better voice evaluation - creates one professional MP3
./tts-cli sample "Welcome to our podcast. Today we'll be discussing the latest developments in artificial intelligence and machine learning. This longer sample will help you evaluate voice quality and characteristics."
```

**Features:**
- 🎵 **Single Consolidated MP3**: One professional audio file instead of separate files
- 🎙️ **Narrator Labels**: Clear "One:", "Two:", "Three:" introductions for each voice sample
- 🔀 **Multiple Engines**: Automatically uses Edge TTS, Google TTS, and pyttsx3 for variety
- ⏱️ **Smart Spacing**: Proper pauses between samples for easy comparison
- 📁 **Clean Output**: Single file `voice_samples_consolidated.mp3` in `generated/voice_samples/`

This creates a production-ready voice comparison that's perfect for professional decision-making.

## 🎧 Podcast Workflow Example

```bash
# 1️⃣ Generate a podcast episode from a script
./tts-cli generate episode.txt --engine edge_tts -v "en-US-JennyNeural" -o episode.mp3

# 2️⃣ (Optional) Preview different narrators
./tts-cli sample "Welcome to the show!" 

# 3️⃣ Clean up temporary files when done
./tts-cli cleanup --temp
```

## 📝 Usage Examples

### 🌍 Language-Based Voice Selection (Recommended)
```bash
# English variants
./tts-cli generate script.txt --engine edge_tts -v "en-US-JennyNeural"    # American English
./tts-cli generate script.txt --engine edge_tts -v "en-GB-SoniaNeural"    # British English
./tts-cli generate script.txt --engine edge_tts -v "en-AU-NatashaNeural"  # Australian English

# Other languages
./tts-cli generate script.txt --engine gtts -l fr       # French
./tts-cli generate script.txt --engine edge_tts -v "es-ES-ElviraNeural"    # Spanish (Spain)
./tts-cli generate script.txt --engine edge_tts -v "de-DE-KatjaNeural"     # German
./tts-cli generate script.txt --engine gtts -l ja       # Japanese
./tts-cli generate script.txt --engine edge_tts -v "zh-CN-XiaoxiaoNeural" # Chinese (Simplified)

# List available voices
./tts-cli generate --engine edge_tts --list-voices
```

### List Available Voices
```bash
./tts-cli generate --list-voices
```

### Advanced Options
```bash
# Faster speech rate with higher pitch
./tts-cli generate script.txt --engine edge_tts -v "en-US-JennyNeural" -r "+50%" -p "+10Hz" -o fast_narration.mp3

# Slower speech rate for better comprehension
./tts-cli generate script.txt --engine gtts -l fr --slow -o slow_narration.mp3

# Combine voice selection with custom settings
./tts-cli generate script.txt --engine edge_tts -v "de-DE-KatjaNeural" -r "+25%" -p "+5Hz"
```

### 🎭 Bulk Voice Generation
```bash
# Generate voice samples to compare different engines
./tts-cli sample "Your sample text here"

# Use different engines for comparison
./tts-cli generate script.txt --engine edge_tts -v "en-US-JennyNeural"
./tts-cli generate script.txt --engine gtts -l en
./tts-cli generate script.txt --engine pyttsx3 --rate-int 200
```

**Note**: Bulk generation creates a folder `{filename}_bulk_voices/` with hundreds of MP3 files, one for each available voice. Perfect for:
- Voice comparison and selection
- Creating voice sample libraries
- Testing content across different languages/accents
- A/B testing different narrator styles

## 🎙️ Popular Voice Options (Traditional Method)

| Voice | Language | Gender | Description |
|-------|----------|---------|-------------|
| `en-US-AriaNeural` | English (US) | Female | Default, natural and clear |
| `en-US-JennyNeural` | English (US) | Female | Warm and friendly |
| `en-US-GuyNeural` | English (US) | Male | Professional and confident |
| `en-GB-SoniaNeural` | English (UK) | Female | British accent |
| `en-AU-NatashaNeural` | English (AU) | Female | Australian accent |

*Note: With the new language parameter (`-l`), you don't need to remember specific voice names!*

## 🛠️ Command Line Options

```
usage: tts-cli <subcommand> [options]

Subcommands:
  generate   Convert text files to audio
  sample     Create consolidated voice samples
  cleanup    Remove generated audio files

Common generate options:
  --engine {edge_tts,gtts,pyttsx3}
  -v, --voice VOICE
  -l, --language LANG
  -r, --rate RATE
  --rate-int RATE_INT
  -p, --pitch PITCH
  --prosody-style STYLE
  --prosody-intensity 1-5
  -o, --output PATH
  --list-voices
  --engine-info

Cleanup options:
  --temp   Remove files with 'temp' or 'test' in the name
  --all    Remove everything in the generated/ directory

Use `tts-cli <subcommand> --help` for details on each command.
```

## 🌍 Language Support

The script supports **67+ languages** with automatic voice selection. Popular languages include:

| Language Code | Language | Example Voice |
|---------------|----------|---------------|
| `en`, `en-US` | English (US) | en-US-AriaNeural |
| `en-GB` | English (UK) | en-GB-SoniaNeural |
| `en-AU` | English (AU) | en-AU-NatashaNeural |
| `fr`, `fr-FR` | French | fr-FR-DeniseNeural |
| `es`, `es-ES` | Spanish (Spain) | es-ES-ElviraNeural |
| `de`, `de-DE` | German | de-DE-KatjaNeural |
| `ja`, `ja-JP` | Japanese | ja-JP-NanamiNeural |
| `zh`, `zh-CN` | Chinese (Simplified) | zh-CN-XiaoxiaoNeural |
| `ar`, `ar-SA` | Arabic | ar-SA-ZariyahNeural |
| `hi`, `hi-IN` | Hindi | hi-IN-SwaraNeural |
| `ru`, `ru-RU` | Russian | ru-RU-SvetlanaNeural |
| `pt`, `pt-BR` | Portuguese (Brazil) | pt-BR-FranciscaNeural |

**To see all supported languages:**
```bash
./tts-cli generate --list-languages
```

**Why use language codes instead of voice names?**
- ✅ **Simpler**: Just specify the language you want
- ✅ **Automatic**: Gets the best available voice for that language
- ✅ **Future-proof**: Works even if Microsoft updates voice names
- ✅ **Fallback**: Gracefully falls back to default if language not found

## 🎭 Prosody Enhancement System

The TTS system now includes intelligent prosody control for enhanced naturalness and expressiveness.

### Available Speaking Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `newscast` | Professional, clear, authoritative | News, announcements, formal content |
| `warm_coach` | Encouraging and supportive | Educational content, tutorials, coaching |
| `conversational` | Natural and relaxed (default) | Casual content, storytelling, dialogue |
| `formal` | Professional and measured | Presentations, documentation, speeches |

### Configuration System

The prosody system uses YAML configuration files:

- **`generated/styles.yaml`**: Defines speaking style presets with SSML parameters
- **`generated/calibration.yaml`**: Voice-specific adjustments for consistent quality

### Style Intensity Levels

Styles support intensity levels from 1 (subtle) to 5 (maximum):

```bash
# Examples using Python SDK (when integrated)
sdk.speak("Hello world", style="newscast", intensity=3)    # Standard application
sdk.speak("Hello world", style="warm_coach", intensity=1)  # Subtle coaching tone
sdk.speak("Hello world", style="formal", intensity=5)      # Maximum formality
```

### Module Architecture

```
src/prosody/
├── styles/          # Style definitions and voice calibrations
│   ├── manager.py   # Style configuration management
│   ├── style.py     # Style data structures
│   └── calibration.py # Voice-specific adjustments
├── ssml/           # Enhanced SSML composition
│   ├── composer.py  # Core SSML generation utilities
│   ├── enhancer.py  # Style-based SSML enhancement
│   └── utils.py     # SSML validation and manipulation
└── integration/    # TTS engine integration
    ├── integrator.py      # Base integration interface
    └── edge_tts.py        # EdgeTTS prosody integration
```

## 📁 File Structure

```
PodcastGeneration/
├── tts-cli                # Convenience script (run this!)
├── src/
│   ├── cli.py             # Main CLI implementation
│   ├── config.py          # Configuration and engine settings
│   ├── engines/           # TTS engine implementations
│   │   ├── core/          # Base engine classes and management
│   │   ├── implementations/  # Actual engine implementations
│   │   │   ├── cloud/     # Cloud-based engines (edge_tts, gtts)
│   │   │   └── offline/   # Offline engines (pyttsx3)
│   │   ├── models/        # Voice models and data structures
│   │   └── utils/         # Engine utilities and validation
│   ├── tts/              # TTS SDK and conversion logic
│   │   ├── sdk.py        # Python SDK for TTS operations
│   │   └── converter.py  # Core conversion logic
│   └── prosody/          # Prosody enhancement system
│       ├── ssml/         # SSML composition and enhancement
│       ├── styles/       # Style definitions and calibration
│       └── integration/  # TTS engine integration
├── generated/            # Output files and configurations
│   ├── styles.yaml       # Prosody style definitions
│   └── calibration.yaml  # Voice calibration settings
├── tests/                # Comprehensive test suite
├── requirements-core.txt  # Core runtime dependencies
├── requirements-tts.txt   # TTS engine-specific dependencies
├── requirements-dev.txt   # Development and test dependencies
└── README.md            # This documentation
```

## ⚡ Requirements

- Python 3.7 or higher
- Internet connection (required for Microsoft Edge TTS)
- Dependencies listed in `requirements-core.txt` and `requirements-tts.txt`
  (or `requirements-dev.txt` for tests)

## 🎵 Audio Quality

The script generates high-quality MP3 files with:
- **Sample Rate**: 24kHz
- **Bit Rate**: Variable (optimized by Edge TTS)
- **Format**: MP3
- **Quality**: Near-studio quality for most voices

## 🔧 Troubleshooting


### Getting Help

```bash
# Show help message with all options
./tts-cli --help

# List available voices
./tts-cli generate --list-voices
```

## 🧪 Testing

For comprehensive testing documentation, see **[TESTING.md](TESTING.md)**.

Quick test commands:
```bash
# Run fast mock tests (recommended for development)
python -m pytest tests/test_voice_mock_integration.py -v

# Run all tests with real engines
USE_REAL_ENGINES=true python -m pytest tests/ -v
```

## 🎯 Use Cases

- **Podcast Creation**: Convert scripts to podcast episodes in any language
- **Audiobook Production**: Turn written content into audiobooks with native-sounding voices  
- **Accessibility**: Make written content available as audio in multiple languages
- **Language Learning**: Generate pronunciation examples in target languages
- **Content Creation**: Create voiceovers for videos in different languages
- **Prototyping**: Quick audio mockups for multilingual applications
- **Global Content**: Easily create audio versions for international audiences

## 📈 Performance

- **Speed**: Typically 2-5x faster than real-time playback
- **File Size**: ~1MB per minute of audio (varies by content)
- **Processing**: Async processing for efficient conversion
- **Memory**: Low memory usage, suitable for long texts
- **Languages**: Support for 67+ languages with automatic voice selection

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the script!

## 📄 License

This project is open source. The Edge TTS service is provided by Microsoft.

---

**Happy podcasting! 🎙️🎧** 