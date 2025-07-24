#!/usr/bin/env python3
"""
Simple run script for Perplexity AI GUI Client
Just run: python run.py
"""

import sys
import subprocess

def main():
    """Launch the application using the launcher."""
    print("🚀 Starting Perplexity AI GUI Client...")
    try:
        subprocess.run([sys.executable, "launch.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    main()