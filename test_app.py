#!/usr/bin/env python3
"""
Test script for Perplexity AI GUI Client
Enhanced Edition v2.0

This script tests the core components without launching the full GUI.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import tkinter
        print("  ✅ tkinter imported successfully")
    except ImportError as e:
        print(f"  ❌ tkinter import failed: {e}")
        return False
    
    try:
        import requests
        print("  ✅ requests imported successfully")
    except ImportError as e:
        print(f"  ❌ requests import failed: {e}")
        return False
    
    try:
        from App1 import PerplexityAPI, PerplexityGUI, AVAILABLE_MODELS, CONVERSATION_TEMPLATES
        print("  ✅ App1 components imported successfully")
    except ImportError as e:
        print(f"  ❌ App1 import failed: {e}")
        return False
    
    try:
        import config
        print("  ✅ config module imported successfully")
    except ImportError as e:
        print(f"  ❌ config import failed: {e}")
        return False
    
    return True

def test_api_class():
    """Test the PerplexityAPI class initialization."""
    print("\n🧪 Testing PerplexityAPI class...")
    
    try:
        from App1 import PerplexityAPI
        
        # Test with dummy API key
        api = PerplexityAPI("test-key-123")
        print("  ✅ PerplexityAPI class initialized successfully")
        
        # Test error handling for empty key
        try:
            api_empty = PerplexityAPI("")
            print("  ❌ Empty API key should raise ValueError")
            return False
        except ValueError:
            print("  ✅ Empty API key properly raises ValueError")
        
        return True
    except Exception as e:
        print(f"  ❌ PerplexityAPI test failed: {e}")
        return False

def test_configuration():
    """Test configuration values."""
    print("\n🧪 Testing configuration...")
    
    try:
        from App1 import AVAILABLE_MODELS, CONVERSATION_TEMPLATES
        import config
        
        print(f"  ✅ Found {len(AVAILABLE_MODELS)} available models")
        print(f"  ✅ Found {len(CONVERSATION_TEMPLATES)} conversation templates")
        print(f"  ✅ Found {len(config.CONVERSATION_TEMPLATES)} config templates")
        
        # Test that default model exists
        if config.DEFAULT_MODEL in AVAILABLE_MODELS:
            print(f"  ✅ Default model '{config.DEFAULT_MODEL}' is available")
        else:
            print(f"  ⚠️  Default model '{config.DEFAULT_MODEL}' not in available models")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing it."""
    print("\n🧪 Testing GUI creation...")
    
    try:
        import tkinter as tk
        from App1 import PerplexityGUI
        
        # Create a root window (but don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test GUI initialization
        app = PerplexityGUI()
        app.withdraw()  # Hide the app window too
        
        print("  ✅ GUI created successfully")
        
        # Clean up
        app.destroy()
        root.destroy()
        
        return True
    except Exception as e:
        print(f"  ❌ GUI creation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Perplexity AI GUI Client - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("API Class Test", test_api_class),
        ("Configuration Test", test_configuration),
        ("GUI Creation Test", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())