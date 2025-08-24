"""Demonstration pipeline for the "I Have a Dream" excerpt.

Stages:
    1. Preset loading
    2. Annotation parsing
    3. Performance crafting
    4. Audio rendering (silent for demo/testing)
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

from pydub import AudioSegment
import yaml

@dataclass
class Segment:
    """A piece of the script after annotation parsing."""
    kind: str  # 'text' or 'pause'
    content: str = ""
    duration: float = 0.0  # seconds for pauses or precomputed speech
    pitch: float = 0.0
    volume: float = 0.0


def load_preset(name: str) -> Dict:
    """Load a preset YAML configuration."""
    preset_path = Path(__file__).parent / "presets" / f"{name}.yaml"
    with preset_path.open() as f:
        return yaml.safe_load(f)


def parse_script(path: Path) -> List[Segment]:
    """Parse the annotated script into text and pause segments."""
    text = path.read_text().strip()
    parts = re.split(r"\[pause=([0-9.]+)\]", text)
    segments: List[Segment] = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                segments.append(Segment(kind="text", content=part.strip()))
        else:
            segments.append(Segment(kind="pause", duration=float(part)))
    return segments


def craft_performance(preset: Dict, segments: List[Segment], voice: Optional[str]) -> List[Segment]:
    """Apply preset parameters and repetition strategy to segments."""
    base_pitch = preset.get("pitch", 0)
    base_volume = preset.get("volume", 0)
    repetition = preset.get("repetition", {})
    phrase = repetition.get("phrase")
    pitch_inc = repetition.get("pitch_increment", 0)
    volume_inc = repetition.get("volume_increment", 0)
    counts: Dict[str, int] = {}

    tempo = preset.get("tempo", 100)  # words per minute
    for seg in segments:
        if seg.kind == "text":
            text = seg.content
            if phrase and phrase.lower() in text.lower():
                counts[phrase] = counts.get(phrase, 0) + 1
                seg.pitch = base_pitch + pitch_inc * counts[phrase]
                seg.volume = base_volume + volume_inc * counts[phrase]
            else:
                seg.pitch = base_pitch
                seg.volume = base_volume
            words = len(text.split())
            seg.duration = words / float(tempo) * 60.0
    return segments


def render_audio(plan: List[Segment], out_path: Path, seed: Optional[int]) -> float:
    """Render the performance plan to a WAV file (silent audio)."""
    if seed is not None:
        random.seed(seed)
    audio = AudioSegment.silent(duration=0)
    for seg in plan:
        if seg.kind == "pause":
            duration_ms = int(seg.duration * 1000)
            audio += AudioSegment.silent(duration=duration_ms)
        else:
            # For text, create silent audio based on computed duration
            duration_ms = int(seg.duration * 1000)
            audio += AudioSegment.silent(duration=duration_ms)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio.export(out_path, format="wav")
    return audio.duration_seconds


def run_demo(out: Path, voice: Optional[str], dry_run: bool, seed: Optional[int]) -> float:
    preset = load_preset("prophetic_oratory")
    script_path = Path(__file__).parent / "scripts" / "i_have_a_dream.txt"
    segments = parse_script(script_path)
    plan = craft_performance(preset, segments, voice)
    if dry_run:
        for seg in plan:
            if seg.kind == "text":
                print(f"TEXT: '{seg.content}' | dur={seg.duration:.2f}s pitch={seg.pitch}Hz vol={seg.volume}dB")
            else:
                print(f"PAUSE: {seg.duration:.2f}s")
        print(f"Preset: prophetic_oratory, Voice: {voice or preset.get('voice')}")
        print("Dry run - no audio generated")
        return 0.0
    duration = render_audio(plan, out, seed)
    print(f"Preset: prophetic_oratory, Voice: {voice or preset.get('voice')}, Output: {out}, Duration: {duration:.2f}s")
    return duration
