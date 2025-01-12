import pytest
from ...src.core.model_explorer import ModelExplorer, AutoModelSelector
from ...src.core.unified_context import ContextType

@pytest.mark.asyncio
async def test_model_discovery():
    """Test model discovery and evaluation"""
    explorer = ModelExplorer()
    
    # Test discovery
    models = await explorer.discover_models(ContextType.TEST)
    assert len(models) > 0
    assert all(m.model_id for m in models)
    
    # Test evaluation
    metrics = await explorer.evaluate_model(models[0].model_id, ContextType.TEST)
    assert metrics.latency > 0
    assert metrics.memory_usage > 0

@pytest.mark.asyncio
async def test_auto_model_selection():
    """Test automatic model selection"""
    selector = AutoModelSelector()
    
    # Select model for test context
    model = await selector.select_optimal_model(ContextType.TEST)
    assert model.name.startswith("test-")
    assert model.model_path
    assert ContextType.TEST in model.best_for 