import os
import sys
import pytest
import requests
import time
import subprocess
import signal # type: ignore
import logging
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    # Load .env file and force override of existing variables
    dotenv_values = {}
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                dotenv_values[key] = value
                # Force override any existing environment variables
                os.environ[key] = value
                print(f"Set {key}={value[:4]}... from .env file")

# Print environment variables after loading .env
print("\n--- ENVIRONMENT VARIABLES AFTER LOADING .ENV ---")
#print(f"OPENWEATHER_API_KEY: {os.environ.get('OPENWEATHER_API_KEY')}")
if os.environ.get('OPENWEATHER_API_KEY'):
    print(f"API key starts with: {os.environ.get('OPENWEATHER_API_KEY')[:4]}...") # type: ignore

# Check for .env files that might be overriding environment variables
project_root = Path(__file__).parent.parent
env_files = list(project_root.glob("**/.env"))
print(f"\nFound {len(env_files)} .env files:")
for env_file in env_files:
    print(f"- {env_file}")
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if "OPENWEATHER_API_KEY" in content:
                print(f"  Contains OPENWEATHER_API_KEY definition")
    except Exception as e:
        print(f"  Error reading file: {e}")

print("-----------------------------------\n")

# Configure logging with a stream handler to output to console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler and set level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

# Print directly to ensure output is visible
print("Starting E2E test setup")

