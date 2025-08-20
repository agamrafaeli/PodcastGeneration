from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import generate
import main
import pytest


class DummyConverter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def read_text_file(self, path: Path) -> str:
        return path.read_text()

    async def validate_request(self):
        return True, None

    async def convert_text_to_speech(self, text: str, output: Path):
        output.write_text('audio')
        self.called_with = (text, output)


def test_generate_parses_and_calls(monkeypatch, tmp_path):
    script = tmp_path / 'script.txt'
    script.write_text('hello world')
    out = tmp_path / 'out.mp3'

    monkeypatch.setattr(generate, 'TextToSpeechConverter', DummyConverter)
    main.main(['generate', str(script), '--engine', 'edge_tts', '-o', str(out)])

    assert out.exists()
