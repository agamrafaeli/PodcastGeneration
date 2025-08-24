import subprocess
import wave
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_demo_mlk_cli(tmp_path):
    out_path = tmp_path / "dream.wav"
    cmd = [str(Path(__file__).resolve().parent.parent / "prosody"), "demo-mlk", "--out", str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert out_path.exists()

    with wave.open(str(out_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)

    assert 5 <= duration <= 15
