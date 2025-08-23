"""MLK demo pipeline: preset -> annotation parsing -> performance craft -> audio render."""
from __future__ import annotations

import random
import re
import struct
import wave
from pathlib import Path

import yaml

ANNOTATION_RE = re.compile(r"\[(?P<key>[^=\]]+)(=(?P<value>[^\]]+))?\]")

def load_preset() -> dict:
    """Load the prophetic oratory preset."""
    preset_path = Path(__file__).resolve().parent.parent.parent / "examples" / "demo-mlk" / "prophetic_oratory.yaml"
    with open(preset_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_script() -> tuple[str, list[dict]]:
    """Load the annotated script text."""
    script_path = Path(__file__).resolve().parent.parent.parent / "examples" / "demo-mlk" / "script.txt"
    text = script_path.read_text(encoding="utf-8")
    return parse_annotations(text)

def parse_annotations(text: str) -> tuple[str, list[dict]]:
    """Strip inline annotations from text and return them separately."""
    annotations: list[dict] = []
    def repl(match: re.Match[str]) -> str:
        annotations.append({"key": match.group("key"), "value": match.group("value")})
        return ""
    plain = ANNOTATION_RE.sub(repl, text)
    return plain.strip(), annotations

def craft_performance(plain_text: str, preset: dict, annotations: list[dict]) -> dict:
    """Apply preset repetition strategy to the plain text."""
    repeated_text = plain_text
    rep = preset.get("repetition")
    if rep:
        phrase = rep.get("phrase")
        count = rep.get("count", 1)
        if phrase:
            repeated = " ".join([phrase] * count)
            repeated_text = repeated_text.replace(phrase, repeated, 1)
    return {"text": repeated_text, "preset": preset, "annotations": annotations}

def render_audio(plan: dict, out_path: Path) -> float:
    """Render a short silent WAV file and return its duration."""
    duration_sec = 1.0
    framerate = 16000
    frames = int(duration_sec * framerate)
    with wave.open(str(out_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(struct.pack("<h", 0) * frames)
    return duration_sec

def run_demo_mlk(args) -> int:
    """Entry point for the demo-mlk CLI command."""
    if args.seed is not None:
        random.seed(args.seed)
    preset = load_preset()
    plain_text, annotations = load_script()
    plan = craft_performance(plain_text, preset, annotations)
    voice = args.voice or "default"
    if args.dry_run:
        print("Render plan:")
        print(plan)
        duration = None
    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        duration = render_audio(plan, out_path)
    summary = f"Preset: prophetic_oratory | Voice: {voice} | Output: {args.out}"

    if duration is not None:
        summary += f" | Duration: {duration:.2f}s"
    print(summary)
    return 0
