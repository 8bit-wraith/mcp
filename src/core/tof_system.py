from typing import Dict, Optional, List, Any
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from .context_store import ContextStore

logger = logging.getLogger(__name__)

class ContextType(Enum):
    TEST = "test"
    TOOL = "tool"
    PARTICIPANT = "participant"
    FEELING = "feeling"
    CONVERSATION = "conversation"
    SYSTEM = "system"
    MEMORY = "memory"        # For long-term memory storage
    INTENTION = "intention"  # For capturing AI/human intentions
    EMOTION = "emotion"      # For emotional state tracking
    LEARNING = "learning"    # For tracking learning progress

@dataclass
class ContextMetadata:
    created_at: datetime
    last_validated: Optional[datetime]
    validation_count: int
    context_type: ContextType
    tags: List[str]
    version: int = 1  # Added version tracking
    parent_id: Optional[str] = None  # For tracking context lineage

class Context:
    def __init__(
        self, 
        context_id: str, 
        data: Dict,
        context_type: ContextType,
        tags: List[str] = None,
        parent_id: Optional[str] = None
    ):
        self.context_id = context_id
        self.data = data
        self.metadata = ContextMetadata(
            created_at=datetime.now(),
            last_validated=None,
            validation_count=0,
            context_type=context_type,
            tags=tags or [],
            parent_id=parent_id
        )
        self._previous_states: List[Dict] = []  # Track context changes

    def update_validation(self):
        """Update validation metadata"""
        self.metadata.last_validated = datetime.now()
        self.metadata.validation_count += 1

    def save_state(self):
        """Save current state for potential recovery"""
        self._previous_states.append({
            "data": self.data.copy(),
            "timestamp": datetime.now(),
            "version": self.metadata.version
        })
        self.metadata.version += 1

class ValidationResult:
    def __init__(self, passed: bool, message: str, context_id: str):
        self.passed = passed
        self.message = message
        self.timestamp = datetime.now()
        self.context_id = context_id

class ToFManager:
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.contexts: Dict[str, Context] = {}
        self.results: Dict[str, List[ValidationResult]] = {}
        self.context_store = ContextStore(host=qdrant_host, port=qdrant_port)
        
    async def register_context(
        self, 
        context_id: str, 
        data: Dict,
        context_type: ContextType,
        tags: List[str] = None,
        parent_id: Optional[str] = None
    ) -> Context:
        """Register a new context with the ToF system"""
        if context_id in self.contexts:
            logger.warning(f"Context {context_id} already exists, updating...")
        
        context = Context(context_id, data, context_type, tags, parent_id)
        self.contexts[context_id] = context
        self.results[context_id] = []
        
        # Store in Qdrant
        await self.context_store.store_context(context)
        
        logger.info(f"Registered new context: {context_id} of type {context_type.value}")
        return context
    
    async def validate_context(self, context_id: str) -> ValidationResult:
        """Validate a context's integrity"""
        context = self.contexts.get(context_id)
        if not context:
            result = ValidationResult(False, "Context not found", context_id)
            logger.error(f"Failed to validate non-existent context: {context_id}")
            return result
        
        try:
            # Save current state before validation
            context.save_state()
            
            # Perform validation based on context type
            if context.metadata.context_type == ContextType.TEST:
                valid = await self._validate_test_context(context)
            elif context.metadata.context_type == ContextType.TOOL:
                valid = await self._validate_tool_context(context)
            elif context.metadata.context_type == ContextType.MEMORY:
                valid = await self._validate_memory_context(context)
            elif context.metadata.context_type == ContextType.INTENTION:
                valid = await self._validate_intention_context(context)
            elif context.metadata.context_type == ContextType.EMOTION:
                valid = await self._validate_emotion_context(context)
            elif context.metadata.context_type == ContextType.LEARNING:
                valid = await self._validate_learning_context(context)
            else:
                valid = await self._validate_generic_context(context)
            
            message = "Context validated successfully" if valid else "Context validation failed"
            result = ValidationResult(valid, message, context_id)
            
            if valid:
                context.update_validation()
                # Update in Qdrant
                await self.context_store.store_context(context)
                logger.info(f"Successfully validated context: {context_id}")
            else:
                logger.warning(f"Context validation failed: {context_id}")
            
            self.results[context_id].append(result)
            return result
            
        except Exception as e:
            error_msg = f"Error during context validation: {str(e)}"
            logger.error(error_msg)
            result = ValidationResult(False, error_msg, context_id)
            self.results[context_id].append(result)
            return result
    
    async def _validate_test_context(self, context: Context) -> bool:
        """Validate test-specific context"""
        required_fields = ["test_name", "test_result", "timestamp"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_tool_context(self, context: Context) -> bool:
        """Validate tool-specific context"""
        required_fields = ["tool_name", "tool_state", "last_execution"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_memory_context(self, context: Context) -> bool:
        """Validate memory-specific context"""
        required_fields = ["memory_type", "content", "timestamp", "importance"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_intention_context(self, context: Context) -> bool:
        """Validate intention-specific context"""
        required_fields = ["actor", "intention", "confidence", "timestamp"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_emotion_context(self, context: Context) -> bool:
        """Validate emotion-specific context"""
        required_fields = ["emotion_type", "intensity", "trigger", "timestamp"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_learning_context(self, context: Context) -> bool:
        """Validate learning-specific context"""
        required_fields = ["topic", "progress", "mastery_level", "last_update"]
        return all(field in context.data for field in required_fields)
    
    async def _validate_generic_context(self, context: Context) -> bool:
        """Validate generic context"""
        return bool(context.data)  # Ensure data is not empty
    
    async def recover_context(self, context_id: str) -> Optional[Context]:
        """Attempt to recover a lost context"""
        context = self.contexts.get(context_id)
        if not context:
            logger.error(f"Cannot recover non-existent context: {context_id}")
            return None
        
        try:
            # First, try to find similar contexts in Qdrant
            similar_contexts = await self.context_store.find_similar_contexts(
                context,
                limit=3,
                score_threshold=0.8
            )
            
            if similar_contexts:
                # Use the most similar context as a reference
                best_match = similar_contexts[0]
                logger.info(f"Found similar context: {best_match['context_id']}")
                
                # If it's a newer version of the same context, use it
                if best_match["context_id"] == context_id and best_match["data"] != context.data:
                    context.data = best_match["data"]
                    await self.context_store.store_context(context)
                    return context
            
            # If no similar contexts help, try to restore from previous states
            if context._previous_states:
                last_state = context._previous_states[-1]
                context.data = last_state["data"]
                logger.info(f"Restored context from previous state (version {last_state['version']})")
                await self.context_store.store_context(context)
                return context
            
        except Exception as e:
            logger.error(f"Error during context recovery: {str(e)}")
        
        return context
    
    def get_context_history(self, context_id: str) -> List[ValidationResult]:
        """Get validation history for a context"""
        return self.results.get(context_id, []) 