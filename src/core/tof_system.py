from typing import Dict, Optional, List
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContextType(Enum):
    TEST = "test"
    TOOL = "tool"
    PARTICIPANT = "participant"
    FEELING = "feeling"
    CONVERSATION = "conversation"
    SYSTEM = "system"

@dataclass
class ContextMetadata:
    created_at: datetime
    last_validated: Optional[datetime]
    validation_count: int
    context_type: ContextType
    tags: List[str]

class Context:
    def __init__(
        self, 
        context_id: str, 
        data: Dict,
        context_type: ContextType,
        tags: List[str] = None
    ):
        self.context_id = context_id
        self.data = data
        self.metadata = ContextMetadata(
            created_at=datetime.now(),
            last_validated=None,
            validation_count=0,
            context_type=context_type,
            tags=tags or []
        )

    def update_validation(self):
        """Update validation metadata"""
        self.metadata.last_validated = datetime.now()
        self.metadata.validation_count += 1

class ValidationResult:
    def __init__(self, passed: bool, message: str, context_id: str):
        self.passed = passed
        self.message = message
        self.timestamp = datetime.now()
        self.context_id = context_id

class ToFManager:
    def __init__(self):
        self.contexts: Dict[str, Context] = {}
        self.results: Dict[str, List[ValidationResult]] = {}
        
    async def register_context(
        self, 
        context_id: str, 
        data: Dict,
        context_type: ContextType,
        tags: List[str] = None
    ) -> Context:
        """Register a new context with the ToF system"""
        if context_id in self.contexts:
            logger.warning(f"Context {context_id} already exists, updating...")
        
        context = Context(context_id, data, context_type, tags)
        self.contexts[context_id] = context
        self.results[context_id] = []
        
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
            # Perform validation based on context type
            if context.metadata.context_type == ContextType.TEST:
                valid = await self._validate_test_context(context)
            elif context.metadata.context_type == ContextType.TOOL:
                valid = await self._validate_tool_context(context)
            else:
                valid = await self._validate_generic_context(context)
            
            message = "Context validated successfully" if valid else "Context validation failed"
            result = ValidationResult(valid, message, context_id)
            
            if valid:
                context.update_validation()
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
    
    async def _validate_generic_context(self, context: Context) -> bool:
        """Validate generic context"""
        return bool(context.data)  # Ensure data is not empty
    
    async def recover_context(self, context_id: str) -> Optional[Context]:
        """Attempt to recover a lost context"""
        context = self.contexts.get(context_id)
        if not context:
            logger.error(f"Cannot recover non-existent context: {context_id}")
            return None
        
        # Get validation history
        history = self.results.get(context_id, [])
        if not history:
            logger.warning(f"No validation history for context: {context_id}")
            return context
        
        # Check if context needs recovery
        latest_validation = history[-1]
        if not latest_validation.passed:
            logger.info(f"Attempting to recover context: {context_id}")
            # In a real implementation, we would attempt recovery strategies here
            # For now, we just return the existing context
            return context
        
        return context
    
    def get_context_history(self, context_id: str) -> List[ValidationResult]:
        """Get validation history for a context"""
        return self.results.get(context_id, []) 