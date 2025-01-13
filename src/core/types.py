#!/usr/bin/env python3

"""
Core type definitions for the MCP system.
Tri says: Types are like receipts - they help keep everything organized! 📋
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

class ContextType(Enum):
    """Types of contexts supported by the system"""
    TEST = "TEST"
    TOOL = "TOOL"
    MEMORY = "MEMORY"
    INTENTION = "INTENTION"
    EMOTION = "EMOTION"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"

@dataclass
class ContextMetadata:
    """Metadata for a context instance"""
    context_type: ContextType
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    version: int = 1

@dataclass
class Context:
    """A context instance in the system"""
    context_id: str
    data: Dict[str, Any]
    metadata: ContextMetadata
    _previous_states: List[Dict] = field(default_factory=list)
    
    def __init__(
        self,
        context_id: str,
        data: Dict[str, Any],
        context_type: ContextType,
        tags: List[str] = None,
        parent_id: Optional[str] = None
    ):
        self.context_id = context_id
        self.data = data
        self.metadata = ContextMetadata(
            context_type=context_type,
            tags=tags or []
        )
        self._previous_states = []
        if parent_id:
            self.data["parent_id"] = parent_id
    
    def save_state(self):
        """Save current state for potential recovery"""
        self._previous_states.append({
            "version": self.metadata.version,
            "data": self.data.copy(),
            "timestamp": datetime.now()
        })
    
    def update_validation(self):
        """Update validation metadata"""
        self.metadata.last_validated = datetime.now()
        self.metadata.validation_count += 1
        self.metadata.version += 1

@dataclass
class ValidationResult:
    """Result of a context validation"""
    valid: bool
    message: str
    context_id: str
    timestamp: datetime = field(default_factory=datetime.now)