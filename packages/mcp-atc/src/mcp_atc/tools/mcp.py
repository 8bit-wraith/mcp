#!/usr/bin/env python3

import sys
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import asyncio
from dataclasses import dataclass
from datetime import datetime

# Initialize rich console for beautiful output
console = Console()

@dataclass
class ToolInfo:
    name: str
    description: str
    categories: List[str]
    emoji: str
    examples: List[str]

class MCP:
    """Master Control Program - Your friendly neighborhood tool suggester! 🤖"""
    
    def __init__(self):
        self.tools: Dict[str, ToolInfo] = {}
        self.context_history: List[str] = []
        self._load_tools()
        
    def _load_tools(self):
        """Load all available tools with their metadata"""
        # Example tools - in production, this would load from a config file
        self.tools = {
            "gak": ToolInfo(
                name="gak",
                description="Global Awesome Keywords - Search files like a ninja!",
                categories=["search", "files", "text"],
                emoji="🔍",
                examples=["gak password", "gak -t py,js function"]
            ),
            "file": ToolInfo(
                name="file",
                description="File operations with style",
                categories=["files", "monitor", "analyze"],
                emoji="📁",
                examples=["file analyze path/to/file", "file watch ."]
            ),
            "system": ToolInfo(
                name="system",
                description="System monitoring with feelings",
                categories=["system", "monitor", "resources"],
                emoji="🖥️",
                examples=["system status", "system resources"]
            )
        }
    
    def suggest_tools(self, context: str) -> List[ToolInfo]:
        """Suggest tools based on the given context"""
        # Add to context history
        self.context_history.append(context)
        
        # Tokenize the context
        tokens = set(re.findall(r'\w+', context.lower()))
        
        # Score each tool based on category and description matches
        tool_scores = []
        for tool in self.tools.values():
            score = 0
            # Check categories
            for category in tool.categories:
                if category in tokens:
                    score += 2
            
            # Check description words
            desc_words = set(re.findall(r'\w+', tool.description.lower()))
            score += len(tokens.intersection(desc_words))
            
            if score > 0:
                tool_scores.append((score, tool))
        
        # Sort by score and return tools
        return [tool for _, tool in sorted(tool_scores, reverse=True)]

    def display_suggestions(self, tools: List[ToolInfo]):
        """Display tool suggestions in a beautiful table"""
        if not tools:
            console.print(Panel("🤔 No matching tools found. Try different keywords!", 
                              title="Tool Suggestions",
                              style="yellow"))
            return
            
        table = Table(title="🛠️  Suggested Tools", show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Example", style="yellow")
        
        for tool in tools:
            table.add_row(
                f"{tool.emoji} {tool.name}",
                tool.description,
                tool.examples[0] if tool.examples else "N/A"
            )
            
        console.print(table)

@click.group()
def cli():
    """MCP - Your friendly neighborhood tool suggester! 🤖"""
    pass

@cli.command()
@click.argument('context', nargs=-1)
def l(context):
    """List tools matching the given context"""
    mcp = MCP()
    context_str = ' '.join(context)
    suggestions = mcp.suggest_tools(context_str)
    mcp.display_suggestions(suggestions)

@cli.command()
@click.argument('tool_name')
@click.argument('args', nargs=-1)
def run(tool_name, args):
    """Run a specific tool with arguments"""
    mcp = MCP()
    if tool_name not in mcp.tools:
        console.print(f"❌ Tool '{tool_name}' not found!", style="bold red")
        return
        
    # In production, this would actually execute the tool
    tool = mcp.tools[tool_name]
    console.print(f"🚀 Running {tool.emoji} {tool_name} with args: {' '.join(args)}")

if __name__ == "__main__":
    cli() 