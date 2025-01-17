import magic
import asyncio
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ..core.plugin import Tool

class FileTools(Tool):
    name = "file"
    description = "Advanced file operations and monitoring"
    
    def __init__(self):
        self.magic = magic.Magic(mime=True)
        self.observers: Dict[str, Observer] = {}
    
    async def execute(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        commands = {
            "analyze": self._analyze_file,
            "watch": self._watch_directory,
            "find": self._find_files,
            "type": self._get_file_type
        }
        
        if command not in commands:
            raise ValueError(f"Unknown command: {command}")
            
        return await commands[command](params)
    
    async def _analyze_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a file and return detailed information"""
        path = Path(params["path"])
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        return {
            "name": path.name,
            "size": path.stat().st_size,
            "type": self.magic.from_file(str(path)),
            "created": path.stat().st_ctime,
            "modified": path.stat().st_mtime
        }
    
    async def _watch_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Watch a directory for changes"""
        path = params["path"]
        if path in self.observers:
            return {"message": f"Already watching {path}"}
            
        event_handler = FileSystemEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=params.get("recursive", False))
        observer.start()
        
        self.observers[path] = observer
        return {"message": f"Started watching {path}"} 