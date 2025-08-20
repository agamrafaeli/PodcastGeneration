#!/usr/bin/env python3
"""
Global Voice entity for TTS system
Provides a unified representation of voices across all engines
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Voice:
    """Represents a TTS voice across all engines"""
    id: str
    name: str
    language: str
    gender: Optional[str] = None
    engine: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return f"Voice(id='{self.id}', name='{self.name}', language='{self.language}', engine='{self.engine}')"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__() 