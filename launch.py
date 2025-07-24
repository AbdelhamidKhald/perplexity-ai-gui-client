#!/usr/bin/env python3
"""
Perplexity AI GUI Client Launcher
Enhanced Edition v2.0

This launcher script checks dependencies and provides helpful error messages.
"""

import sys
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print("❌ Error: Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 To install missing dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if API key is available."""
    api_key_file = "pplx_api_key.txt"
    env_key = os.getenv('PERPLEXITY_API_KEY')
    
    if os.path.exists(api_key_file):
        print("✅ API key file found")
        return True
    elif env_key:
        print("✅ API key found in environment variable")
        return True
    else:
        print("⚠️  No API key found")
        print("   You'll need to set your Perplexity AI API key in the application")
        return True  # Not a blocking error

def main():
    """Main launcher function."""
    print("🚀 Perplexity AI GUI Client - Enhanced Edition v2.0")
    print("=" * 55)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key (non-blocking)
    check_api_key()
    
    print("\n🎯 Starting application...")
    print("   Close this window to stop the application")
    print("=" * 55)
    
    # Import and run the main application
    try:
        from App1 import PerplexityGUI
        import tkinter as tk
        
        app = PerplexityGUI()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("   Please check the error message above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()