# Annotated Prosody Script Example

This example shows how to tag a script with prosody **style** and **intensity** markers, parse those markers, and call the `tts-cli` for each block. The script also uses `get_prosody_params` to reveal the concrete rate, pitch, and volume values applied at runtime.

## 1. Annotated Script (`episode.txt`)

```text
[style=energetic intensity=5]
Welcome to CodeCast, the show where code comes to life!

[style=conversational intensity=3]
Today we'll explore how prosody transforms text-to-speech.

[style=warm_coach intensity=2]
Remember to follow and rate the podcast!
```

## 2. Processing Script (`process_episode.py`)

```python
#!/usr/bin/env python3
"""Parse style/intensity markers and render each block with the TTS CLI."""
import re
import subprocess
import tempfile
from pathlib import Path

from prosody import get_prosody_params

# Load the annotated script
txt = Path("episode.txt").read_text()

# Match blocks like: [style=name intensity=N]\n<content>
pattern = r"\[style=(?P<style>\w+) intensity=(?P<intensity>\d)\]\n(?P<content>.+?)(?=\n\[|$)"

for i, m in enumerate(re.finditer(pattern, txt, re.DOTALL), 1):
    style = m.group("style")
    intensity = int(m.group("intensity"))
    content = m.group("content").strip()

    # Show the resolved prosody values
    params = get_prosody_params(style, intensity)
    print(f"Segment {i}: {style} (int {intensity}) -> {params}")

    # Write block to a temporary file for the CLI
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        subprocess.run([
            "./tts-cli", tmp.name,
            "--engine", "edge_tts",
            "--prosody-style", style,
            "--prosody-intensity", str(intensity),
            "-o", f"segment_{i}.mp3",
        ], check=True)
```

## 3. Run It

```bash
python process_episode.py
```

The script prints the rate/pitch/volume derived from each style and produces `segment_1.mp3`, `segment_2.mp3`, etc.
