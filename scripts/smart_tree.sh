#!/usr/bin/env python3

import os
import stat
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Set

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

    def __init__(self, root_path: str, display_mode: str = 'classic'):
        self.root = Path(root_path).resolve()
        self.nodes: Dict[Path, FileNode] = {}
        self.display_mode = display_mode
        self.use_color = True
        self._build_tree()

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

    def _build_tree(self):
        """Build the initial tree structure"""
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root).relative_to(self.root)
            
            # Add current directory if not root
            if root_path != Path('.'):
                full_path = self.root / root_path
                self.nodes[root_path] = FileNode(
                    path=root_path,
                    is_dir=True,
                    stat_info=full_path.stat()
                )

            # Add files
            for file in files:
                file_path = root_path / file
                full_path = self.root / file_path
                if full_path.exists():  # Check to avoid broken symlinks
                    self.nodes[file_path] = FileNode(
                        path=file_path,
                        is_dir=False,
                        stat_info=full_path.stat()
                    )

    def format_hex_node(self, path: Path, depth: int = 0) -> str:
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
        
        if self.use_color:
            return (f"{self.COLORS['depth']}{depth_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['perm']}{perms_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['id']}{uid_hex} {gid_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['size']}{size_hex}{self.COLORS['reset']} "
                   f"{self.COLORS['time']}{time_hex}{self.COLORS['reset']} "
                   f"{emoji} {path.name}")
        else:
            return f"{depth_hex} {perms_hex} {uid_hex} {gid_hex} {size_hex} {time_hex} {emoji} {path.name}"

    def display(self, path: Path = None, depth: int = 0) -> str:
        """Display the tree structure"""
        if path is None:
            path = Path('.')
            
        result = []
        
        # Handle root specially
        if path == Path('.'):
            result.append(self.format_hex_node(path, depth))
            
        # Get and sort children
        children = sorted([
            p for p in self.nodes.keys()
            if p.parent == path and p != path
        ])
        
        # Display each child
        for child in children:
            result.append(self.format_hex_node(child, depth + 1))
            if self.nodes[child].is_dir:
                # Recurse into directory
                result.extend(self.display(child, depth + 1).split('\n')[1:])
                
        return '\n'.join(result)

def main():
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    tree = SmartTree(path)
    print(tree.display())

if __name__ == '__main__':
    main()