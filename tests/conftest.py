import sys
import os

# Add the parent directory to the path so we can import the actions module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set mock environment variables for testing
os.environ["OPENWEATHER_API_KEY"] = "test_api_key"
os.environ["TIMEZONE_API_KEY"] = "test_timezone_key"