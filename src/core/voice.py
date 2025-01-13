"""
Voice module for MCP - Let's give our AIs a voice! 🎙️

Trisha says: "Numbers sound better when spoken with a smile!" 😊
"""

import asyncio
import json
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional

import edge_tts
import sounddevice as sd
import soundfile as sf
from edge_tts import VoicesManager
from rich.console import Console

console = Console()

class AIPersonality(Enum):
    """Different AI personalities and their voice preferences."""
    
    AYE = {
        "name": "Aye",
        "voice": "en-US-ChristopherNeural",  # Clear and friendly male voice
        "rate": "+10%",  # Slightly faster than normal
        "volume": "+10%",  # Slightly louder
        "pitch": "+2Hz"  # Slightly higher pitch
    }
    
    TRISHA = {
        "name": "Trisha",
        "voice": "en-US-JennyNeural",  # Professional female voice
        "rate": "+5%",  # Normal pace with slight enthusiasm
        "volume": "+5%",  # Clear volume
        "pitch": "+1Hz"  # Slight pitch adjustment for warmth
    }
    
    OMNI = {
        "name": "Omni",
        "voice": "en-US-GuyNeural",  # Warm and wise male voice
        "rate": "-5%",  # Slightly slower for wisdom
        "volume": "+0%",  # Normal volume
        "pitch": "-2Hz"  # Slightly deeper for authority
    }

class VoiceManager:
    """Manages text-to-speech for different AI personalities."""
    
    def __init__(self):
        self._cache_dir = Path(tempfile.gettempdir()) / "mcp_voice_cache"
        self._cache_dir.mkdir(exist_ok=True)
        self._voices: Optional[list] = None
    
    async def _init_voices(self):
        """Initialize available voices."""
        if self._voices is None:
            voices = await VoicesManager.create()
            self._voices = voices.voices
    
    async def _get_voice_path(self, text: str, personality: AIPersonality) -> Path:
        """Get path for cached voice file or generate new one."""
        # Create a unique filename based on text and personality
        filename = f"{personality.name}_{hash(text)}.wav"
        voice_path = self._cache_dir / filename
        
        if not voice_path.exists():
            # Generate new voice file
            communicate = edge_tts.Communicate(
                text,
                personality.value["voice"],
                rate=personality.value["rate"],
                volume=personality.value["volume"],
                pitch=personality.value["pitch"]
            )
            
            await communicate.save(str(voice_path))
        
        return voice_path
    
    def _play_audio(self, path: Path):
        """Play audio file using sounddevice."""
        data, samplerate = sf.read(str(path))
        sd.play(data, samplerate)
        sd.wait()  # Wait until audio is finished playing
    
    async def say(self, text: str, personality: AIPersonality):
        """Speak text with specified personality."""
        try:
            await self._init_voices()
            
            # Add personality-specific emoji and formatting
            formatted_text = f"{personality.value['name']} says: {text}"
            console.print(f"🎙️ [bold]{formatted_text}[/bold]")
            
            # Get voice file path (cached or new)
            voice_path = await self._get_voice_path(text, personality)
            
            # Play the audio
            self._play_audio(voice_path)
            
        except Exception as e:
            console.print(f"[red]Failed to speak: {e}[/red]")
            # Fallback to text-only
            console.print(f"💭 [italic]{formatted_text}[/italic]")
    
    async def list_voices(self):
        """List all available voices."""
        await self._init_voices()
        console.print("\n🎙️ [bold]Available Voices:[/bold]")
        for voice in self._voices:
            console.print(f"- {voice['ShortName']}: {voice['LocaleName']}")

# Create a singleton instance
voice_manager = VoiceManager()

async def speak(text: str, personality: AIPersonality = AIPersonality.AYE):
    """Convenience function to speak text with a personality."""
    await voice_manager.say(text, personality)

async def test_voices():
    """Test all AI personalities."""
    test_text = "Hello! It's wonderful to meet you!"
    
    for personality in AIPersonality:
        await speak(test_text, personality)
        await asyncio.sleep(2)  # Pause between voices

if __name__ == "__main__":
    # Test the voice system
    asyncio.run(test_voices()) 