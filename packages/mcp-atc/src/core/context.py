from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import json
from pathlib import Path

class Participant(BaseModel):
    """Represents an AI or Human participant"""
    id: str
    name: str
    type: str  # "ai" or "human"
    personality: Optional[Dict[str, Any]] = None
    
class ContextualFeeling(BaseModel):
    """Represents emotional/contextual state"""
    mood: str
    confidence: float
    insights: List[str]
    timestamp: datetime
    participant_id: str

class ToolContext(BaseModel):
    """Manages context for a tool session"""
    tool_id: str
    session_id: str
    participants: Dict[str, Participant]
    history: List[Dict[str, Any]]
    feelings: List[ContextualFeeling]
    shared_state: Dict[str, Any]
    
    def add_feeling(self, participant_id: str, mood: str, confidence: float, insights: List[str]):
        """Add a new contextual feeling"""
        feeling = ContextualFeeling(
            mood=mood,
            confidence=confidence,
            insights=insights,
            timestamp=datetime.now(),
            participant_id=participant_id
        )
        self.feelings.append(feeling)
    
    def get_participant_mood(self, participant_id: str) -> Optional[ContextualFeeling]:
        """Get the latest mood for a participant"""
        for feeling in reversed(self.feelings):
            if feeling.participant_id == participant_id:
                return feeling
        return None

    def save(self):
        """Save context to disk"""
        context_dir = Path("data/contexts")
        context_dir.mkdir(parents=True, exist_ok=True)
        
        with open(context_dir / f"{self.tool_id}_{self.session_id}.json", "w") as f:
            json.dump(self.dict(), f, default=str) 