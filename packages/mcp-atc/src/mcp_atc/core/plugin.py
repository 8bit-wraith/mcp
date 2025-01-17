from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseTool
from .context import ToolContext, Participant

class Tool(BaseTool):
    """Enhanced tool class with ToF support"""
    
    def __init__(self):
        super().__init__()
        self._tof = None  # Lazy load ToF manager to avoid circular imports
    
    @property
    def tof(self):
        """Lazy load ToF manager"""
        if self._tof is None:
            from .tof_manager import ToFManager
            self._tof = ToFManager()
        return self._tof
    
    async def create_session(self, session_id: str, initial_participant: Participant) -> ToolContext:
        """Create a new tool session with ToF monitoring"""
        context = await super().create_session(session_id, initial_participant)
        await self.tof.register_context(context)
        return context
    
    async def execute(self, session_id: str, command: str, params: Dict[str, Any], participant_id: str) -> Dict[str, Any]:
        """Execute tool command with ToF validation"""
        result = await super().execute(session_id, command, params, participant_id)
        
        if result.get("status") != "error":
            # Run ToF tests
            test_results = await self.tof.run_context_tests(session_id)
            if not all(r.passed for r in test_results):
                result["warnings"] = [r.details for r in test_results if not r.passed]
        
        return result