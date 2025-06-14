import os
from pathlib import Path
import pytest

def pytest_runtest_setup(item):
    """Load environment variables from .env file only for E2E tests."""
    if "e2e" in item.nodeid:
        try:
            from dotenv import load_dotenv
            env_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))).joinpath('.env')
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"Loaded environment from {env_path}")
            
            # Print the first few characters of the API key for debugging
            api_key = os.environ.get("OPENWEATHER_API_KEY", "")
            if api_key:
                print(f"OPENWEATHER_API_KEY loaded: {api_key[:4]}{'*' * (len(api_key) - 4)}")
        except ImportError:
            print("WARNING: python-dotenv not installed, environment variables may not be loaded")
