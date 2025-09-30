#!/usr/bin/env python3
"""
Simple Model Test - Diagnose Core Issues
========================================

This script tests the model directly to identify the root cause of the "Broken pipe" error.
"""

import requests
import json
import time

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Model Loaded: {data.get('model_loaded')}")
            print(f"Model Path: {data.get('model_path')}")
            print(f"Model Dimension: {data.get('model_dimension')}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_embed():
    """Test the embed endpoint with simple text"""
    print("\n🔍 Testing Embed Endpoint...")
    try:
        data = {
            "texts": ["Hello world", "Simple test"],
            "normalize": True
        }
        response = requests.post("http://localhost:8000/embed", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Embeddings shape: {len(result.get('embeddings', []))} x {len(result.get('embeddings', [[]])[0]) if result.get('embeddings') else 0}")
            return True
        else:
            print(f"Embed failed: {response.text}")
            return False
    except Exception as e:
        print(f"Embed error: {e}")
        return False

def test_similarity_simple():
    """Test similarity with very simple text"""
    print("\n🔍 Testing Simple Similarity...")
    try:
        data = {
            "text1": "hello",
            "text2": "hi"
        }
        response = requests.post("http://localhost:8000/similarity", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Similarity: {result.get('similarity')}")
            return True
        else:
            print(f"Similarity failed: {response.text}")
            return False
    except Exception as e:
        print(f"Similarity error: {e}")
        return False

def test_generate_minimal():
    """Test generate with minimal input"""
    print("\n🔍 Testing Minimal Generate...")
    try:
        data = {
            "human_example": "contract",
            "target_length": 100,
            "style_preference": "professional",
            "document_type": "legal_template"
        }
        response = requests.post("http://localhost:8000/generate", json=data, timeout=60)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Generated length: {len(result.get('generated_text', ''))}")
            print(f"Similarity: {result.get('similarity_to_example')}")
            return True
        else:
            print(f"Generate failed: {response.text}")
            return False
    except Exception as e:
        print(f"Generate error: {e}")
        return False

def main():
    print("🧪 SIMPLE MODEL DIAGNOSTIC TEST")
    print("=" * 40)
    
    # Test each endpoint progressively
    tests = [
        ("Health Check", test_health),
        ("Embed Endpoint", test_embed),
        ("Simple Similarity", test_similarity_simple),
        ("Minimal Generate", test_generate_minimal)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        result = test_func()
        results.append((test_name, result))
        
        if not result:
            print(f"❌ {test_name} failed - stopping here")
            break
        else:
            print(f"✅ {test_name} passed")
    
    print(f"\n{'='*40}")
    print("📊 SUMMARY")
    print("=" * 40)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
