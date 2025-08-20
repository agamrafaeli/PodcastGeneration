"""
Mocks package for TTS testing

Provides mock implementations of engines and SDK for predictable testing
without external dependencies.
"""

# Import all mock classes for convenient access
from tests.mocks.engine import MockTTSEngine, MockEngineFactory
from tests.mocks.sdk import MockTTSSDK

__all__ = [
    'MockTTSEngine',
    'MockEngineFactory', 
    'MockTTSSDK'
]
