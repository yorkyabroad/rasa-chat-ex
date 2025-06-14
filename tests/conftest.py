import sys
import os
import pytest

# Add the parent directory to the path so we can import the actions module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_configure(config):
    """Configure pytest - check if rasa is installed."""
    try:
        import importlib.util
        print(f"Using Python: {sys.executable}")
        
        rasa_spec = importlib.util.find_spec('rasa')
        if rasa_spec is None:
            print("WARNING: Rasa package is not installed. E2E tests will be skipped.")
    except ImportError:
        print("WARNING: Error checking for Rasa package. E2E tests may fail.")
