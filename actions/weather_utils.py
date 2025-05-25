# This files contains utility functions for weather-related actions.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

"""
Utility functions for weather-related actions.
"""
import os
import sys
import requests
import logging
import tenacity
from dataclasses import dataclass  # noqa: E402 - Ignore 'from' in import statements
from typing import Dict, Any, Optional, Tuple, List  # noqa: E402 - Ignore 'from' in import statements
from dotenv import load_dotenv  # noqa: E402 - Ignore 'from' in import statements

# Configure logger
logger = logging.getLogger(__name__)

# Check if tenacity is available
has_tenacity = hasattr(tenacity, 'retry')
if not has_tenacity:
    logger.warning("Tenacity module not properly installed, running without retry logic")

# Define fetch_with_retry function based on tenacity availability
if has_tenacity:
    # Use tenacity attributes directly
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10)
    )
    def fetch_with_retry(url: str) -> requests.Response:
        """Fetch data from URL with retry logic for transient failures."""
        return requests.get(url, timeout=10)
else:
    def fetch_with_retry(url: str) -> requests.Response:
        """Simple fetch without retry logic."""
        return requests.get(url, timeout=10)

# API endpoints configuration
API_ENDPOINTS = {
    "current_weather": "http://api.openweathermap.org/data/2.5/weather",
    "forecast": "http://api.openweathermap.org/data/2.5/forecast",
    "uv_index": "http://api.openweathermap.org/data/2.5/uvi",
    "uv_forecast": "http://api.openweathermap.org/data/2.5/uvi/forecast"
}

@dataclass
class UVInfo:
    value: float
    level: str
    advice: str

class WeatherAPIError(Exception):
    """Exception raised for errors in the Weather API."""
    pass

def get_coordinates(location: str, api_key: str) -> Optional[Tuple[float, float]]:
    """Get latitude and longitude for a location."""
    try:
        url = f"{API_ENDPOINTS['current_weather']}?q={location}&appid={api_key}"
        logger.info(f"Fetching coordinates for location: {location}")
        response = fetch_with_retry(url)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch location data: HTTP {response.status_code}")
            return None
            
        geo_data = response.json()
        return geo_data["coord"]["lat"], geo_data["coord"]["lon"]
    except Exception as e:
        logger.error(f"Error getting coordinates for {location}: {str(e)}")
        return None

def get_uv_level(uv_value: float) -> str:
    """Determine UV level based on UV index value."""
    if uv_value < 3:
        return "Low"
    elif uv_value < 6:
        return "Moderate"
    elif uv_value < 8:
        return "High"
    elif uv_value < 11:
        return "Very High"
    else:
        return "Extreme"

def get_protection_advice(uv_value: float) -> str:
    """Get protection advice based on UV index value."""
    if uv_value < 3:
        return "No protection required for most people."
    elif uv_value < 6:
        return "Wear sunscreen, a hat, and sunglasses. Seek shade during midday hours."
    elif uv_value < 8:
        return "Wear sunscreen SPF 30+, protective clothing, a hat, and sunglasses. Reduce time in the sun between 10 AM and 4 PM."
    elif uv_value < 11:
        return "Wear SPF 30+ sunscreen, protective clothing, a wide-brim hat, and UV-blocking sunglasses. Try to avoid sun exposure between 10 AM and 4 PM."
    else:
        return "Take all precautions: SPF 30+ sunscreen, protective clothing, wide-brim hat, and UV-blocking sunglasses. Avoid sun exposure as much as possible."

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        url = f"{API_ENDPOINTS['current_weather']}?q={location}&appid={self.api_key}&units=metric"
        response = fetch_with_retry(url)
        if response.status_code != 200:
            raise WeatherAPIError(f"Failed to fetch weather data: HTTP {response.status_code}")
        return response.json()
        
    def get_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        url = f"{API_ENDPOINTS['forecast']}?q={location}&appid={self.api_key}&units=metric"
        response = fetch_with_retry(url)
        if response.status_code != 200:
            raise WeatherAPIError(f"Failed to fetch forecast data: HTTP {response.status_code}")
        return response.json()
        
    def get_uv_index(self, lat: float, lon: float) -> UVInfo:
        """Get current UV index for coordinates."""
        url = f"{API_ENDPOINTS['uv_index']}?lat={lat}&lon={lon}&appid={self.api_key}"
        response = fetch_with_retry(url)
        if response.status_code != 200:
            raise WeatherAPIError(f"Failed to fetch UV data: HTTP {response.status_code}")
        
        data = response.json()
        uv_value = data["value"]
        level = get_uv_level(uv_value)
        advice = get_protection_advice(uv_value)
        
        return UVInfo(value=uv_value, level=level, advice=advice)
        
    def get_uv_forecast(self, lat: float, lon: float, days: int = 1) -> List[Dict[str, Any]]:
        """Get UV index forecast for coordinates."""
        url = f"{API_ENDPOINTS['uv_forecast']}?lat={lat}&lon={lon}&appid={self.api_key}&cnt={days+1}"
        response = fetch_with_retry(url)
        if response.status_code != 200:
            raise WeatherAPIError(f"Failed to fetch UV forecast data: HTTP {response.status_code}")
        return response.json()
    

def validate_env_vars(required_vars: List[str]) -> bool:
    """
    Validate that all required environment variables are set.
    Logs an error message if any are missing.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        True if all required vars are present, False otherwise
    """
    load_dotenv()
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment.")
        return False
    
    return True

def get_api_key() -> Optional[str]:
    """Get the OpenWeather API key from environment variables."""
    return os.environ.get("OPENWEATHER_API_KEY")

def fetch_current_weather(location: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Fetch current weather data for a location.
    
    Args:
        location: The name of the location to get weather for
        
    Returns:
        Tuple containing status code and response data (or None if request failed)
    """
    api_key = get_api_key()
    if not api_key:
        return 401, None
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return 200, response.json()
        return response.status_code, None
    except requests.exceptions.RequestException:
        return 500, None

def fetch_weather_forecast(location: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Fetch weather forecast data for a location.
    
    Args:
        location: The name of the location to get forecast for
        
    Returns:
        Tuple containing status code and response data (or None if request failed)
    """
    api_key = get_api_key()
    if not api_key:
        return 401, None
        
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return 200, response.json()
        return response.status_code, None
    except requests.exceptions.RequestException:
        return 500, None