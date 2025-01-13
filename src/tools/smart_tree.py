#!/usr/bin/env python3

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class FileNode:
    """Represents a file or directory in the tree with additional context"""
    path: Path
    is_dir: bool
    references: Set[Path] = field(default_factory=set)
    referenced_by: Set[Path] = field(default_factory=set)
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[Path] = field(default_factory=set)

class SmartTree:
    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        self.nodes: Dict[Path, FileNode] = {}
        self.gitignore_patterns = self._load_gitignore()
        
    def _load_gitignore(self) -> List[str]:
        """Load .gitignore patterns if present"""
        gitignore_path = self.root / '.gitignore'
        if not gitignore_path.exists():
            return []
        
        with open(gitignore_path) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on .gitignore patterns"""
        rel_path = str(path.relative_to(self.root))
        return any(
            rel_path.startswith(pattern.rstrip('/')) or 
            rel_path.endswith(pattern.lstrip('/'))
            for pattern in self.gitignore_patterns
        )

    def _find_python_imports(self, file_path: Path) -> Set[str]:
        """Extract Python imports from a file"""
        if not str(file_path).endswith('.py'):
            return set()

        imports = set()
        try:
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(('import ', 'from ')):
                        imports.add(line)
        except Exception:
            pass
        return imports

    def _scan_file_references(self, file_path: Path, content: str):
        """Scan file content for references to other files"""
        rel_path = file_path.relative_to(self.root)
        node = self.nodes[rel_path]
        
        # Look for file path strings in content
        for other_path in self.nodes:
            if str(other_path) in content:
                node.references.add(other_path)
                self.nodes[other_path].referenced_by.add(rel_path)

    def build(self):
        """Build the smart tree structure"""
        # First pass: collect all files and directories
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root).relative_to(self.root)
            
            # Add directories
            if root_path != Path('.'):
                if not self._should_ignore(self.root / root_path):
                    self.nodes[root_path] = FileNode(root_path, True)

            # Add files
            for file in files:
                file_path = root_path / file
                if not self._should_ignore(self.root / file_path):
                    self.nodes[file_path] = FileNode(file_path, False)

        # Second pass: analyze relationships
        for path, node in self.nodes.items():
            if not node.is_dir:
                try:
                    with open(self.root / path) as f:
                        content = f.read()
                        node.imports = self._find_python_imports(self.root / path)
                        self._scan_file_references(path, content)
                except Exception:
                    pass

    def _format_node(self, path: Path, prefix: str = "", is_last: bool = True) -> List[str]:
        """Format a node for display with its relationships"""
        node = self.nodes[path]
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        lines = [f"{prefix}{current_prefix}{path.name}"]
        
        # Add relationship information if any exists
        if node.references:
            lines.append(f"{prefix}{next_prefix}References:")
            for ref in sorted(node.references):
                lines.append(f"{prefix}{next_prefix}  → {ref}")
                
        if node.referenced_by:
            lines.append(f"{prefix}{next_prefix}Referenced by:")
            for ref in sorted(node.referenced_by):
                lines.append(f"{prefix}{next_prefix}  ← {ref}")
                
        if node.imports:
            lines.append(f"{prefix}{next_prefix}Imports:")
            for imp in sorted(node.imports):
                lines.append(f"{prefix}{next_prefix}  • {imp}")
                
        return lines

    def display(self, path: Optional[Path] = None, prefix: str = "") -> str:
        """Display the smart tree starting from the given path"""
        if path is None:
            path = Path('.')
            
        result = []
        if path == Path('.'):
            result.append(self.root.name)
            prefix = ""
        
        # Get all immediate children of the current path
        children = sorted([
            p for p in self.nodes.keys()
            if p.parent == path and p != path
        ])
        
        # Display each child
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            result.extend(self._format_node(child, prefix, is_last))
            
            # Recurse into directories
            if self.nodes[child].is_dir:
                next_prefix = prefix + ("    " if is_last else "│   ")
                result.extend(self.display(child, next_prefix))
                
        return "\n".join(result)

def main():
    """Main entry point"""
    tree = SmartTree(os.getcwd())
    tree.build()
    print(tree.display())

if __name__ == "__main__":
    main() 