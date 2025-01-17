import psutil
import platform
from typing import Dict, Any
from ..core.plugin import Tool
from ..core.context import ToolContext

class SystemTools(Tool):
    name = "system"
    description = "System monitoring and management with contextual awareness"
    
    async def _execute_command(self, command: str, params: Dict[str, Any], context: ToolContext) -> Dict[str, Any]:
        commands = {
            "status": self._get_system_status,
            "processes": self._list_processes,
            "resources": self._monitor_resources
        }
        
        if command not in commands:
            raise ValueError(f"Unknown command: {command}")
        
        result = await commands[command](params, context)
        
        # Add some contextual feelings based on system state
        if command == "resources":
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Generate insights based on resource usage
            insights = []
            if cpu_percent > 80:
                insights.append("CPU usage is very high!")
            if memory_percent > 80:
                insights.append("Memory usage is concerning")
                
            # Add feeling to context
            context.add_feeling(
                participant_id="system",
                mood="stressed" if cpu_percent > 80 else "relaxed",
                confidence=0.9,
                insights=insights
            )
        
        return result
    
    async def _get_system_status(self, params: Dict[str, Any], context: ToolContext) -> Dict[str, Any]:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "context_participants": len(context.participants)
        } 