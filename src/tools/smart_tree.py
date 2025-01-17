#!/usr/bin/env python3

import os
import stat
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class FileNode:
    """Represents a file or directory in the tree with additional context"""
    path: Path
    is_dir: bool
    stat_info: os.stat_result = None
    references: Set[Path] = field(default_factory=set)
    referenced_by: Set[Path] = field(default_factory=set)
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[Path] = field(default_factory=set)

class SmartTree:
    COLORS = {
        'depth': '\033[36m',  # cyan for depth
        'perm': '\033[33m',   # yellow for permissions
        'id': '\033[35m',     # magenta for uid/gid
        'size': '\033[32m',   # green for size
        'time': '\033[34m',   # blue for timestamp
        'reset': '\033[0m'    # reset
    }

    def __init__(self, root_path: str, display_mode: str = 'classic', use_color: bool = True):
        self.root = Path(root_path).resolve()
        self.nodes: Dict[Path, FileNode] = {}
        self.gitignore_patterns = self._load_gitignore()
        self.display_mode = display_mode
        self.use_color = use_color
        
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

    def _get_file_emoji(self, mode):
        """Get appropriate emoji for file type"""
        if stat.S_ISDIR(mode): return "📁"
        elif stat.S_ISLNK(mode): return "🔗"
        elif mode & stat.S_IXUSR: return "⚙️"
        elif stat.S_ISSOCK(mode): return "🔌"
        elif stat.S_ISFIFO(mode): return "📝"
        elif stat.S_ISBLK(mode): return "💾"
        elif stat.S_ISCHR(mode): return "📺"
        else: return "📄"

    def build(self):
        """Build the smart tree structure"""
        # First pass: collect all files and directories
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root).relative_to(self.root)
            
            # Add directories
            if root_path != Path('.'):
                if not self._should_ignore(self.root / root_path):
                    stat_info = (self.root / root_path).stat()
                    self.nodes[root_path] = FileNode(root_path, True, stat_info)

            # Add files
            for file in files:
                file_path = root_path / file
                if not self._should_ignore(self.root / file_path):
                    stat_info = (self.root / file_path).stat()
                    self.nodes[file_path] = FileNode(file_path, False, stat_info)

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

    def _format_hex_node(self, path: Path, depth: int = 0) -> str:
        """Format a node in hex format with all metadata"""
        node = self.nodes[path]
        stat_info = node.stat_info
        
        # Convert values to hex
        perms_hex = f"{stat_info.st_mode & 0o777:03x}"
        uid_hex = f"{stat_info.st_uid:x}"
        gid_hex = f"{stat_info.st_gid:x}"
        size_hex = f"{stat_info.st_size:x}"
        time_hex = f"{int(stat_info.st_mtime):x}"
        depth_hex = f"{depth:x}"
        
        emoji = self._get_file_emoji(stat_info.st_mode)
        
        refs = ""
        if node.references:
            refs = f" → {', '.join(str(r) for r in sorted(node.references))}"
        
        if self.use_color:
            return (f"{self.COLORS['depth']}{depth_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['perm']}{perms_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['id']}{uid_hex} {gid_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['size']}{size_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['time']}{time_hex}{self.COLORS['reset']} "
                   f"{emoji} {path.name}{refs}")
        else:
            return f"{depth_hex} {perms_hex} {uid_hex} {gid_hex} {size_hex} {time_hex} {emoji} {path.name}{refs}"

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

    def _display_hex(self, path: Optional[Path] = None, depth: int = 0) -> str:
        """Display the tree in hex format"""
        if path is None:
            path = Path('.')
            
        result = []
        if path == Path('.'):
            root_stat = self.root.stat()
            result.append(self._format_hex_node(path, depth))
            
        # Get all immediate children
        children = sorted([
            p for p in self.nodes.keys()
            if p.parent == path and p != path
        ])
        
        # Display each child
        for child in children:
            result.append(self._format_hex_node(child, depth + 1))
            
            # Recurse into directories
            if self.nodes[child].is_dir:
                result.extend(self._display_hex(child, depth + 1))
                
        return "\n".join(result)

    def display(self, path: Optional[Path] = None, prefix: str = "") -> str:
        """Display the smart tree in selected format"""
        if self.display_mode == 'hex':
            return self._display_hex(path)
        return self._display_classic(path, prefix)

    def _display_classic(self, path: Optional[Path] = None, prefix: str = "") -> str:
        """Classic tree display format"""
        if path is None:
            path = Path('.')
            
        result = []
        if path == Path('.'):
            result.append(self.root.name)
            prefix = ""
        
        # Get all immediate children
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
                result.extend(self._display_classic(child, next_prefix))
                
        return "\n".join(result)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced tree display with hex format option')
    parser.add_argument('path', nargs='?', default='.', help='Root path to display')
    parser.add_argument('--hex', action='store_true', help='Use hex format display')
    parser.add_argument('--no-color', action='store_true', help='Disable color output')
    args = parser.parse_args()

    mode = 'hex' if args.hex else 'classic'
    tree = SmartTree(args.path, display_mode=mode, use_color=not args.no_color)
    tree.build()
    print(tree.display())

if __name__ == "__main__":
    main()