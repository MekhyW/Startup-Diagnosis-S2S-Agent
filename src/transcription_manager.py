import logging
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
import asyncio

logger = logging.getLogger("transcription_manager")

@dataclass
class TranscriptionEntry:
    """Represents a single transcription entry"""
    timestamp: datetime
    speaker: str  # 'agent' or 'user'
    text: str
    confidence: Optional[float] = None

class TranscriptionManager:
    """Manages transcription collection during the interview"""
    
    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.entries: List[TranscriptionEntry] = []
        self.start_time = datetime.now()
        self.is_recording = False
        self._lock = asyncio.Lock()
    
    async def start_recording(self):
        """Start recording transcription"""
        async with self._lock:
            self.is_recording = True
            self.start_time = datetime.now()
            logger.info(f"Started transcription recording for interview {self.interview_id}")
    
    async def stop_recording(self):
        """Stop recording transcription"""
        async with self._lock:
            self.is_recording = False
            logger.info(f"Stopped transcription recording for interview {self.interview_id}")
    
    async def add_agent_message(self, text: str, confidence: Optional[float] = None):
        """Add an agent message to the transcription"""
        if self.is_recording:
            async with self._lock:
                entry = TranscriptionEntry(timestamp=datetime.now(), speaker="agent", text=text, confidence=confidence)
                self.entries.append(entry)
                logger.debug(f"Added agent message: {text[:50]}...")
    
    async def add_user_message(self, text: str, confidence: Optional[float] = None):
        """Add a user message to the transcription"""
        if self.is_recording:
            async with self._lock:
                entry = TranscriptionEntry(timestamp=datetime.now(), speaker="user", text=text, confidence=confidence)
                self.entries.append(entry)
                logger.debug(f"Added user message: {text[:50]}...")
    
    async def get_full_transcription(self) -> str:
        """Get the complete transcription as formatted text"""
        async with self._lock:
            if not self.entries:
                return "No transcription available."
            lines = []
            lines.append(f"INTERVIEW TRANSCRIPTION")
            lines.append(f"Interview ID: {self.interview_id}")
            lines.append(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Duration: {self._get_duration()}")
            lines.append("=" * 50)
            lines.append("")
            for entry in self.entries:
                timestamp_str = entry.timestamp.strftime('%H:%M:%S')
                speaker_label = "AGENT" if entry.speaker == "agent" else "USER"
                confidence_str = f" (confidence: {entry.confidence:.2f})" if entry.confidence else ""
                lines.append(f"[{timestamp_str}] {speaker_label}{confidence_str}:")
                lines.append(f"{entry.text}")
                lines.append("")
            return "\n".join(lines)
    
    async def get_conversation_only(self) -> str:
        """Get just the conversation without metadata for analysis"""
        async with self._lock:
            if not self.entries:
                return "No conversation available."
            lines = []
            for entry in self.entries:
                speaker_label = "Entrevistador" if entry.speaker == "agent" else "Entrevistado"
                lines.append(f"{speaker_label}: {entry.text}")
            return "\n\n".join(lines)
    
    def _get_duration(self) -> str:
        """Calculate and format the duration of the interview"""
        if not self.entries:
            return "0:00:00"
        end_time = self.entries[-1].timestamp if self.entries else datetime.now()
        duration = end_time - self.start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    
    async def clear(self):
        """Clear all transcription data"""
        async with self._lock:
            self.entries.clear()
            logger.info(f"Cleared transcription data for interview {self.interview_id}")