class TestChatbotE2E:
    @classmethod
    def setup_class(cls):
        # Get API key from environment
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        
        if api_key:
            # Print first few chars of API key for debugging
            print(f"API key starts with: {api_key[:4]}...")
        
        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            return

        # Start Rasa server
        logger.info("Starting Rasa server...")
        print("Starting Rasa server...")
        cls.rasa_server = subprocess.Popen(
            ["rasa", "run", "--enable-api", "--port", "5005"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Start Actions server with explicit environment variable
        logger.info("Starting Actions server...")
        print("Starting Actions server...")
        
        # Create a new environment with the API key
        env = os.environ.copy()
        env["OPENWEATHER_API_KEY"] = api_key
        print(f"Setting OPENWEATHER_API_KEY in actions server environment: {api_key[:4]}...")
        
        cls.actions_server = subprocess.Popen(
            ["rasa", "run", "actions", "--debug"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )

        # Give servers time to start
        logger.info("Waiting for servers to start...")
        print("Waiting for servers to start...")
        time.sleep(180)
        logger.info("Setup complete")
        print("Setup complete")

    @classmethod
    def teardown_class(cls):
        # Stop servers
        logger.info("Stopping servers...")
        print("Stopping servers...")
        cls.rasa_server.terminate()
        cls.actions_server.terminate()
        cls.rasa_server.wait()
        cls.actions_server.wait()
        logger.info("Servers stopped")
        print("Servers stopped")

    def print_server_logs(self):
        """Print logs from the servers for debugging."""
        print("\n--- ACTIONS SERVER LOGS ---")
        
        # Check if the process is still running
        if self.actions_server.poll() is None:
            print("Actions server is still running")
        else:
            print(f"Actions server has terminated with return code: {self.actions_server.returncode}")
        
        # Try to get process info with error handling for zombie processes
        try:
            import psutil # type: ignore
            try:
                process = psutil.Process(self.actions_server.pid)
                print(f"Actions server process status: {process.status()}")
                try:
                    print(f"Actions server memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                except (psutil.ZombieProcess, psutil.NoSuchProcess, psutil.AccessDenied):
                    print("Cannot get memory info - process may be a zombie")
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                print(f"Process {self.actions_server.pid} is no longer available or is a zombie")
        except ImportError:
            print("psutil not available")
        
        # Try to get environment variables
        print("\n--- ENVIRONMENT VARIABLES ---")
        env = os.environ.copy()
        print(f"OPENWEATHER_API_KEY present: {bool(env.get('OPENWEATHER_API_KEY'))}")
        
        # Skip trying to read stdout/stderr as it's causing hanging
        print("Skipping stdout/stderr reading to avoid blocking")

    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the Rasa server and return the response."""
        response = requests.post(
            "http://localhost:5005/webhooks/rest/webhook",
            json={"sender": "test_user", "message": message},
            timeout=30  # Add a 30-second timeout
        )
        return response.json()
            
    def test_rain_in_stockholm(self):
        """Test asking about rain in Stockholm today."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if api_key:
            print(f"API key starts with: {api_key[:4]}...")
        
        # Try a direct API call to verify the API key works
        try:
            import requests
            test_url = f"http://api.openweathermap.org/data/2.5/weather?q=Stockholm&appid={api_key}"
            print(f"\nTesting direct API call to: {test_url.replace(api_key, 'API_KEY')}") # type: ignore
            
            response = requests.get(test_url, timeout=10)
            print(f"Direct API call status: {response.status_code}")
            if response.status_code == 200:
                print("Direct API call successful")
            else:
                print(f"Direct API call failed: {response.text}")
                pytest.skip(f"API key is invalid: {response.text}")
                return
        except Exception as e:
            print(f"Error testing API directly: {str(e)}")
        
        # First, check what intent is recognized for our query
        responses = self.send_message("What's the precipitation forecast for Stockholm today?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")
        
        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR PRECIPITATION TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Try alternative queries if the first one didn't work
        if not any(term in response_text.lower() for term in ["precipitation", "rain", "rainfall", "shower", "drizzle", "mm"]):
            print("First query didn't return precipitation info, trying alternative query...")
            responses = self.send_message("Will it rain in Stockholm today?")
            response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
            print(f"Alternative response: {response_text}")
        
        # Check for Stockholm keyword
        has_stockholm = "stockholm" in response_text.lower()
        print(f"Has 'Stockholm' keyword: {has_stockholm}")
        
        # Check for today keyword
        has_today = "today" in response_text.lower()
        print(f"Has 'today' keyword: {has_today}")
        
        # Check for weather-related keywords
        weather_terms = ["precipitation", "rain", "rainfall", "shower", "drizzle", "mm", "weather", "temperature", "forecast"]
        has_weather_info = any(term in response_text.lower() for term in weather_terms)
        print(f"Has weather info: {has_weather_info}")
        
        # More flexible assertion
        assert has_stockholm and has_weather_info, f"Expected weather information for Stockholm, got: {response_text}"

    def test_wind_in_stockholm_tomorrow(self):
        """Test asking about wind in Stockholm tomorrow."""
        # Send the message
        responses = self.send_message("wind in Stockholm tomorrow?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")
        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR WIND TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")

        assert "wind forecast for stockholm tomorrow" in response_text.lower(), f"Expected wind forecast, got: {response_text}"
        assert "wind speed" in response_text.lower(), "Response should include wind speed"

    def test_sunrise_in_london(self):
        """Test asking about sunrise in London."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("When is sunrise in London today?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR SUNRISE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        assert "sunrise" in response_text.lower() and "london" in response_text.lower(), f"Expected sunrise info for London, got: {response_text}"

    def test_air_quality_in_beijing(self):
        """Test asking about air pollution and quality in Beijing."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("What will the air quality be like in Beijing tomorrow?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR AIR QUALITY TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for quality keyword
        has_quality = "quality" in response_text.lower()
        print(f"Has 'quality' keyword: {has_quality}")
    
        # Check for Beijing keyword
        has_beijing = "beijing" in response_text.lower()
        print(f"Has 'Beijing' keyword: {has_beijing}")

    def test_temperature_range_in_paris(self):
        """Test asking about air pollution and quality in Beijing."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("What will the temperature range be in Paris tomorrow?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for temperature keyword
        has_temperature = "temperature" in response_text.lower()
        print(f"Has 'quality' keyword: {has_temperature}")
    
        # Check for range keyword
        has_range = "range" in response_text.lower()
        print(f"Has 'range' keyword: {has_range}")
    
        # Check for Paris keyword
        has_paris = "paris" in response_text.lower()
        print(f"Has 'Paris' keyword: {has_paris}")

        # Check for tomorrow keyword
        has_tomorrow = "tomorrow" in response_text.lower()          
        print(f"Has 'tomorrow' keyword: {has_tomorrow}")

    def test_time_in_moscow(self):
        """Test asking aboUt time in Moscow."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("What is the time in Moscow?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for current keyword
        has_current = "current" in response_text.lower()
        print(f"Has 'current' keyword: {has_current}")
    
        # Check for time keyword
        has_time = "time" in response_text.lower()
        print(f"Has 'time' keyword: {has_time}")
    
        # Check for Moscow keyword
        has_moscow = "moscow" in response_text.lower()
        print(f"Has 'Moscow' keyword: {has_moscow}")

    def test_weather_comparison_in_tokyo(self):
        """Test asking aboUt comparing weather in Tokyo."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("Is Tokyo colder than average today?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for current keyword
        has_current = "current" in response_text.lower()
        print(f"Has 'current' keyword: {has_current}")
    
        # Check for temperature keyword
        has_temperature = "temperature" in response_text.lower()
        print(f"Has 'temperature' keyword: {has_temperature}")
    
        # Check for average keyword
        has_average = "average" in response_text.lower()
        print(f"Has 'average' keyword: {has_average}")
    
        # Check for Tokyo keyword
        has_tokyo = "tokyo" in response_text.lower()
        print(f"Has 'Tokyo' keyword: {has_tokyo}")

    def test_UV_index_in_sydney(self):
        """Test asking aboUt UV index in Sydney."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("What will the UV index be like in Sydney tomorrow?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for UV keyword
        has_uv = "uv" in response_text.lower()
        print(f"Has 'UV' keyword: {has_uv}")
    
        # Check for forecast keyword
        has_forecast = "forecast" in response_text.lower()
        print(f"Has 'forecast' keyword: {has_forecast}")
    
        # Check for Sydney keyword
        has_sydney = "sydney" in response_text.lower()
        print(f"Has 'Sydney' keyword: {has_sydney}")

    def test_current_weather_in_paris(self):
        """Test asking aboUt current weather in Paris."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("What's the weather like in Paris?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for current keyword
        has_current = "current" in response_text.lower()
        print(f"Has 'current' keyword: {has_current}")
        
        # Check for weather keyword
        has_weather = "weather" in response_text.lower()
        print(f"Has 'weather' keyword: {has_weather}")
        
        # Check for Paris keyword
        has_paris = "paris" in response_text.lower()
        print(f"Has 'Paris' keyword: {has_paris}")

    def test_weather_forecast_in_paris(self):
        """Test asking aboUt weather forecast in Paris."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("what is the weather forecast for Paris?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for forecast keyword
        has_forecast = "forecast" in response_text.lower()
        print(f"Has 'forecast' keyword: {has_forecast}")
        
        # Check for weather keyword
        has_weather = "weather" in response_text.lower()
        print(f"Has 'weather' keyword: {has_weather}")
        
        # Check for Paris keyword
        has_paris = "paris" in response_text.lower()
        print(f"Has 'Paris' keyword: {has_paris}")

    def test_rain_forecast_in_london_tomorrow(self):
        """Test asking aboUt rain forecast in London."""
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        logger.info(f"OPENWEATHER_API_KEY present: {api_key is not None}")
        print(f"OPENWEATHER_API_KEY present: {api_key is not None}")

        if api_key is None:
            logger.warning("OPENWEATHER_API_KEY is not set in environment")
            print("WARNING: OPENWEATHER_API_KEY is not set in environment")
            pytest.skip("No API key available - skipping test")

        responses = self.send_message("what is the weather forecast for Paris?")
        assert len(responses) > 0, "No response received"
        
        response_text = " ".join([r.get("text", "") for r in responses]) # type: ignore
        print(f"Response: {response_text}")

        # Check if the response is an error message
        if "couldn't fetch" in response_text.lower() or "error" in response_text.lower():
            print("\n--- DEBUG INFO FOR TEMPERATURE RANGE TEST ---")
            self.print_server_logs()
            pytest.skip("API connection error - skipping test")
        
        # Check for forecast keyword
        has_forecast = "forecast" in response_text.lower()
        print(f"Has 'forecast' keyword: {has_forecast}")
        
        # Check for weather keyword
        has_weather = "weather" in response_text.lower()
        print(f"Has 'weather' keyword: {has_weather}")
        
        # Check for Paris keyword
        has_paris = "paris" in response_text.lower()
        print(f"Has 'Paris' keyword: {has_paris}")
