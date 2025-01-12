#!/usr/bin/env python3
"""Git Context Visualizer - Interactive interface for Git Context Builder."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import gradio as gr
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from fastapi import FastAPI, WebSocket
from git_context_builder import GitContextBuilder
from pyvis.network import Network

# Initialize FastAPI for WebSocket support
app = FastAPI()
websocket_clients = set()

async def broadcast_update(data: Dict):
    """Broadcast updates to all connected WebSocket clients."""
    for client in websocket_clients:
        try:
            await client.send_json(data)
        except:
            websocket_clients.remove(client)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        websocket_clients.remove(websocket)

class GitContextVisualizer:
    """Interactive visualizer for Git contexts."""
    
    def __init__(self):
        self.builder = GitContextBuilder()
        self.current_context = None
    
    def build_relationship_graph(self, context_name: str) -> go.Figure:
        """Build an interactive graph of relationships."""
        G = nx.Graph()
        
        # Get commits
        commits = self.builder.client.scroll(
            collection_name="git_commits",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_name",
                        match=models.MatchValue(value=context_name)
                    )
                ]
            ),
            limit=1000
        )[0]
        
        # Add commit nodes
        for commit in commits:
            G.add_node(
                commit.payload["commit_hash"],
                type="commit",
                message=commit.payload["message"],
                author=commit.payload["author_name"]
            )
        
        # Get relationships
        relationships = self.builder.client.scroll(
            collection_name="git_relationships",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_name",
                        match=models.MatchValue(value=context_name)
                    )
                ]
            ),
            limit=1000
        )[0]
        
        # Add relationship edges
        for rel in relationships:
            G.add_edge(
                rel.payload["source_id"],
                rel.payload["target_id"],
                weight=rel.payload["similarity"],
                type=rel.payload["type"]
            )
        
        # Create interactive visualization
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        net.from_nx(G)
        net.show_buttons(filter_=['physics'])
        
        # Save to temporary file
        temp_path = Path("temp_graph.html")
        net.save_graph(str(temp_path))
        
        return temp_path.read_text()
    
    def create_commit_timeline(self, context_name: str) -> go.Figure:
        """Create an interactive commit timeline."""
        commits = self.builder.client.scroll(
            collection_name="git_commits",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_name",
                        match=models.MatchValue(value=context_name)
                    )
                ]
            ),
            limit=1000
        )[0]
        
        dates = [datetime.fromisoformat(c.payload["timestamp"]) for c in commits]
        authors = [c.payload["author_name"] for c in commits]
        messages = [c.payload["message"] for c in commits]
        
        fig = px.scatter(
            x=dates,
            y=authors,
            hover_data={"message": messages},
            title="Commit Timeline",
            labels={"x": "Date", "y": "Author"}
        )
        
        return fig
    
    def create_file_treemap(self, context_name: str) -> go.Figure:
        """Create an interactive treemap of files."""
        files = self.builder.client.scroll(
            collection_name="git_files",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_name",
                        match=models.MatchValue(value=context_name)
                    )
                ]
            ),
            limit=1000
        )[0]
        
        paths = [f.payload["path"] for f in files]
        sizes = [f.payload["size"] for f in files]
        
        fig = px.treemap(
            names=paths,
            parents=["/".join(Path(p).parts[:-1]) or "/" for p in paths],
            values=sizes,
            title="File Structure"
        )
        
        return fig
    
    async def build_context_ui(
        self,
        repo_path: str,
        context_name: str,
        is_multi: bool
    ) -> Dict:
        """Build context and return visualizations."""
        # Build context
        await self.builder.build_context(repo_path, context_name, is_multi)
        self.current_context = context_name
        
        # Create visualizations
        graph_html = self.build_relationship_graph(context_name)
        timeline = self.create_commit_timeline(context_name)
        treemap = self.create_file_treemap(context_name)
        
        # Broadcast update
        await broadcast_update({
            "type": "context_built",
            "context_name": context_name,
            "repo_path": repo_path
        })
        
        return {
            "graph": graph_html,
            "timeline": timeline,
            "treemap": treemap,
            "message": f"Context '{context_name}' built successfully!"
        }
    
    async def analyze_context_ui(self, context_name: str) -> Dict:
        """Analyze context and return visualizations."""
        analysis = await self.builder.analyze_context(context_name)
        
        # Create busy hours chart
        hours = list(analysis["commits"]["busy_times"].keys())
        counts = list(analysis["commits"]["busy_times"].values())
        busy_hours = px.bar(
            x=hours,
            y=counts,
            title="Commit Activity by Hour",
            labels={"x": "Hour", "y": "Number of Commits"}
        )
        
        # Create file types pie chart
        types = list(analysis["files"]["types"].keys())
        type_counts = list(analysis["files"]["types"].values())
        file_types = px.pie(
            values=type_counts,
            names=types,
            title="File Types Distribution"
        )
        
        # Broadcast update
        await broadcast_update({
            "type": "context_analyzed",
            "context_name": context_name,
            "stats": analysis
        })
        
        return {
            "busy_hours": busy_hours,
            "file_types": file_types,
            "stats": f"""
            Analysis for {context_name}:
            - Total commits: {analysis['commits']['total']}
            - Total authors: {len(analysis['commits']['authors'])}
            - Total files: {analysis['files']['total']}
            - Similar commits: {analysis['relationships']['similar_commits']}
            - Cross-repo relationships: {analysis['relationships']['cross_repo']}
            """
        }

def create_gradio_interface():
    """Create the Gradio interface."""
    visualizer = GitContextVisualizer()
    
    with gr.Blocks(title="Git Context Explorer") as interface:
        gr.Markdown("# 🔍 Git Context Explorer")
        gr.Markdown("Analyze and visualize Git repositories with the power of AI!")
        
        with gr.Tab("Build Context"):
            with gr.Row():
                repo_path = gr.Textbox(label="Repository Path")
                context_name = gr.Textbox(label="Context Name")
                is_multi = gr.Checkbox(label="Multi-Repository Context")
            
            build_btn = gr.Button("Build Context")
            
            with gr.Row():
                graph_output = gr.HTML(label="Relationship Graph")
                timeline_output = gr.Plot(label="Commit Timeline")
            
            with gr.Row():
                treemap_output = gr.Plot(label="File Structure")
                message_output = gr.Textbox(label="Status")
        
        with gr.Tab("Analyze Context"):
            context_select = gr.Dropdown(
                label="Select Context",
                choices=lambda: asyncio.run(visualizer.builder.list_contexts())
            )
            analyze_btn = gr.Button("Analyze Context")
            
            with gr.Row():
                busy_hours_output = gr.Plot(label="Commit Activity")
                file_types_output = gr.Plot(label="File Types")
            
            stats_output = gr.Textbox(label="Statistics")
        
        # Event handlers
        build_btn.click(
            fn=lambda p, n, m: asyncio.run(visualizer.build_context_ui(p, n, m)),
            inputs=[repo_path, context_name, is_multi],
            outputs=[graph_output, timeline_output, treemap_output, message_output]
        )
        
        analyze_btn.click(
            fn=lambda c: asyncio.run(visualizer.analyze_context_ui(c)),
            inputs=[context_select],
            outputs=[busy_hours_output, file_types_output, stats_output]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch(server_name="0.0.0.0", share=True) 