#!/usr/bin/env python3

"""
Test basic imports to ensure all core modules are properly structured.
Tri says: Let's make sure our imports are as clean as our accounting books! 📚
"""

import traceback
import pytest
from typing import Dict, List, Optional

def test_imports():
    """Test basic imports to isolate any import issues"""
    
    # Test core types import
    try:
        print("\n🔍 Testing core types import...")
        from src.core.types import Context, ContextType, ValidationResult
        print("✅ Successfully imported types")
        
        # Verify we can create instances
        context_type = ContextType.TEST
        assert context_type.value == "TEST", "ContextType enum not working correctly"
        
    except ImportError as e:
        print(f"❌ Error importing types:")
        traceback.print_exc()
        pytest.fail(f"Failed to import types: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error with types:")
        traceback.print_exc()
        pytest.fail(f"Unexpected error with types: {str(e)}")

    # Test context store import
    try:
        print("\n🔍 Testing context_store import...")
        from src.core.context_store import ContextStore
        print("✅ Successfully imported context_store")
        
        # Verify we can create an instance
        store = ContextStore(host="localhost", port=6333)
        assert store.collection_name == "contexts", "ContextStore initialization failed"
        
    except ImportError as e:
        print(f"❌ Error importing context_store:")
        traceback.print_exc()
        pytest.fail(f"Failed to import context_store: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error with context_store:")
        traceback.print_exc()
        pytest.fail(f"Unexpected error with context_store: {str(e)}")

    # Test ToF system import
    try:
        print("\n🔍 Testing tof_system import...")
        from src.core.tof_system import ToFManager
        print("✅ Successfully imported tof_system")
        
        # Verify we can create an instance
        manager = ToFManager()
        assert hasattr(manager, 'contexts'), "ToFManager initialization failed"
        
    except ImportError as e:
        print(f"❌ Error importing tof_system:")
        traceback.print_exc()
        pytest.fail(f"Failed to import tof_system: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error with tof_system:")
        traceback.print_exc()
        pytest.fail(f"Unexpected error with tof_system: {str(e)}")

    print("\n✨ All imports tested successfully!")