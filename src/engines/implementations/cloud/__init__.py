"""
Cloud-based TTS Engines
"""

from engines.implementations.cloud.edge_tts import EdgeTTSEngine
from engines.implementations.cloud.gtts import gTTSEngine

__all__ = [
    "EdgeTTSEngine",
    "gTTSEngine"
] 