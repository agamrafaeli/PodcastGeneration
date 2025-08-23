import subprocess
import wave
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_demo_mlk_cli(tmp_path):
    out_file = tmp_path / "out.wav"
    result = subprocess.run([
        "./prosody",
        "demo-mlk",
        "--out",
        str(out_file),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert out_file.exists(), "Output file was not created"

    with wave.open(str(out_file), "rb") as wf:
        duration = wf.getnframes() / float(wf.getframerate())
        assert 0.9 <= duration <= 1.1, f"Unexpected duration {duration}"

    assert "Preset: prophetic_oratory" in result.stdout
