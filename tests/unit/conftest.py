import os
import pytest

def pytest_runtest_setup(item):
    """Set mock environment variables only for unit tests."""
    if "unit" in item.nodeid:
        os.environ["OPENWEATHER_API_KEY"] = "test_api_key"
        os.environ["TIMEZONE_API_KEY"] = "test_timezone_key"
