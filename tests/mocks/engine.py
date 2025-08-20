#!/usr/bin/env python3
"""
Mock TTS Engine for testing Voice entity integration

Provides predictable Voice objects without external dependencies.
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

from engines.core import BaseTTSEngine, EngineType
from engines.models import Voice


class MockTTSEngine(BaseTTSEngine):
    """Mock TTS engine that returns predictable Voice objects for testing"""
    
    def __init__(self, engine_name: str):
        """Initialize mock engine with predictable voice data"""
        super().__init__(name=f"mock_{engine_name}", engine_type=EngineType.OFFLINE)
        self.engine_name = engine_name.lower()
        self._mock_voices = self._create_mock_voices()
    
    def _create_mock_voices(self) -> List[Voice]:
        """Create predictable mock voices for testing"""
        return [
            Voice(
                id=f"mock-{self.engine_name}-voice-1",
                name=f"Mock {self.engine_name.title()} Female Voice",
                language="en-US",
                gender="female",
                engine=self.engine_name,
                metadata={"quality": "high", "speed": "normal"}
            ),
            Voice(
                id=f"mock-{self.engine_name}-voice-2", 
                name=f"Mock {self.engine_name.title()} Male Voice",
                language="en-US",
                gender="male",
                engine=self.engine_name,
                metadata={"quality": "high", "speed": "normal"}
            ),
            Voice(
                id=f"mock-{self.engine_name}-voice-3",
                name=f"Mock {self.engine_name.title()} Spanish Voice",
                language="es-ES",
                gender="female", 
                engine=self.engine_name,
                metadata={"quality": "medium", "speed": "normal"}
            ),
            Voice(
                id=f"mock-{self.engine_name}-voice-4",
                name=f"Mock {self.engine_name.title()} French Voice",
                language="fr-FR",
                gender="male",
                engine=self.engine_name,
                metadata={"quality": "high", "speed": "fast"}
            ),
            Voice(
                id=f"mock-{self.engine_name}-voice-5",
                name=f"Mock {self.engine_name.title()} German Voice",
                language="de-DE",
                gender="female",
                engine=self.engine_name,
                metadata={"quality": "high", "speed": "normal"}
            )
        ]
    
    async def initialize(self) -> bool:
        """Initialize mock engine - always succeeds"""
        self.is_available = True
        return True
    
    async def _perform_conversion(self, text: str, output_path: Path, params=None) -> bool:
        """Mock TTS conversion that creates a dummy audio file"""
        try:
            # Create a valid mock MP3 file that will pass audio validation
            # Scale duration based on text length (roughly 150 words per minute)
            text_length = len(text.split())
            duration_seconds = max(1.0, text_length / 150 * 60)  # At least 1 second
            mock_mp3_data = self._create_mock_mp3_with_duration(duration_seconds)
            output_path.write_bytes(mock_mp3_data)
            
            # Add some delay to simulate processing
            await asyncio.sleep(0.1)
            return True
        except Exception:
            return False
    
    def _create_mock_mp3_with_duration(self, duration_seconds: float) -> bytes:
        """Create a mock MP3 file with specified duration"""
        # At 44.1kHz with MPEG-1, each frame represents 1152 samples
        # So for N seconds: (44100 * N) / 1152 frames
        num_frames = max(1, int((44100 * duration_seconds) / 1152))
        return self._create_valid_mock_mp3_frames(num_frames)
    
    def _create_valid_mock_mp3(self) -> bytes:
        """Create a minimal but valid MP3 file for testing"""
        # Create a proper MP3 file with valid frame structure
        # MPEG-1 Layer 3, 128kbps, 44.1kHz, Stereo, No CRC, No Padding
        
        # Calculate frame size: (144 * bitrate / sample_rate) + padding
        # For 128kbps at 44.1kHz: (144 * 128000 / 44100) = 417.959... ≈ 417 bytes per frame
        frame_size = 417
        
        # MP3 Frame Header (4 bytes)
        # Bits: AAAAAAAA AAABBCCD EEEEFFGH IIJJKLMM
        # A(11): Frame sync (0xFFE)
        # B(2): MPEG Audio version (11 = MPEG-1)  
        # C(2): Layer description (01 = Layer 3)
        # D(1): Protection bit (1 = No CRC)
        # E(4): Bitrate index (1001 = 128 kbps for MPEG-1 Layer 3)
        # F(2): Sampling rate (00 = 44100 Hz)
        # G(1): Padding bit (0 = no padding)
        # H(1): Private bit (0)
        # I(2): Channel mode (00 = Stereo)
        # J(2): Mode extension (00)
        # K(1): Copyright (0)
        # L(1): Original (0)
        # M(2): Emphasis (00)
        
        header = bytearray([
            0xFF,  # 11111111 - sync word part 1
            0xFB,  # 11111011 - sync word part 2 + version(11) + layer(01) + protection(1)
            0x90,  # 10010000 - bitrate(1001) + sample_rate(00) + padding(0) + private(0)
            0x00   # 00000000 - mode(00) + mode_ext(00) + copyright(0) + original(0) + emphasis(00)
        ])
        
        # Create frame data (frame_size - 4 header bytes)
        # For a minimal valid frame, we need some actual MP3 data structure
        # This creates a basic side information and main data section
        
        # Side information for stereo (32 bytes for MPEG-1 Layer 3 stereo)
        side_info = bytearray(32)
        
        # Set minimal required side info values
        side_info[0] = 0x00  # main_data_begin
        side_info[1] = 0x00
        side_info[2] = 0x0F  # private_bits and scfsi for channel 0
        side_info[3] = 0x0F  # scfsi for channel 1 
        
        # Granule info (basic values to make it parseable)
        for granule in range(2):  # 2 granules per frame
            for channel in range(2):  # 2 channels (stereo)
                offset = 4 + granule * 16 + channel * 8
                if offset + 7 < len(side_info):
                    side_info[offset] = 0x01     # part2_3_length (low bits)
                    side_info[offset + 1] = 0x00 # part2_3_length (high bits) + big_values
                    side_info[offset + 2] = 0x00 # big_values + global_gain
                    side_info[offset + 3] = 0x00 # scalefac_compress
                    side_info[offset + 4] = 0x00 # window_switching_flag + block_type + mixed_block_flag + table_select
                    side_info[offset + 5] = 0x00 # table_select + table_select + subblock_gain
                    side_info[offset + 6] = 0x00 # subblock_gain + region0_count + region1_count
                    side_info[offset + 7] = 0x00 # preflag + scalefac_scale + count1table_select
        
        # Main data (remaining bytes filled with minimal valid data)
        main_data_size = frame_size - 4 - len(side_info)
        main_data = bytearray(main_data_size)
        
        # Add some minimal huffman coded data to avoid empty main data
        if main_data_size > 0:
            main_data[0] = 0x01  # Minimal huffman data
            
        # Construct the frame
        frame = header + side_info + main_data
        
        # Ensure frame is exactly the right size
        if len(frame) > frame_size:
            frame = frame[:frame_size]
        elif len(frame) < frame_size:
            frame.extend(b'\x00' * (frame_size - len(frame)))
        
        # Create multiple frames for a realistic duration (~1 second)  
        return self._create_valid_mock_mp3_frames(40)
    
    def _create_valid_mock_mp3_frames(self, num_frames: int) -> bytes:
        """Create MP3 with specified number of frames"""
        # Calculate frame size: (144 * bitrate / sample_rate) + padding
        # For 128kbps at 44.1kHz: (144 * 128000 / 44100) = 417.959... ≈ 417 bytes per frame
        frame_size = 417
        
        # MP3 Frame Header (4 bytes) - same structure as before
        header = bytearray([
            0xFF,  # 11111111 - sync word part 1
            0xFB,  # 11111011 - sync word part 2 + version(11) + layer(01) + protection(1)
            0x90,  # 10010000 - bitrate(1001) + sample_rate(00) + padding(0) + private(0)
            0x00   # 00000000 - mode(00) + mode_ext(00) + copyright(0) + original(0) + emphasis(00)
        ])
        
        # Side information for stereo (32 bytes for MPEG-1 Layer 3 stereo)
        side_info = bytearray(32)
        side_info[0] = 0x00  # main_data_begin
        side_info[1] = 0x00
        side_info[2] = 0x0F  # private_bits and scfsi for channel 0
        side_info[3] = 0x0F  # scfsi for channel 1 
        
        # Basic granule info
        for granule in range(2):
            for channel in range(2):
                offset = 4 + granule * 16 + channel * 8
                if offset + 7 < len(side_info):
                    side_info[offset] = 0x01
                    
        # Main data
        main_data_size = frame_size - 4 - len(side_info)
        main_data = bytearray(main_data_size)
        if main_data_size > 0:
            main_data[0] = 0x01
            
        # Construct single frame
        frame = header + side_info + main_data
        if len(frame) > frame_size:
            frame = frame[:frame_size]
        elif len(frame) < frame_size:
            frame.extend(b'\x00' * (frame_size - len(frame)))
        
        # Create the full MP3 with specified number of frames
        mock_mp3 = frame * num_frames
        return bytes(mock_mp3)
    
    def validate_params(self, params) -> tuple[bool, str]:
        """Validate mock engine parameters - always valid"""
        return True, ""
    
    async def list_voices(self) -> List[Dict[str, Any]]:
        """Return mock voice data as dictionaries (engine format)"""
        return [
            {
                'id': voice.id,
                'name': voice.name, 
                'language': voice.language,
                'gender': voice.gender,
                'engine': voice.engine,
                'metadata': voice.metadata
            }
            for voice in self._mock_voices
        ]
    
    def parse_voice_list(self, raw_output: str) -> List[Voice]:
        """Parse mock voice data and return Voice objects"""
        # For mocks, ignore raw_output and return our predefined voices
        return self._mock_voices.copy()


class MockEngineFactory:
    """Factory for creating mock engines for different engine types"""
    
    @staticmethod
    def create_mock_edge_tts() -> MockTTSEngine:
        """Create mock Edge TTS engine"""
        return MockTTSEngine("edge_tts")
    
    @staticmethod 
    def create_mock_gtts() -> MockTTSEngine:
        """Create mock GTTS engine"""
        return MockTTSEngine("gtts")
    
    @staticmethod
    def create_mock_pyttsx3() -> MockTTSEngine:
        """Create mock PyTTSx3 engine"""
        return MockTTSEngine("pyttsx3")
    
    @staticmethod
    def get_all_mock_engines() -> Dict[str, MockTTSEngine]:
        """Get all available mock engines"""
        return {
            "edge_tts": MockEngineFactory.create_mock_edge_tts(),
            "gtts": MockEngineFactory.create_mock_gtts(), 
            "pyttsx3": MockEngineFactory.create_mock_pyttsx3()
        }
