from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import aiohttp
import asyncio
from huggingface_hub import HfApi, ModelFilter
from sentence_transformers import SentenceTransformer
import torch
from .unified_context import ContextType, EmbeddingModel

class ModelMetrics(BaseModel):
    """Metrics for evaluating model performance"""
    accuracy: float
    latency: float  # milliseconds
    memory_usage: float  # MB
    sample_score: Optional[float] = None

class ModelCandidate(BaseModel):
    """Represents a potential model from HuggingFace"""
    model_id: str
    description: str
    downloads: int
    likes: int
    tags: List[str]
    pipeline_tag: str
    metrics: Optional[ModelMetrics] = None

class ModelExplorer:
    """Explores and evaluates HuggingFace models for different context types"""
    
    def __init__(self):
        self.hf_api = HfApi()
        self.evaluation_cache: Dict[str, ModelMetrics] = {}
        
    async def discover_models(self, context_type: ContextType) -> List[ModelCandidate]:
        """Discover potential models for a context type"""
        # Map context types to relevant model tags
        type_tags = {
            ContextType.TEST: ["sentence-similarity", "text-embedding"],
            ContextType.FEELING: ["sentiment", "emotion", "text-embedding"],
            ContextType.PARTICIPANT: ["sentence-similarity", "text-embedding"],
            ContextType.CONVERSATION: ["sentence-similarity", "conversational"],
            ContextType.SYSTEM: ["text-embedding", "zero-shot-classification"],
            ContextType.TOOL: ["text-embedding", "zero-shot-classification"]
        }
        
        # Get relevant tags for this context type
        relevant_tags = type_tags.get(context_type, ["text-embedding"])
        
        # Search for models
        models = self.hf_api.list_models(
            filter=ModelFilter(
                task="feature-extraction",
                tags=relevant_tags,
                library="sentence-transformers"
            )
        )
        
        # Convert to candidates
        candidates = []
        for model in models:
            candidates.append(ModelCandidate(
                model_id=model.modelId,
                description=model.description or "",
                downloads=model.downloads or 0,
                likes=model.likes or 0,
                tags=model.tags or [],
                pipeline_tag=model.pipeline_tag or "unknown"
            ))
        
        # Sort by popularity (downloads + likes)
        candidates.sort(key=lambda x: x.downloads + x.likes, reverse=True)
        return candidates[:10]  # Return top 10
    
    async def evaluate_model(self, model_id: str, context_type: ContextType) -> ModelMetrics:
        """Evaluate a model's performance for a specific context type"""
        if model_id in self.evaluation_cache:
            return self.evaluation_cache[model_id]
        
        # Create sample data based on context type
        sample_data = self._generate_sample_data(context_type)
        
        try:
            # Load model
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            
            start_time.record()
            model = SentenceTransformer(model_id)
            end_time.record()
            
            torch.cuda.synchronize()
            load_time = start_time.elapsed_time(end_time)
            
            # Measure memory
            memory_usage = torch.cuda.max_memory_allocated() / 1024 / 1024  # Convert to MB
            
            # Test embedding creation
            start_time.record()
            embeddings = model.encode(sample_data["texts"])
            end_time.record()
            
            torch.cuda.synchronize()
            encoding_time = start_time.elapsed_time(end_time)
            
            # Calculate similarity score if applicable
            sample_score = None
            if "similar_pairs" in sample_data:
                similarities = torch.nn.functional.cosine_similarity(
                    torch.tensor(embeddings[0]).unsqueeze(0),
                    torch.tensor(embeddings[1]).unsqueeze(0)
                )
                sample_score = similarities.mean().item()
            
            metrics = ModelMetrics(
                accuracy=sample_score or 0.0,
                latency=(load_time + encoding_time) / 2,
                memory_usage=memory_usage,
                sample_score=sample_score
            )
            
            self.evaluation_cache[model_id] = metrics
            return metrics
            
        except Exception as e:
            print(f"Error evaluating model {model_id}: {str(e)}")
            return ModelMetrics(accuracy=0.0, latency=float('inf'), memory_usage=float('inf'))
    
    def _generate_sample_data(self, context_type: ContextType) -> Dict[str, Any]:
        """Generate sample data for model evaluation"""
        samples = {
            ContextType.TEST: {
                "texts": [
                    "Test failed due to null pointer exception in user authentication",
                    "Authentication test failed because user object was null",
                    "Database connection timeout during backup operation"
                ],
                "similar_pairs": [(0, 1)]  # Indices of similar pairs
            },
            ContextType.FEELING: {
                "texts": [
                    "I'm really excited about this new feature!",
                    "This bug is frustrating me a lot",
                    "The system is running smoothly, feeling confident"
                ]
            },
            ContextType.PARTICIPANT: {
                "texts": [
                    "User prefers visual explanations and quick responses",
                    "AI assistant provides detailed technical answers",
                    "User needs step-by-step guidance"
                ]
            }
        }
        return samples.get(context_type, {"texts": ["Default test text"]})

class AutoModelSelector:
    """Automatically selects and configures optimal models for context types"""
    
    def __init__(self):
        self.explorer = ModelExplorer()
        self.selected_models: Dict[ContextType, EmbeddingModel] = {}
    
    async def select_optimal_model(self, context_type: ContextType) -> EmbeddingModel:
        """Select the optimal model for a context type"""
        # Discover potential models
        candidates = await self.explorer.discover_models(context_type)
        
        # Evaluate top candidates
        best_model = None
        best_metrics = None
        best_score = float('-inf')
        
        for candidate in candidates[:3]:  # Evaluate top 3
            metrics = await self.explorer.evaluate_model(candidate.model_id, context_type)
            
            # Calculate overall score (lower is better for latency and memory)
            score = (
                (metrics.accuracy * 2.0) +
                (1.0 / (metrics.latency + 1)) +
                (1.0 / (metrics.memory_usage + 1)) +
                (metrics.sample_score or 0.0)
            )
            
            if score > best_score:
                best_score = score
                best_metrics = metrics
                best_model = candidate
        
        if best_model:
            model = EmbeddingModel(
                name=f"{context_type.value}-{best_model.model_id}",
                type="embedding",
                description=best_model.description,
                dimensions=768,  # We'll need to detect this dynamically
                best_for=[context_type],
                version="1.0.0",
                model_path=best_model.model_id
            )
            self.selected_models[context_type] = model
            return model
        
        raise ValueError(f"Could not find suitable model for {context_type}") 