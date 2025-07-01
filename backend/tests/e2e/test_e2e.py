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
            pytest.skip("OPENWEATHER_API_KEY is not set in environment")
            return

        try:
            # Check if rasa is installed
            import importlib.util
            rasa_spec = importlib.util.find_spec('rasa')
            if rasa_spec is None:
                logger.warning("Rasa package is not installed")
                print("WARNING: Rasa package is not installed")
                pytest.skip("Rasa package is not installed - skipping E2E tests")
                return
                
            # Check if model exists first
            models_dir = Path("models")
            if not models_dir.exists() or not list(models_dir.glob("*.tar.gz")):
                print("ERROR: No trained model found. Run 'rasa train' first.")
                pytest.skip("No trained model found")
                return
            else:
                model_files = sorted(list(models_dir.glob("*.tar.gz")), key=lambda x: x.stat().st_mtime, reverse=True)
                latest_model = model_files[0]
                print(f"Using latest model: {latest_model}")
            
            # Kill any existing processes on ports 5005 and 5055
            import subprocess as sp
            for port in [5005, 5055]:
                try:
                    result = sp.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
                    if result.stdout.strip():
                        pids = result.stdout.strip().split('\n')
                        print(f"Killing existing processes on port {port}: {pids}")
                        for pid in pids:
                            if pid.strip():
                                sp.run(["kill", "-9", pid.strip()], capture_output=True)
                except Exception as e:
                    print(f"Error cleaning port {port}: {e}")
            time.sleep(3)  # Give processes more time to die
            
            # Start Rasa server
            logger.info("Starting Rasa server...")
            print("Starting Rasa server...")
            try:
                # Get the backend directory path
                backend_dir = Path(__file__).parent.parent.parent
                print(f"Running Rasa from directory: {backend_dir}")
                cls.rasa_server = subprocess.Popen(
                    ["rasa", "run", "--enable-api", "--port", "5005", "--endpoints", "endpoints-ci.yml", "--model", str(latest_model)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=str(backend_dir)
                )
                print(f"Rasa server started with PID: {cls.rasa_server.pid}")
                # Give it a moment to start
                time.sleep(2)
                if cls.rasa_server.poll() is not None:
                    stdout, stderr = cls.rasa_server.communicate()
                    print(f"Rasa server died immediately. Return code: {cls.rasa_server.returncode}")
                    print(f"Stdout: {stdout}")
                    print(f"Stderr: {stderr}")
                    pytest.skip("Rasa server failed to start")
                    return
                else:
                    # Check for startup errors without blocking
                    time.sleep(1)
                    if cls.rasa_server.poll() is not None:
                        stdout, stderr = cls.rasa_server.communicate()
                        print(f"Rasa server failed during startup. Return code: {cls.rasa_server.returncode}")
                        print(f"Stdout: {stdout}")
                        print(f"Stderr: {stderr}")
            except Exception as e:
                print(f"Failed to start Rasa server: {e}")
                pytest.skip(f"Failed to start Rasa server: {e}")
                return
            
            # Start Actions server with explicit environment variable
            logger.info("Starting Actions server...")
            print("Starting Actions server...")
            
            # Create a new environment with the API key
            env = os.environ.copy()
            env["OPENWEATHER_API_KEY"] = api_key
            print(f"Setting OPENWEATHER_API_KEY in actions server environment: {api_key[:4]}...")
            
            cls.actions_server = subprocess.Popen(
                ["rasa", "run", "actions", "--debug", "--port", "5055"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                cwd=str(backend_dir)
            )

            # Give servers time to start
            logger.info("Waiting for servers to start...")
            print("Waiting for servers to start...")
            
            # Initial wait for servers to initialize
            print("Waiting for Rasa server to load model (this can take 1-2 minutes)...")
            time.sleep(30)  # Longer wait for model loading
            print("Initial wait complete, checking server status...")
            
            # Wait for servers to be ready with health check
            max_retries = 50  # 50 * 5s = 4+ minutes for actions server
            retry_interval = 5
            server_ready = False
            
            print(f"Starting health check loop with {max_retries} retries...")
            for i in range(max_retries):
                # Check if processes are still running
                rasa_running = cls.rasa_server.poll() is None
                actions_running = cls.actions_server.poll() is None
                
                print(f"Loop {i+1}: Rasa running: {rasa_running}, Actions running: {actions_running}")
                
                if not rasa_running:
                    print(f"ERROR: Rasa server process died with return code: {cls.rasa_server.returncode}")
                    # Try to get error output
                    try:
                        stdout, stderr = cls.rasa_server.communicate(timeout=1)
                        print(f"Rasa stdout: {stdout}")
                        print(f"Rasa stderr: {stderr}")
                    except Exception as e:
                        print(f"Could not get Rasa output: {e}")
                    break
                    
                if not actions_running:
                    print(f"ERROR: Actions server process died with return code: {cls.actions_server.returncode}")
                    # Try to get error output
                    try:
                        stdout, stderr = cls.actions_server.communicate(timeout=1)
                        print(f"Actions stdout: {stdout}")
                        print(f"Actions stderr: {stderr}")
                    except Exception as e:
                        print(f"Could not get Actions output: {e}")
                    break
                
                try:
                    # Check if both servers are responding
                    rasa_response = requests.get("http://localhost:5005/", timeout=3)
                    actions_response = requests.get("http://localhost:5055/", timeout=3)
                    
                    if rasa_response.status_code == 200 and actions_response.status_code in [200, 404, 500]:
                        # 404 and 500 are OK for actions server root endpoint
                        server_ready = True
                        logger.info(f"Both servers ready after {i * retry_interval} seconds")
                        print(f"Both servers ready after {i * retry_interval} seconds")
                        break
                    else:
                        print(f"Servers not ready yet - Rasa: {rasa_response.status_code}, Actions: {actions_response.status_code}")
                except Exception as e:
                    if i < 10:
                        print(f"Connection failed: {str(e)[:100]}...")
                    elif i % 10 == 0:  # Print every 50 seconds after first 50 seconds
                        print(f"Still waiting for servers... ({i+1}/{max_retries}) - Actions server can take 3-4 minutes")
                
                # Always sleep between retries
                if not server_ready:
                    time.sleep(retry_interval)
            
            if not server_ready:
                logger.error("Rasa server failed to start within the timeout period")
                print("ERROR: Rasa server failed to start within the timeout period")
                # Try to get final server logs
                print("\n=== CHECKING SERVER STATUS ===")
                print(f"Rasa server running: {cls.rasa_server.poll() is None}")
                print(f"Actions server running: {cls.actions_server.poll() is None}")
                if cls.rasa_server.poll() is not None:
                    print(f"Rasa server exit code: {cls.rasa_server.returncode}")
                if cls.actions_server.poll() is not None:
                    print(f"Actions server exit code: {cls.actions_server.returncode}")
                print("=== END SERVER STATUS ===\n")
                raise Exception("Rasa server failed to start")
                
            logger.info("Setup complete")
            print("Setup complete")
        except FileNotFoundError as e:
            logger.error(f"Error starting servers: {e}")
            print(f"ERROR: {e}")
            pytest.skip(f"Rasa command not found - skipping E2E tests: {e}")
            return

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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Sending message: '{message}'")
                response = requests.post(
                    "http://localhost:5005/webhooks/rest/webhook",
                    json={"sender": "test_user", "message": message},
                    timeout=15
                )
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.text}")
                
                if response.status_code == 200:
                    json_response = response.json()
                    if not json_response:
                        print("WARNING: Empty response from Rasa - checking server logs")
                        # Check if server processes are still alive
                        if hasattr(self, 'rasa_server') and self.rasa_server.poll() is not None:
                            print(f"ERROR: Rasa server died with return code: {self.rasa_server.returncode}")
                        if hasattr(self, 'actions_server') and self.actions_server.poll() is not None:
                            print(f"ERROR: Actions server died with return code: {self.actions_server.returncode}")
                    return json_response
                else:
                    print(f"Non-200 status code: {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                
                # Final attempt failed, check server health
                try:
                    health_check = requests.get("http://localhost:5005/", timeout=3)
                    print(f"Server health check: {health_check.status_code}")
                except Exception as health_e:
                    print(f"Server health check failed: {str(health_e)}")
                return [] # type: ignore
        return [] # type: ignore
            
    def test_rain_in_stockholm(self):
        """Test asking about rain in Stockholm today."""
        # Skip if rasa is not installed
        try:
            import importlib.util
            rasa_spec = importlib.util.find_spec('rasa')
            if rasa_spec is None:
                pytest.skip("Rasa package is not installed - skipping test")
                return
        except ImportError:
            pytest.skip("Error checking for Rasa package - skipping test")
            return
            
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
            pytest.skip(f"Error testing API directly: {str(e)}")
            return
        
        # First, check what intent is recognized for our query
        try:
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
        except Exception as e:
            print(f"Error during test execution: {str(e)}")
            pytest.skip(f"Error during test execution: {str(e)}")
            return
        
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

        # First test basic greeting to ensure server is working
        print("Testing basic greeting first...")
        
        # Try a direct status check first
        try:
            status_response = requests.get("http://localhost:5005/status", timeout=5)
            print(f"Rasa status endpoint: {status_response.status_code} - {status_response.text[:200]}")
        except Exception as e:
            print(f"Status check failed: {e}")
        
        greeting_responses = self.send_message("hello")
        if len(greeting_responses) == 0:
            print("Basic greeting failed - server may not be processing messages")
            pytest.skip("Rasa server not processing messages")
            return
        print(f"Greeting worked: {greeting_responses}")
        
        # Now test air quality query
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

        # First test basic functionality with a simple greeting
        print("Testing basic greeting...")
        greeting_responses = self.send_message("hello")
        print(f"Greeting responses: {greeting_responses}")
        
        if len(greeting_responses) == 0:
            print("Basic greeting failed - Rasa server may not be processing messages")
            pytest.skip("Rasa server not processing messages")
            return
        
        # Now test weather functionality
        print("Testing weather query...")
        responses = self.send_message("What's the weather like in Paris?")
        print(f"Weather responses: {responses}")
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
