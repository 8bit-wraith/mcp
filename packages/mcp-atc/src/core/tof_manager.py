from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import inspect
from pathlib import Path
import json
from .context import ToolContext, Participant
from .plugin import Tool
from .test_context_store import ContextualTestStore, TestContext
from .unified_context import ContextManager, UnifiedContext, ContextType

class TestResult:
    """Represents the result of a ToF test"""
    def __init__(self, name: str, passed: bool, context_id: str):
        self.name = name
        self.passed = passed
        self.timestamp = datetime.now()
        self.context_id = context_id
        self.details: Dict[str, Any] = {}

class ToFManager:
    """Enhanced Test or Forget Manager with unified context"""
    
    def __init__(self):
        self.test_history: List[TestResult] = []
        self.active_contexts: Dict[str, ToolContext] = {}
        self.context_manager = ContextManager()
    
    async def run_context_tests(self, context_id: str) -> List[TestResult]:
        context = self.active_contexts.get(context_id)
        if not context:
            raise ValueError(f"Context {context_id} not found")
            
        results = []
        
        for test_func in [self._test_context_integrity, 
                         self._test_participant_state,
                         self._test_history_consistency]:
            # Create unified test context
            test_context = UnifiedContext(
                context_id=f"test_{test_func.__name__}_{datetime.now().isoformat()}",
                context_type=ContextType.TEST,
                timestamp=datetime.now(),
                content={
                    "name": test_func.__name__,
                    "description": test_func.__doc__ or "",
                    "tool_id": context.tool_id,
                    "expected_behavior": "Test should pass without errors",
                    "participants": list(context.participants.keys()),
                    "function_source": inspect.getsource(test_func)
                },
                relationships=[context_id],
                metadata={"tool_context": context.dict()}
            )
            
            # Store context
            await self.context_manager.store_context(test_context)
            
            # Run test
            result = await test_func(context)
            results.append(result)
            
            if not result.passed:
                # Find similar failures
                similar_failures = await self.context_manager.find_similar_contexts(
                    f"failed {test_func.__name__} {str(result.details)}",
                    context_type=ContextType.TEST
                )
                result.details["similar_failures"] = [
                    c.dict() for c in similar_failures
                ]
        
        return results
    
    async def _test_context_integrity(self, context: ToolContext) -> TestResult:
        """Test if context data is complete and valid"""
        result = TestResult("context_integrity", True, context.session_id)
        
        try:
            # Check essential context properties
            assert context.tool_id is not None
            assert context.session_id is not None
            assert isinstance(context.participants, dict)
            assert isinstance(context.history, list)
            assert isinstance(context.feelings, list)
            
            # Verify context can be serialized/deserialized
            context_dict = context.dict()
            json.dumps(context_dict)  # Test serialization
            
        except Exception as e:
            result.passed = False
            result.details["error"] = str(e)
            
        return result
    
    async def _test_participant_state(self, context: ToolContext) -> TestResult:
        """Test if all participants are in valid states"""
        result = TestResult("participant_state", True, context.session_id)
        
        try:
            for participant_id, participant in context.participants.items():
                # Verify participant data
                assert participant.id == participant_id
                assert participant.type in ["ai", "human"]
                
                # Check for recent activity
                recent_history = [h for h in context.history 
                                if h["participant_id"] == participant_id]
                if recent_history:
                    last_activity = datetime.fromisoformat(str(recent_history[-1]["timestamp"]))
                    if (datetime.now() - last_activity).total_seconds() > 3600:
                        result.details[f"warning_{participant_id}"] = "Participant inactive for >1 hour"
                
        except Exception as e:
            result.passed = False
            result.details["error"] = str(e)
            
        return result
    
    async def _test_history_consistency(self, context: ToolContext) -> TestResult:
        """Test if history is consistent and commands are valid"""
        result = TestResult("history_consistency", True, context.session_id)
        
        try:
            if context.history:
                # Check history order
                timestamps = [datetime.fromisoformat(str(h["timestamp"])) 
                            for h in context.history]
                assert all(t1 <= t2 for t1, t2 in zip(timestamps[:-1], timestamps[1:]))
                
                # Verify all commands had participants
                for entry in context.history:
                    assert entry["participant_id"] in context.participants
                    
        except Exception as e:
            result.passed = False
            result.details["error"] = str(e)
            
        return result
    
    async def _trigger_recovery(self, context: ToolContext, failed_results: List[TestResult]):
        """Attempt to recover from test failures"""
        recovery_actions = {
            "context_integrity": self._recover_context_integrity,
            "participant_state": self._recover_participant_state,
            "history_consistency": self._recover_history_consistency
        }
        
        for result in failed_results:
            if not result.passed:
                recover_func = recovery_actions.get(result.name)
                if recover_func:
                    await recover_func(context, result) 