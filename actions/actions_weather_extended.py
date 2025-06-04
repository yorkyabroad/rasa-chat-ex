# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import os
import logging
import datetime
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv
from .weather_utils import WeatherService, WeatherAPIError, get_coordinates

logger = logging.getLogger(__name__)

class ActionGetSevereWeatherAlerts(Action):
    def name(self) -> Text:
        return "action_get_severe_weather_alerts"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather alert service is currently unavailable.")
            return []
        
        try:
            # First get coordinates for the location
            lat, lon = get_coordinates(location, api_key)
            if not lat or not lon:
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
            
            # Get weather alerts using OneCall API
            url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={api_key}"
            logger.info(f"Fetching weather alerts for coordinates: {lat}, {lon}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("alerts", [])
                
                if alerts:
                    message = f"Weather alerts for {location}:\n\n"
                    for i, alert in enumerate(alerts, 1):
                        event = alert.get("event", "Weather alert")
                        description = alert.get("description", "No details available")
                        sender = alert.get("sender_name", "Weather service")
                        
                        # Format start and end times
                        start_time = datetime.datetime.fromtimestamp(alert.get("start", 0))
                        end_time = datetime.datetime.fromtimestamp(alert.get("end", 0))
                        
                        message += f"ALERT {i}: {event}\n"
                        message += f"• From: {start_time.strftime('%Y-%m-%d %H:%M')}\n"
                        message += f"• Until: {end_time.strftime('%Y-%m-%d %H:%M')}\n"
                        message += f"• Issued by: {sender}\n"
                        message += f"• Details: {description[:100]}...\n\n"
                    
                    dispatcher.utter_message(text=message)
                else:
                    dispatcher.utter_message(text=f"Good news! There are no weather alerts for {location} at this time.")
            else:
                logger.error(f"Failed to fetch weather alerts: HTTP {response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch weather alerts for that location. Try again.")
        except Exception as e:
            logger.error(f"Error fetching weather alerts for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching weather alerts.")
        
        return []

class ActionGetPrecipitation(Action):
    def name(self) -> Text:
        return "action_get_precipitation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        time_period = tracker.get_slot("time_period") or "today"
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            # First get coordinates for the location
            lat, lon = get_coordinates(location, api_key)
            if not lat or not lon:
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
            
            # Get precipitation data using OneCall API
            url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,current,alerts&units=metric&appid={api_key}"
            logger.info(f"Fetching precipitation data for coordinates: {lat}, {lon}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if time_period.lower() in ["today", "now"]:
                    # Get today's hourly forecast
                    hourly_data = data.get("hourly", [])[:24]  # Next 24 hours
                    
                    # Calculate precipitation probability
                    rain_hours = sum(1 for hour in hourly_data if hour.get("pop", 0) > 0.2)
                    max_pop = max((hour.get("pop", 0) for hour in hourly_data), default=0)
                    
                    # Check for rain or snow volume
                    has_rain = any("rain" in hour for hour in hourly_data)
                    has_snow = any("snow" in hour for hour in hourly_data)
                    
                    rain_volume = sum(hour.get("rain", {}).get("1h", 0) for hour in hourly_data if "rain" in hour)
                    snow_volume = sum(hour.get("snow", {}).get("1h", 0) for hour in hourly_data if "snow" in hour)
                    
                    message = f"Precipitation forecast for {location} today:\n\n"
                    message += f"• Chance of precipitation: {int(max_pop * 100)}%\n"
                    
                    if has_rain:
                        message += f"• Expected rainfall: {rain_volume:.1f} mm\n"
                    if has_snow:
                        message += f"• Expected snowfall: {snow_volume:.1f} mm\n"
                    
                    if rain_hours > 0:
                        message += f"• Precipitation expected for approximately {rain_hours} hours today"
                    else:
                        message += "• No significant precipitation expected today"
                    
                    dispatcher.utter_message(text=message)
                    
                elif time_period.lower() in ["tomorrow"]:
                    # Get tomorrow's data
                    daily_data = data.get("daily", [])
                    if len(daily_data) > 1:
                        tomorrow = daily_data[1]
                        
                        pop = tomorrow.get("pop", 0)
                        rain = tomorrow.get("rain", 0)
                        snow = tomorrow.get("snow", 0)
                        
                        message = f"Precipitation forecast for {location} tomorrow:\n\n"
                        message += f"• Chance of precipitation: {int(pop * 100)}%\n"
                        
                        if rain:
                            message += f"• Expected rainfall: {rain:.1f} mm\n"
                        if snow:
                            message += f"• Expected snowfall: {snow:.1f} mm\n"
                        
                        if pop > 0.5:
                            message += "• Prepare for wet conditions"
                        elif pop > 0.2:
                            message += "• Some precipitation possible"
                        else:
                            message += "• No significant precipitation expected"
                        
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text=f"I couldn't get tomorrow's precipitation forecast for {location}.")
                
                else:
                    dispatcher.utter_message(text=f"I can only provide precipitation forecasts for today or tomorrow.")
            else:
                logger.error(f"Failed to fetch precipitation data: HTTP {response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch precipitation data for that location. Try again.")
        except Exception as e:
            logger.error(f"Error fetching precipitation data for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching precipitation data.")
        
        return []

class ActionGetWindConditions(Action):
    def name(self) -> Text:
        return "action_get_wind_conditions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        time_period = tracker.get_slot("time_period") or "today"
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            # Get current wind conditions
            if time_period.lower() in ["today", "now"]:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                logger.info(f"Fetching current wind data for location: {location}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    wind_speed = data["wind"]["speed"]
                    wind_deg = data["wind"]["deg"]
                    wind_gust = data["wind"].get("gust", wind_speed * 1.5)  # Estimate gust if not provided
                    
                    # Convert degrees to direction
                    wind_direction = self._degree_to_direction(wind_deg)
                    
                    # Determine if it's windy
                    wind_description = self._describe_wind(wind_speed)
                    outdoor_recommendation = self._outdoor_recommendation(wind_speed)
                    
                    message = f"Current wind conditions in {location}:\n\n"
                    message += f"• Wind speed: {wind_speed:.1f} m/s ({self._ms_to_kmh(wind_speed):.1f} km/h)\n"
                    message += f"• Wind direction: {wind_direction} ({wind_deg}°)\n"
                    message += f"• Wind gusts up to: {wind_gust:.1f} m/s ({self._ms_to_kmh(wind_gust):.1f} km/h)\n"
                    message += f"• Conditions: {wind_description}\n"
                    message += f"• {outdoor_recommendation}"
                    
                    dispatcher.utter_message(text=message)
                else:
                    logger.error(f"Failed to fetch wind data: HTTP {response.status_code}")
                    dispatcher.utter_message(text="I couldn't fetch wind conditions for that location. Try again.")
            
            # Get tomorrow's wind forecast
            elif time_period.lower() in ["tomorrow"]:
                # First get coordinates
                lat, lon = get_coordinates(location, api_key)
                if not lat or not lon:
                    dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                    return []
                
                # Get forecast data
                url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&units=metric&appid={api_key}"
                logger.info(f"Fetching wind forecast for coordinates: {lat}, {lon}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    daily_data = data.get("daily", [])
                    
                    if len(daily_data) > 1:
                        tomorrow = daily_data[1]
                        wind_speed = tomorrow.get("wind_speed", 0)
                        wind_deg = tomorrow.get("wind_deg", 0)
                        wind_gust = tomorrow.get("wind_gust", wind_speed * 1.5)
                        
                        # Convert degrees to direction
                        wind_direction = self._degree_to_direction(wind_deg)
                        
                        # Determine if it's windy
                        wind_description = self._describe_wind(wind_speed)
                        outdoor_recommendation = self._outdoor_recommendation(wind_speed)
                        
                        message = f"Wind forecast for {location} tomorrow:\n\n"
                        message += f"• Wind speed: {wind_speed:.1f} m/s ({self._ms_to_kmh(wind_speed):.1f} km/h)\n"
                        message += f"• Wind direction: {wind_direction} ({wind_deg}°)\n"
                        message += f"• Wind gusts up to: {wind_gust:.1f} m/s ({self._ms_to_kmh(wind_gust):.1f} km/h)\n"
                        message += f"• Expected conditions: {wind_description}\n"
                        message += f"• {outdoor_recommendation}"
                        
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text=f"I couldn't get tomorrow's wind forecast for {location}.")
                else:
                    logger.error(f"Failed to fetch wind forecast: HTTP {response.status_code}")
                    dispatcher.utter_message(text="I couldn't fetch the wind forecast for that location. Try again.")
            
            else:
                dispatcher.utter_message(text=f"I can only provide wind conditions for today or tomorrow.")
                
        except Exception as e:
            logger.error(f"Error fetching wind data for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching wind data.")
        
        return []
    
    def _degree_to_direction(self, degree):
        directions = ["North", "North-Northeast", "Northeast", "East-Northeast", 
                      "East", "East-Southeast", "Southeast", "South-Southeast",
                      "South", "South-Southwest", "Southwest", "West-Southwest", 
                      "West", "West-Northwest", "Northwest", "North-Northwest", "North"]
        
        # Convert degrees to 0-16 range
        val = int((degree / 22.5) + 0.5)
        return directions[val % 16]
    
    def _ms_to_kmh(self, speed_ms):
        return speed_ms * 3.6
    
    def _describe_wind(self, speed_ms):
        if speed_ms < 0.5:
            return "Calm"
        elif speed_ms < 1.5:
            return "Light air"
        elif speed_ms < 3.3:
            return "Light breeze"
        elif speed_ms < 5.5:
            return "Gentle breeze"
        elif speed_ms < 7.9:
            return "Moderate breeze"
        elif speed_ms < 10.7:
            return "Fresh breeze"
        elif speed_ms < 13.8:
            return "Strong breeze"
        elif speed_ms < 17.1:
            return "High wind"
        elif speed_ms < 20.7:
            return "Gale"
        elif speed_ms < 24.4:
            return "Strong gale"
        elif speed_ms < 28.4:
            return "Storm"
        elif speed_ms < 32.6:
            return "Violent storm"
        else:
            return "Hurricane force"
    
    def _outdoor_recommendation(self, speed_ms):
        if speed_ms < 5.5:
            return "Perfect for most outdoor activities."
        elif speed_ms < 10.7:
            return "Good for most activities, but might affect precision sports."
        elif speed_ms < 17.1:
            return "Challenging for cycling and some outdoor activities."
        elif speed_ms < 24.4:
            return "Not recommended for most outdoor activities."
        else:
            return "Dangerous conditions - stay indoors."

class ActionGetSunriseSunset(Action):
    def name(self) -> Text:
        return "action_get_sunrise_sunset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        time_period = tracker.get_slot("time_period") or "today"
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            if time_period.lower() in ["today", "now"]:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
                logger.info(f"Fetching sunrise/sunset data for location: {location}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    sunrise_timestamp = data["sys"]["sunrise"]
                    sunset_timestamp = data["sys"]["sunset"]
                    timezone_offset = data["timezone"]
                    
                    # Convert to local time
                    sunrise_time = datetime.datetime.utcfromtimestamp(sunrise_timestamp + timezone_offset)
                    sunset_time = datetime.datetime.utcfromtimestamp(sunset_timestamp + timezone_offset)
                    
                    # Calculate daylight hours
                    daylight_seconds = sunset_timestamp - sunrise_timestamp
                    daylight_hours = daylight_seconds / 3600
                    
                    message = f"Sunrise and sunset times for {location} today:\n\n"
                    message += f"• Sunrise: {sunrise_time.strftime('%H:%M')}\n"
                    message += f"• Sunset: {sunset_time.strftime('%H:%M')}\n"
                    message += f"• Daylight hours: {int(daylight_hours)} hours and {int((daylight_hours % 1) * 60)} minutes"
                    
                    dispatcher.utter_message(text=message)
                else:
                    logger.error(f"Failed to fetch sunrise/sunset data: HTTP {response.status_code}")
                    dispatcher.utter_message(text="I couldn't fetch sunrise and sunset times for that location. Try again.")
            
            elif time_period.lower() in ["tomorrow"]:
                # First get coordinates
                lat, lon = get_coordinates(location, api_key)
                if not lat or not lon:
                    dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                    return []
                
                # Get forecast data
                url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={api_key}"
                logger.info(f"Fetching sunrise/sunset forecast for coordinates: {lat}, {lon}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    daily_data = data.get("daily", [])
                    timezone_offset = data.get("timezone_offset", 0)
                    
                    if len(daily_data) > 1:
                        tomorrow = daily_data[1]
                        sunrise_timestamp = tomorrow["sunrise"]
                        sunset_timestamp = tomorrow["sunset"]
                        
                        # Convert to local time
                        sunrise_time = datetime.datetime.utcfromtimestamp(sunrise_timestamp + timezone_offset)
                        sunset_time = datetime.datetime.utcfromtimestamp(sunset_timestamp + timezone_offset)
                        
                        # Calculate daylight hours
                        daylight_seconds = sunset_timestamp - sunrise_timestamp
                        daylight_hours = daylight_seconds / 3600
                        
                        message = f"Sunrise and sunset times for {location} tomorrow:\n\n"
                        message += f"• Sunrise: {sunrise_time.strftime('%H:%M')}\n"
                        message += f"• Sunset: {sunset_time.strftime('%H:%M')}\n"
                        message += f"• Daylight hours: {int(daylight_hours)} hours and {int((daylight_hours % 1) * 60)} minutes"
                        
                        dispatcher.utter_message(text=message)
                    else:
                        dispatcher.utter_message(text=f"I couldn't get tomorrow's sunrise and sunset times for {location}.")
                else:
                    logger.error(f"Failed to fetch sunrise/sunset forecast: HTTP {response.status_code}")
                    dispatcher.utter_message(text="I couldn't fetch the sunrise and sunset forecast for that location. Try again.")
            
            else:
                dispatcher.utter_message(text=f"I can only provide sunrise and sunset times for today or tomorrow.")
                
        except Exception as e:
            logger.error(f"Error fetching sunrise/sunset data for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching sunrise and sunset data.")
        
        return []

class ActionGetWeatherComparison(Action):
    def name(self) -> Text:
        return "action_get_weather_comparison"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            # Get current weather
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            logger.info(f"Fetching current weather for location: {location}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current_temp = data["main"]["temp"]
                current_weather = data["weather"][0]["description"]
                
                # Get yesterday's weather using historical data
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]
                
                # Calculate yesterday's timestamp
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                yesterday_timestamp = int(yesterday.timestamp())
                
                # Get historical data
                hist_url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={yesterday_timestamp}&appid={api_key}&units=metric"
                logger.info(f"Fetching historical weather for coordinates: {lat}, {lon}")
                hist_response = requests.get(hist_url, timeout=10)
                
                if hist_response.status_code == 200:
                    hist_data = hist_response.json()
                    yesterday_temp = hist_data["data"][0]["temp"]
                    yesterday_weather = hist_data["data"][0]["weather"][0]["description"]
                    
                    # Compare temperatures
                    temp_diff = current_temp - yesterday_temp
                    
                    if abs(temp_diff) < 1:
                        temp_comparison = "about the same temperature as"
                    elif temp_diff > 0:
                        temp_comparison = f"{abs(temp_diff):.1f}°C warmer than"
                    else:
                        temp_comparison = f"{abs(temp_diff):.1f}°C cooler than"
                    
                    message = f"Weather comparison for {location}:\n\n"
                    message += f"• Today: {current_weather}, {current_temp:.1f}°C\n"
                    message += f"• Yesterday: {yesterday_weather}, {yesterday_temp:.1f}°C\n\n"
                    message += f"Today is {temp_comparison} yesterday."
                    
                    dispatcher.utter_message(text=message)
                else:
                    logger.error(f"Failed to fetch historical data: HTTP {hist_response.status_code}")
                    dispatcher.utter_message(text=f"I could only get today's weather for {location}: {current_weather}, {current_temp:.1f}°C")
            else:
                logger.error(f"Failed to fetch weather data: HTTP {response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch weather data for that location. Try again.")
                
        except Exception as e:
            logger.error(f"Error comparing weather for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while comparing weather data.")
        
        return []