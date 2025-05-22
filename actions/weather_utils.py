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
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv

import logging

# Configure logger
logger = logging.getLogger(__name__)

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