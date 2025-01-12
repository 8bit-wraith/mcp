#!/usr/bin/env python3

"""
Git Context Visualizer using Gradio
Provides an interactive interface for visualizing Git context data
"""

import gradio as gr
import git
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import networkx as nx
from pathlib import Path
import json
from collections import Counter
import numpy as np

class GitContextVisualizer:
    def __init__(self, repo_path="."):
        self.repo = git.Repo(repo_path)
        self.cache = {}
    
    def get_commit_history(self):
        """Get commit history as a pandas DataFrame"""
        if 'commits' not in self.cache:
            commits = []
            for commit in self.repo.iter_commits():
                commits.append({
                    'hash': commit.hexsha[:7],
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': commit.committed_datetime,
                    'files_changed': len(commit.stats.files)
                })
            self.cache['commits'] = pd.DataFrame(commits)
        return self.cache['commits']
    
    def create_commit_timeline(self):
        """Create an interactive timeline of commits"""
        df = self.get_commit_history()
        fig = px.scatter(df, x='date', y='files_changed',
                        hover_data=['hash', 'message', 'author'],
                        title='Commit Timeline',
                        labels={'date': 'Date', 'files_changed': 'Files Changed'},
                        color='author')
        fig.update_layout(height=500)
        return fig

    def create_author_stats(self):
        """Create author contribution statistics"""
        df = self.get_commit_history()
        author_stats = df.groupby('author').agg({
            'hash': 'count',
            'files_changed': 'sum'
        }).reset_index()
        author_stats.columns = ['Author', 'Commits', 'Files Changed']
        
        fig = go.Figure(data=[
            go.Bar(name='Commits', x=author_stats['Author'], y=author_stats['Commits']),
            go.Bar(name='Files Changed', x=author_stats['Author'], y=author_stats['Files Changed'])
        ])
        fig.update_layout(
            title='Author Contributions',
            barmode='group',
            height=400
        )
        return fig

    def create_file_type_chart(self):
        """Create a pie chart of file types"""
        files = list(Path('.').rglob('*'))
        extensions = Counter(f.suffix for f in files if f.suffix)
        
        fig = px.pie(
            values=list(extensions.values()),
            names=list(extensions.keys()),
            title='File Types Distribution'
        )
        fig.update_layout(height=400)
        return fig

def create_gradio_interface():
    """Create the Gradio interface"""
    visualizer = GitContextVisualizer()
    
    with gr.Blocks(title="Git Context Visualizer", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# Git Context Visualizer")
        gr.Markdown("### Tri says: Let's make these numbers dance! 💃📊")
        
        with gr.Tab("Timeline"):
            timeline_plot = gr.Plot(visualizer.create_commit_timeline())
            gr.Markdown("*Hover over points to see commit details*")
        
        with gr.Tab("Contributors"):
            author_plot = gr.Plot(visualizer.create_author_stats())
            gr.Markdown("*Compare commit counts and files changed per author*")
        
        with gr.Tab("File Types"):
            filetype_plot = gr.Plot(visualizer.create_file_type_chart())
            gr.Markdown("*Distribution of different file types in the project*")
        
        refresh_btn = gr.Button("🔄 Refresh Visualizations")
        refresh_btn.click(
            fn=lambda: [
                visualizer.create_commit_timeline(),
                visualizer.create_author_stats(),
                visualizer.create_file_type_chart()
            ],
            outputs=[timeline_plot, author_plot, filetype_plot]
        )
        
        gr.Markdown("---")
        gr.Markdown("*Tri's Tip: Keep your code clean, and your visualizations will sparkle! ✨*")
    
    return interface

if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        auth=("aht", "8b.is")  # Basic auth for demo
    ) 