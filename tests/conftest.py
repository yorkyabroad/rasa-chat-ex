import sys
import os
import pytest

# Add the parent directory to the path so we can import the actions module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set mock environment variables for testing
os.environ["OPENWEATHER_API_KEY"] = "test_api_key"
os.environ["TIMEZONE_API_KEY"] = "test_timezone_key"

def pytest_configure(config):
    """Configure pytest - check if rasa is installed."""
    try:
        import importlib.util
        rasa_spec = importlib.util.find_spec('rasa')
        if rasa_spec is None:
            print("WARNING: Rasa package is not installed. E2E tests will be skipped.")
    except ImportError:
        print("WARNING: Error checking for Rasa package. E2E tests may fail.")
        
def pytest_collection_modifyitems(config, items):
    """Skip E2E tests if rasa is not installed."""
    try:
        import importlib.util
        rasa_spec = importlib.util.find_spec('rasa')
        if rasa_spec is None:
            skip_e2e = pytest.mark.skip(reason="Rasa package is not installed")
            for item in items:
                if "test_e2e" in item.nodeid:
                    item.add_marker(skip_e2e)
    except ImportError:
        pass