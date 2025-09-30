#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module and report results"""
    try:
        if module_name == "app.main":
            from app.main import create_app
            app = create_app()
            print(f"✅ {description}: SUCCESS - App created")
        elif module_name == "app.core.config":
            from app.core.config import settings
            print(f"✅ {description}: SUCCESS - {settings.APP_NAME}")
        elif module_name == "app.core.dependencies":
            from app.core.dependencies import get_dependency_status
            deps = get_dependency_status()
            print(f"✅ {description}: SUCCESS - {deps}")
        elif module_name == "app.models":
            from app.models import HealthResponse, EmbedRequest
            print(f"✅ {description}: SUCCESS - Models imported")
        elif module_name == "app.services":
            from app.services import get_model_service, get_batch_service
            print(f"✅ {description}: SUCCESS - Services imported")
        elif module_name == "app.routes":
            from app.routes import get_health_router, get_ml_router
            health_router = get_health_router()
            print(f"✅ {description}: SUCCESS - Routers imported")
        else:
            exec(f"import {module_name}")
            print(f"✅ {description}: SUCCESS")
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        traceback.print_exc()
        return False
    return True

def main():
    print("=== Testing Modular App Imports ===\n")
    
    # Test basic dependencies
    test_import("fastapi", "FastAPI")
    test_import("uvicorn", "Uvicorn")
    test_import("pydantic", "Pydantic")
    
    print("\n=== Testing App Modules ===")
    
    # Test app modules in dependency order
    test_import("app.core.config", "Core Config")
    test_import("app.core.dependencies", "Core Dependencies")
    test_import("app.models", "Models")
    test_import("app.services", "Services")
    test_import("app.routes", "Routes")
    test_import("app.main", "Main App")
    
    print("\n=== Import Test Complete ===")

if __name__ == "__main__":
    main()
