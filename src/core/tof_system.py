#!/usr/bin/env python3

"""
Test or Forget (ToF) system implementation.
Tri says: Testing is like double-entry bookkeeping - everything must be verified! 🔍
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import Context, ContextType, ValidationResult
from .context_store import ContextStore

logger = logging.getLogger(__name__)

class ToFManager:
    """Manages context testing and validation"""
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        """Initialize the ToF manager"""
        self.contexts: Dict[str, Context] = {}  # Initialize as empty dict
        self.results: Dict[str, List[ValidationResult]] = {}  # Initialize as empty dict
        self.context_store = ContextStore(host=qdrant_host, port=qdrant_port)
    
    async def register_context(
        self,
        context_id: str,
        data: Dict[str, Any],
        context_type: ContextType,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None
    ) -> Context:
        """Register a new context for testing"""
        context = Context(
            context_id=context_id,
            data=data,
            context_type=context_type,
            tags=tags or [],
            parent_id=parent_id
        )
        self.contexts[context_id] = context
        self.results[context_id] = []
        
        # Store in Qdrant
        await self.context_store.store_context(context)
        logger.info(f"Registered context: {context_id}")
        return context
    
    async def validate_context(self, context_id: str) -> ValidationResult:
        """Validate a context based on its type"""
        context = self.contexts.get(context_id)
        if not context:
            msg = f"Context not found: {context_id}"
            logger.error(msg)
            return ValidationResult(valid=False, message=msg, context_id=context_id)
        
        try:
            # Save current state before validation
            context.save_state()
            
            # Validate based on context type
            result = await self._validate_context_by_type(context)
            
            # Update validation metadata
            if result.valid:
                context.update_validation()
            
            # Store result
            self.results[context_id].append(result)
            return result
            
        except Exception as e:
            msg = f"Error validating context: {str(e)}"
            logger.error(msg)
            return ValidationResult(valid=False, message=msg, context_id=context_id)
    
    async def _validate_context_by_type(self, context: Context) -> ValidationResult:
        """Validate context based on its type"""
        
        validation_methods = {
            ContextType.TEST: self._validate_test_context,
            ContextType.TOOL: self._validate_tool_context,
            ContextType.MEMORY: self._validate_memory_context,
            ContextType.INTENTION: self._validate_intention_context,
            ContextType.EMOTION: self._validate_emotion_context,
            ContextType.LEARNING: self._validate_learning_context,
            ContextType.SYSTEM: self._validate_system_context
        }
        
        validate_method = validation_methods.get(
            context.metadata.context_type,
            self._validate_generic_context
        )
        
        return await validate_method(context)
    
    async def _validate_test_context(self, context: Context) -> ValidationResult:
        """Validate a test context"""
        required_fields = {"test_name", "test_result"}
        if not all(field in context.data for field in required_fields):
            return ValidationResult(
                valid=False,
                message=f"Missing required fields: {required_fields - set(context.data.keys())}",
                context_id=context.context_id
            )
        return ValidationResult(
            valid=True,
            message="Test context validated successfully",
            context_id=context.context_id
        )
    
    async def _validate_tool_context(self, context: Context) -> ValidationResult:
        """Validate a tool context"""
        required_fields = {"tool_name", "tool_state"}
        if not all(field in context.data for field in required_fields):
            return ValidationResult(
                valid=False,
                message=f"Missing required fields: {required_fields - set(context.data.keys())}",
                context_id=context.context_id
            )
        return ValidationResult(
            valid=True,
            message="Tool context validated successfully",
            context_id=context.context_id
        )
    
    async def _validate_generic_context(self, context: Context) -> ValidationResult:
        """Generic validation for unhandled context types"""
        return ValidationResult(
            valid=True,
            message=f"Generic validation passed for type: {context.metadata.context_type}",
            context_id=context.context_id
        )
    
    async def get_validation_history(self, context_id: str) -> List[ValidationResult]:
        """Get validation history for a context"""
        return self.results.get(context_id, []) 