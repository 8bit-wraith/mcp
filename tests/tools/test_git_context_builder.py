#!/usr/bin/env python3
"""Tests for the Git Context Builder tool."""

import asyncio
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Generator

import git
import pytest
from git import Repo
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.tools.git_context_builder import GitContextBuilder

# Test fixtures
@pytest.fixture
def temp_repo() -> Generator[str, None, None]:
    """Create a temporary Git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)
    
    # Create some test files
    files = {
        "README.md": "# Test Repository\nThis is a test repository.",
        "main.py": "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
        "utils/helper.py": "def helper():\n    return 'I am helping!'"
    }
    
    # Add files and make commits
    for path, content in files.items():
        file_path = Path(temp_dir) / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        repo.index.add([str(file_path.relative_to(temp_dir))])
        repo.index.commit(f"Add {path}")
    
    # Make some changes and additional commits
    readme_path = Path(temp_dir) / "README.md"
    readme_path.write_text(readme_path.read_text() + "\nUpdated content.")
    repo.index.add([str(readme_path.relative_to(temp_dir))])
    repo.index.commit("Update README")
    
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_multi_repo() -> Generator[tuple[str, str], None, None]:
    """Create two temporary Git repositories for testing multi-repo features."""
    temp_dir1 = tempfile.mkdtemp()
    temp_dir2 = tempfile.mkdtemp()
    
    # Create first repo
    repo1 = Repo.init(temp_dir1)
    (Path(temp_dir1) / "README.md").write_text("# Repo 1\nThis is the first test repo.")
    repo1.index.add(["README.md"])
    repo1.index.commit("Initial commit for repo 1")
    
    # Create second repo with similar content
    repo2 = Repo.init(temp_dir2)
    (Path(temp_dir2) / "README.md").write_text("# Repo 2\nThis is the second test repo.")
    repo2.index.add(["README.md"])
    repo2.index.commit("Initial commit for repo 2")
    
    yield temp_dir1, temp_dir2
    shutil.rmtree(temp_dir1)
    shutil.rmtree(temp_dir2)

@pytest.fixture
async def context_builder() -> AsyncGenerator[GitContextBuilder, None]:
    """Create a GitContextBuilder instance for testing."""
    builder = GitContextBuilder()
    yield builder
    
    # Cleanup collections after tests
    collections = builder.client.get_collections().collections
    for collection in collections:
        builder.client.delete_collection(collection.name)

# Tests
@pytest.mark.asyncio
async def test_context_builder_initialization(context_builder: GitContextBuilder):
    """Test that the context builder initializes correctly."""
    collections = context_builder.client.get_collections().collections
    collection_names = {c.name for c in collections}
    
    assert "git_commits" in collection_names
    assert "git_files" in collection_names
    assert "git_authors" in collection_names
    assert "git_relationships" in collection_names

@pytest.mark.asyncio
async def test_build_context(context_builder: GitContextBuilder, temp_repo: str):
    """Test building context from a single repository."""
    await context_builder.build_context(temp_repo, "test-context")
    
    # Check commits were processed
    commits = context_builder.client.scroll(
        collection_name="git_commits",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="context_name",
                    match=models.MatchValue(value="test-context")
                )
            ]
        ),
        limit=100
    )[0]
    
    assert len(commits) > 0
    assert any("README.md" in commit.payload["message"] for commit in commits)
    
    # Check files were processed
    files = context_builder.client.scroll(
        collection_name="git_files",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="context_name",
                    match=models.MatchValue(value="test-context")
                )
            ]
        ),
        limit=100
    )[0]
    
    assert len(files) > 0
    assert any(file.payload["path"] == "README.md" for file in files)
    assert any(file.payload["path"] == "main.py" for file in files)
    assert any(file.payload["path"] == "utils/helper.py" for file in files)

@pytest.mark.asyncio
async def test_multi_repo_context(
    context_builder: GitContextBuilder,
    temp_multi_repo: tuple[str, str]
):
    """Test building context from multiple repositories."""
    repo1_path, repo2_path = temp_multi_repo
    
    # Build context for both repos
    await context_builder.build_context(repo1_path, "multi-test", multi_repo=True)
    await context_builder.build_context(repo2_path, "multi-test", multi_repo=True)
    
    # Build relationships
    await context_builder.build_multi_repo_relationships("multi-test")
    
    # Check relationships were created
    relationships = context_builder.client.scroll(
        collection_name="git_relationships",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="context_name",
                    match=models.MatchValue(value="multi-test")
                ),
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(value="cross_repo_similarity")
                )
            ]
        ),
        limit=100
    )[0]
    
    assert len(relationships) > 0

@pytest.mark.asyncio
async def test_list_contexts(context_builder: GitContextBuilder, temp_repo: str):
    """Test listing available contexts."""
    # Build a test context
    await context_builder.build_context(temp_repo, "list-test")
    
    # List contexts
    contexts = await context_builder.list_contexts()
    assert "list-test" in contexts

@pytest.mark.asyncio
async def test_analyze_context(context_builder: GitContextBuilder, temp_repo: str):
    """Test analyzing a context."""
    # Build a test context
    await context_builder.build_context(temp_repo, "analyze-test")
    
    # Analyze context
    analysis = await context_builder.analyze_context("analyze-test")
    
    assert analysis["commits"]["total"] > 0
    assert len(analysis["commits"]["authors"]) > 0
    assert analysis["files"]["total"] > 0
    assert ".md" in analysis["files"]["types"]
    assert ".py" in analysis["files"]["types"]
    assert analysis["files"]["largest"] is not None

@pytest.mark.asyncio
async def test_author_processing(context_builder: GitContextBuilder, temp_repo: str):
    """Test processing of author information."""
    # Build context
    await context_builder.build_context(temp_repo, "author-test")
    
    # Check author information
    authors = context_builder.client.scroll(
        collection_name="git_authors",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="context_name",
                    match=models.MatchValue(value="author-test")
                )
            ]
        ),
        limit=100
    )[0]
    
    assert len(authors) > 0
    author = authors[0]
    assert "name" in author.payload
    assert "email" in author.payload
    assert "commit_count" in author.payload
    assert author.payload["commit_count"] > 0
    assert "file_patterns" in author.payload
    assert len(author.payload["file_patterns"]) > 0

@pytest.mark.asyncio
async def test_relationship_building(
    context_builder: GitContextBuilder,
    temp_repo: str
):
    """Test building relationships between commits."""
    # Build context
    await context_builder.build_context(temp_repo, "relationship-test")
    
    # Check relationships
    relationships = context_builder.client.scroll(
        collection_name="git_relationships",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="context_name",
                    match=models.MatchValue(value="relationship-test")
                )
            ]
        ),
        limit=100
    )[0]
    
    assert len(relationships) > 0
    relationship = relationships[0]
    assert "type" in relationship.payload
    assert "source_id" in relationship.payload
    assert "target_id" in relationship.payload
    assert "similarity" in relationship.payload
    assert relationship.payload["similarity"] > 0.0 