# This files contains utility functions for weather-related actions.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

"""
Utility functions for weather-related actions.
"""
import os
import requests
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

def get_api_key() -> Optional[str]:
    """Get the OpenWeather API key from environment variables."""
    load_dotenv()
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