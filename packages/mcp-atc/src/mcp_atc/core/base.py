from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid
from datetime import datetime
from .context import ToolContext, Participant

class BaseTool(ABC):
    """Base class for all ATC tools"""
    
    def __init__(self):
        self.contexts: Dict[str, ToolContext] = {}
        self._id = str(uuid.uuid4())
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    def tool_id(self) -> str:
        """Unique tool instance identifier"""
        return self._id
    
    async def create_session(self, session_id: str, initial_participant: Participant) -> ToolContext:
        """Create a new tool session"""
        context = ToolContext(
            tool_id=self.tool_id,
            session_id=session_id,
            participants={initial_participant.id: initial_participant},
            history=[],
            feelings=[],
            shared_state={}
        )
        self.contexts[session_id] = context
        return context
    
    async def join_session(self, session_id: str, participant: Participant) -> Optional[ToolContext]:
        """Join an existing tool session"""
        if session_id not in self.contexts:
            return None
            
        context = self.contexts[session_id]
        context.participants[participant.id] = participant
        return context
    
    async def execute(self, session_id: str, command: str, params: Dict[str, Any], participant_id: str) -> Dict[str, Any]:
        """Execute tool command"""
        if session_id not in self.contexts:
            return {"status": "error", "message": "Session not found"}
            
        context = self.contexts[session_id]
        if participant_id not in context.participants:
            return {"status": "error", "message": "Participant not found"}
        
        # Record command in history
        context.history.append({
            "command": command,
            "params": params,
            "participant_id": participant_id,
            "timestamp": datetime.now()
        })
        
        # Execute the command
        result = await self._execute_command(command, params, context)
        
        # Save context
        context.save()
        
        return result
    
    @abstractmethod
    async def _execute_command(self, command: str, params: Dict[str, Any], context: ToolContext) -> Dict[str, Any]:
        """Implement actual command execution"""
        pass