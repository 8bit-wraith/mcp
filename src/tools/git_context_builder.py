#!/usr/bin/env python3
"""Git Context Builder - Analyzes Git repositories and builds context in Qdrant."""

import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import git
from git.repo import Repo
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class GitContextBuilder:
    """Builds and manages Git repository contexts."""
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.model = SentenceTransformer(model_name)
        self._ensure_collections()
    
    def _ensure_collections(self) -> None:
        """Ensure required Qdrant collections exist."""
        collections = self.client.get_collections().collections
        collection_names = {c.name for c in collections}
        
        # Collections we need
        required_collections = {
            "git_commits": 384,  # Commit messages and diffs
            "git_files": 384,    # File contents and metadata
            "git_authors": 384,  # Author information and patterns
            "git_relationships": 384,  # Cross-repository relationships
        }
        
        for name, vector_size in required_collections.items():
            if name not in collection_names:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {name}")
    
    async def build_context(
        self,
        repo_path: str,
        context_name: str,
        multi_repo: bool = False
    ) -> None:
        """Build context from a Git repository."""
        repo = Repo(repo_path)
        logger.info(f"Building context for {repo_path} ({context_name})")
        
        # Process commits
        await self._process_commits(repo, context_name)
        
        # Process files
        await self._process_files(repo, context_name)
        
        # Process authors
        await self._process_authors(repo, context_name)
        
        if not multi_repo:
            # Build initial relationships
            await self._build_relationships(context_name)
    
    async def _process_commits(self, repo: Repo, context_name: str) -> None:
        """Process and store commit information."""
        for commit in repo.iter_commits():
            # Create rich commit text
            commit_text = f"""
            Message: {commit.message}
            Author: {commit.author.name} <{commit.author.email}>
            Date: {commit.authored_datetime}
            Files: {', '.join(d.a_path for d in commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE))}
            """
            
            # Get commit vector
            vector = self.model.encode(commit_text)
            
            # Store in Qdrant
            self.client.upsert(
                collection_name="git_commits",
                points=[models.PointStruct(
                    id=hash(str(commit.hexsha)),
                    vector=vector.tolist(),
                    payload={
                        "context_name": context_name,
                        "commit_hash": commit.hexsha,
                        "message": commit.message,
                        "author_name": commit.author.name,
                        "author_email": commit.author.email,
                        "timestamp": commit.authored_datetime.isoformat(),
                        "stats": {
                            "additions": commit.stats.total["insertions"],
                            "deletions": commit.stats.total["deletions"],
                            "files": commit.stats.total["files"],
                        }
                    }
                )]
            )
    
    async def _process_files(self, repo: Repo, context_name: str) -> None:
        """Process and store file information."""
        for blob in repo.head.commit.tree.traverse():
            if blob.type != 'blob':
                continue
            
            try:
                # Try to decode file content
                content = blob.data_stream.read().decode('utf-8')
                
                # Create rich file text
                file_text = f"""
                Path: {blob.path}
                Content: {content[:1000]}  # First 1000 chars for embedding
                """
                
                # Get file vector
                vector = self.model.encode(file_text)
                
                # Store in Qdrant
                self.client.upsert(
                    collection_name="git_files",
                    points=[models.PointStruct(
                        id=hash(blob.path),
                        vector=vector.tolist(),
                        payload={
                            "context_name": context_name,
                            "path": blob.path,
                            "size": blob.size,
                            "mime_type": blob.mime_type,
                            "last_modified": datetime.fromtimestamp(blob.authored_date).isoformat()
                        }
                    )]
                )
            except UnicodeDecodeError:
                logger.warning(f"Skipping binary file: {blob.path}")
    
    async def _process_authors(self, repo: Repo, context_name: str) -> None:
        """Process and store author information."""
        authors: Dict[str, Dict] = {}
        
        for commit in repo.iter_commits():
            email = commit.author.email
            if email not in authors:
                authors[email] = {
                    "name": commit.author.name,
                    "email": email,
                    "commit_count": 0,
                    "file_patterns": set(),
                    "first_commit": commit.authored_datetime,
                    "last_commit": commit.authored_datetime
                }
            
            authors[email]["commit_count"] += 1
            authors[email]["file_patterns"].update(
                d.a_path for d in commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE)
            )
            authors[email]["last_commit"] = max(
                authors[email]["last_commit"],
                commit.authored_datetime
            )
        
        for email, data in authors.items():
            # Create rich author text
            author_text = f"""
            Name: {data['name']}
            Email: {email}
            Files: {', '.join(data['file_patterns'])}
            """
            
            # Get author vector
            vector = self.model.encode(author_text)
            
            # Store in Qdrant
            self.client.upsert(
                collection_name="git_authors",
                points=[models.PointStruct(
                    id=hash(email),
                    vector=vector.tolist(),
                    payload={
                        "context_name": context_name,
                        "name": data["name"],
                        "email": email,
                        "commit_count": data["commit_count"],
                        "file_patterns": list(data["file_patterns"]),
                        "first_commit": data["first_commit"].isoformat(),
                        "last_commit": data["last_commit"].isoformat()
                    }
                )]
            )
    
    async def _build_relationships(self, context_name: str) -> None:
        """Build relationships between different aspects of the context."""
        # Find related commits (similar changes)
        commits = self.client.scroll(
            collection_name="git_commits",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_name",
                        match=models.MatchValue(value=context_name)
                    )
                ]
            ),
            limit=100
        )[0]
        
        for commit in commits:
            similar = self.client.search(
                collection_name="git_commits",
                query_vector=commit.vector,
                limit=5,
                score_threshold=0.8
            )
            
            for match in similar:
                if match.id != commit.id:
                    # Store relationship
                    self.client.upsert(
                        collection_name="git_relationships",
                        points=[models.PointStruct(
                            id=hash(f"{commit.id}-{match.id}"),
                            vector=np.mean([commit.vector, match.vector], axis=0).tolist(),
                            payload={
                                "context_name": context_name,
                                "type": "similar_commits",
                                "source_id": str(commit.id),
                                "target_id": str(match.id),
                                "similarity": match.score
                            }
                        )]
                    )
    
    async def build_multi_repo_relationships(self, context_name: str) -> None:
        """Build relationships between multiple repositories in a context."""
        # Find all commits in the context
        commits = self.client.scroll(
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
        
        # Find similar commits across repositories
        for commit in commits:
            similar = self.client.search(
                collection_name="git_commits",
                query_vector=commit.vector,
                limit=10,
                score_threshold=0.85
            )
            
            for match in similar:
                if match.id != commit.id:
                    # Store cross-repo relationship
                    self.client.upsert(
                        collection_name="git_relationships",
                        points=[models.PointStruct(
                            id=hash(f"cross-{commit.id}-{match.id}"),
                            vector=np.mean([commit.vector, match.vector], axis=0).tolist(),
                            payload={
                                "context_name": context_name,
                                "type": "cross_repo_similarity",
                                "source_id": str(commit.id),
                                "target_id": str(match.id),
                                "similarity": match.score
                            }
                        )]
                    )
    
    async def list_contexts(self) -> Set[str]:
        """List all available contexts."""
        contexts = set()
        
        # Get contexts from all collections
        for collection in ["git_commits", "git_files", "git_authors", "git_relationships"]:
            results = self.client.scroll(
                collection_name=collection,
                limit=1000
            )[0]
            
            contexts.update(r.payload.get("context_name") for r in results)
        
        return contexts
    
    async def analyze_context(self, context_name: str) -> Dict:
        """Analyze a context and return insights."""
        analysis = {
            "commits": {
                "total": 0,
                "authors": set(),
                "file_types": {},
                "busy_times": {}
            },
            "files": {
                "total": 0,
                "types": {},
                "largest": None
            },
            "authors": {
                "total": 0,
                "most_active": None,
                "file_patterns": {}
            },
            "relationships": {
                "similar_commits": 0,
                "cross_repo": 0
            }
        }
        
        # Analyze commits
        commits = self.client.scroll(
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
        
        for commit in commits:
            analysis["commits"]["total"] += 1
            analysis["commits"]["authors"].add(commit.payload["author_email"])
            
            # Analyze busy times
            hour = datetime.fromisoformat(commit.payload["timestamp"]).hour
            analysis["commits"]["busy_times"][hour] = analysis["commits"]["busy_times"].get(hour, 0) + 1
        
        # Analyze files
        files = self.client.scroll(
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
        
        for file in files:
            analysis["files"]["total"] += 1
            ext = Path(file.payload["path"]).suffix
            analysis["files"]["types"][ext] = analysis["files"]["types"].get(ext, 0) + 1
            
            if not analysis["files"]["largest"] or file.payload["size"] > analysis["files"]["largest"]["size"]:
                analysis["files"]["largest"] = {
                    "path": file.payload["path"],
                    "size": file.payload["size"]
                }
        
        # Analyze relationships
        relationships = self.client.scroll(
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
        
        for rel in relationships:
            if rel.payload["type"] == "similar_commits":
                analysis["relationships"]["similar_commits"] += 1
            elif rel.payload["type"] == "cross_repo_similarity":
                analysis["relationships"]["cross_repo"] += 1
        
        return analysis

async def main():
    parser = argparse.ArgumentParser(description="Git Context Builder")
    parser.add_argument("--repo-path", help="Path to Git repository")
    parser.add_argument("--context-name", help="Name for the context")
    parser.add_argument("--multi-repo", action="store_true", help="Building context for multiple repos")
    parser.add_argument("--build-relationships", action="store_true", help="Build relationships between repos")
    parser.add_argument("--list-contexts", action="store_true", help="List available contexts")
    parser.add_argument("--analyze", action="store_true", help="Analyze a context")
    
    args = parser.parse_args()
    builder = GitContextBuilder()
    
    if args.list_contexts:
        contexts = await builder.list_contexts()
        print("\nAvailable contexts:")
        for ctx in sorted(contexts):
            print(f"- {ctx}")
    
    elif args.analyze:
        if not args.context_name:
            parser.error("--context-name is required for analysis")
        analysis = await builder.analyze_context(args.context_name)
        print(f"\nAnalysis for context: {args.context_name}")
        print(f"Total commits: {analysis['commits']['total']}")
        print(f"Total authors: {len(analysis['commits']['authors'])}")
        print(f"Total files: {analysis['files']['total']}")
        print("\nFile types:")
        for ext, count in analysis['files']['types'].items():
            print(f"  {ext or 'no extension'}: {count}")
        print("\nBusy hours:")
        for hour, count in sorted(analysis['commits']['busy_times'].items()):
            print(f"  {hour:02d}:00 - {count} commits")
        print(f"\nRelationships found: {analysis['relationships']['similar_commits']}")
        if analysis['relationships']['cross_repo']:
            print(f"Cross-repo relationships: {analysis['relationships']['cross_repo']}")
    
    elif args.build_relationships:
        if not args.context_name:
            parser.error("--context-name is required for building relationships")
        await builder.build_multi_repo_relationships(args.context_name)
    
    elif args.repo_path and args.context_name:
        await builder.build_context(args.repo_path, args.context_name, args.multi_repo)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 