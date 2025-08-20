from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import sample
import main


class DummyAudioSegment:
    @staticmethod
    def empty():
        return DummyAudioSegment()

    @staticmethod
    def silent(duration=1000):
        return DummyAudioSegment()

    @staticmethod
    def from_mp3(path):
        return DummyAudioSegment()

    def __add__(self, other):
        return self

    def export(self, path, format):
        Path(path).write_text('audio')


class DummyConverter:
    def __init__(self, **kwargs):
        pass

    async def convert_text_to_speech(self, text: str, output: Path):
        output.write_text('audio')


def test_sample_calls_converters(monkeypatch, tmp_path):
    monkeypatch.setattr(sample, 'TextToSpeechConverter', DummyConverter)
    monkeypatch.setattr(sample, 'AudioSegment', DummyAudioSegment)
    main.main(['sample', 'hello world'])
    generated = Path('generated/voice_samples/voice_samples_consolidated.mp3')
    assert generated.exists()
