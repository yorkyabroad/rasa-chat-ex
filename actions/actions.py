# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import os
import random
import logging
import datetime
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv
from .weather_utils import (
    WeatherService, WeatherAPIError, get_coordinates, 
    get_uv_level, get_protection_advice
)

logger = logging.getLogger(__name__)

class ActionFetchWeather(Action):
    def name(self) -> Text:
        return "action_fetch_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            weather_service = WeatherService(api_key)
            data = weather_service.get_current_weather(location)
            
            temperature = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            logger.info(f"Successfully retrieved weather for {location}: {weather}, {temperature}°C")
            
            dispatcher.utter_message(
                text=f"The current weather in {location} is {weather} with a temperature of {temperature}°C."
            )
        except WeatherAPIError as e:
            logger.error(f"Weather API error for {location}: {str(e)}")
            dispatcher.utter_message(text="I couldn't fetch the weather for that location. Try again.")
        except Exception as e:
            logger.error(f"Error fetching weather for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather data.")
        
        return []
    


class ActionRandomFact(Action):
    def name(self) -> Text:
        return "action_random_fact"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not."
        ]
        dispatcher.utter_message(text=random.choice(facts))
        return []

class ActionCompareWeather(Action):
    def name(self) -> Text:
        return "action_compare_weather"

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
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            logger.info(f"Fetching weather comparison data for location: {location}")
            response = requests.get(current_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current_temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                
                avg_temp = 22.0
                temp_diff = current_temp - avg_temp
                
                if abs(temp_diff) < 2:
                    comparison = "about average"
                elif temp_diff > 5:
                    comparison = "much warmer"
                elif temp_diff > 2:
                    comparison = "warmer"
                elif temp_diff < -5:
                    comparison = "much colder"
                else:
                    comparison = "colder"
                
                dispatcher.utter_message(
                    text=f"The current temperature in {location} is {current_temp}°C, which is {comparison} than average for this time of year."
                )
            else:
                logger.error(f"Failed to fetch weather data: HTTP {response.status_code} for location {location}")
                dispatcher.utter_message(text="I couldn't fetch the weather for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather comparison API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while comparing weather data.")
        
        return []

class ActionGetLocalTime(Action):
    def name(self) -> Text:
        return "action_get_local_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        weather_api_key = os.environ.get("OPENWEATHER_API_KEY")
        timezone_api_key = os.environ.get("TIMEZONE_API_KEY")

        if not weather_api_key:
            dispatcher.utter_message(text="Location service is currently unavailable.")
            return []

        try:
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}"
            logger.info(f"Fetching coordinates for location: {location}")
            weather_response = requests.get(weather_url, timeout=10)

            if weather_response.status_code != 200:
                logger.error(f"Failed to fetch location data: HTTP {weather_response.status_code}")
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []

            weather_data = weather_response.json()
            lat = weather_data["coord"]["lat"]
            lon = weather_data["coord"]["lon"]
            timezone_offset = weather_data.get("timezone", 0)

            if timezone_api_key:
                timezone_url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_api_key}&format=json&by=position&lat={lat}&lng={lon}"
                logger.info(f"Fetching timezone data for coordinates: {lat}, {lon}")
                timezone_response = requests.get(timezone_url, timeout=10)

                if timezone_response.status_code == 200:
                    timezone_data = timezone_response.json()
                    local_time = timezone_data["formatted"]
                    zone_name = timezone_data["zoneName"]
                    logger.info(f"Successfully retrieved timezone data for {location}: {zone_name}")
                    dispatcher.utter_message(
                        text=f"The current time in {location} ({zone_name}) is {local_time.split()[1]}"
                    )
                    return []

            utc_time = datetime.datetime.utcnow()
            local_time = utc_time + datetime.timedelta(seconds=timezone_offset)
            formatted_time = local_time.strftime("%H:%M")
            logger.info(f"Calculated local time for {location} using timezone offset")
            dispatcher.utter_message(
                text=f"The current time in {location} is approximately {formatted_time} (based on timezone offset)"
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the local time data.")

        return []

class ActionFetchWeatherForecast(Action):
    def name(self) -> Text:
        return "action_fetch_weather_forecast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        days = tracker.get_slot("days") or 3
        
        if isinstance(days, str) and days.isdigit():
            days = int(days)
        elif isinstance(days, str):
            days = 3
        days = min(max(1, int(days)), 3)
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather forecast service is currently unavailable.")
            return []
        
        try:    
            # Get coordinates first for UV index
            geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
            geo_response = requests.get(geo_url, timeout=10)
            
            if geo_response.status_code != 200:
                logger.error(f"Failed to fetch location data: HTTP {geo_response.status_code}")
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
                
            geo_data = geo_response.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]
            
            # Get forecast data
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
            logger.info(f"Fetching {days}-day forecast for location: {location}")
            response = requests.get(url, timeout=10)
            
            # Get UV index data
            uv_url = f"http://api.openweathermap.org/data/2.5/uvi/forecast?lat={lat}&lon={lon}&appid={api_key}&cnt={days}"
            uv_response = requests.get(uv_url, timeout=10)
            uv_data = {}
            
            if uv_response.status_code == 200:
                uv_list = uv_response.json()
                for uv_item in uv_list:
                    date = datetime.datetime.fromtimestamp(uv_item["date"]).date()
                    uv_data[date] = uv_item["value"]
                logger.info(f"Successfully retrieved UV index data for {location}")
            else:
                logger.warning(f"Failed to fetch UV data: HTTP {uv_response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Received forecast data with {len(data['list'])} time points")
                
                forecast_message = f"Weather forecast for {location} for the next {days} day(s):\n"
                current_date = None
                day_count = 0
                
                # Get today's date to ensure we include it
                today = datetime.datetime.now().date()
                
                # First add today's forecast if available
                today_forecasts = [f for f in data["list"] if 
                                  datetime.datetime.fromtimestamp(f["dt"]).date() == today]
                
                if today_forecasts and day_count < days:
                    day_count += 1
                    current_date = today
                    date_str = today.strftime("%A, %B %d") + " (Today)"
                    
                    # Find forecast closest to noon for today
                    noon_forecasts = [f for f in today_forecasts if 
                                     datetime.datetime.fromtimestamp(f["dt"]).hour >= 11 and
                                     datetime.datetime.fromtimestamp(f["dt"]).hour <= 13]
                    
                    day_forecast = noon_forecasts[0] if noon_forecasts else today_forecasts[0]
                    temp = day_forecast["main"]["temp"]
                    weather = day_forecast["weather"][0]["description"]
                    
                    # Add UV index if available
                    uv_info = ""
                    if today in uv_data:
                        uv_value = uv_data[today]
                        uv_level = self._get_uv_level(uv_value)
                        uv_info = f", UV index: {uv_value:.1f} ({uv_level})"
                    
                    forecast_message += f"\n• {date_str}: {weather}, temperature around {temp}°C{uv_info}"
                    logger.debug(f"Added forecast for {date_str}: {weather}, {temp}°C{uv_info}")
                
                # Then process the rest of the days
                for item in data["list"]:
                    forecast_date = datetime.datetime.fromtimestamp(item["dt"]).date()
                    
                    # Simple comparison - just check if dates are different
                    if forecast_date != current_date:
                        # Skip dates we've already processed
                        if day_count >= days:
                            break
                        if day_count >= days:
                            break
                        
                        current_date = forecast_date
                        day_count += 1
                        date_str = forecast_date.strftime("%A, %B %d")
                        
                        noon_forecasts = [f for f in data["list"] if 
                                         datetime.datetime.fromtimestamp(f["dt"]).date() == forecast_date and
                                         datetime.datetime.fromtimestamp(f["dt"]).hour >= 11 and
                                         datetime.datetime.fromtimestamp(f["dt"]).hour <= 13]
                        
                        if noon_forecasts:
                            day_forecast = noon_forecasts[0]
                            temp = day_forecast["main"]["temp"]
                            weather = day_forecast["weather"][0]["description"]
                            
                            # Add UV index if available
                            uv_info = ""
                            if forecast_date in uv_data:
                                uv_value = uv_data[forecast_date]
                                uv_level = self._get_uv_level(uv_value)
                                uv_info = f", UV index: {uv_value:.1f} ({uv_level})"
                            
                            forecast_message += f"\n• {date_str}: {weather}, temperature around {temp}°C{uv_info}"
                            logger.debug(f"Added forecast for {date_str}: {weather}, {temp}°C{uv_info}")
                
                logger.info(f"Successfully generated {day_count}-day forecast for {location}")
                dispatcher.utter_message(text=forecast_message)
            else:
                logger.error(f"Failed to fetch forecast data: HTTP {response.status_code} for location {location}")
                dispatcher.utter_message(text="I couldn't fetch the weather forecast for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather forecast data.")
        
        return []
        
    def _get_uv_level(self, uv_value):
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

class ActionGetHumidity(Action):
    def name(self) -> Text:
        return "action_get_humidity"

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
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            logger.info(f"Fetching humidity data for location: {location}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                humidity = data["main"]["humidity"]
                logger.info(f"Successfully retrieved humidity for {location}: {humidity}%")
                dispatcher.utter_message(
                    text=f"The current humidity in {location} is {humidity}%"
                )
            else:
                logger.error(f"Failed to fetch weather data: HTTP {response.status_code} for location {location}")
                dispatcher.utter_message(text="I couldn't fetch the humidity for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the humidity data.")
        
        return []

class ActionGetUVIndex(Action):
    def name(self) -> Text:
        return "action_get_uv_index"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            # First get coordinates for the location
            geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
            logger.info(f"Fetching coordinates for location: {location}")
            geo_response = requests.get(geo_url, timeout=10)
            
            if geo_response.status_code != 200:
                logger.error(f"Failed to fetch location data: HTTP {geo_response.status_code}")
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
                
            geo_data = geo_response.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]
            
            # Get current UV index
            uv_url = f"http://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={api_key}"
            logger.info(f"Fetching UV index data for coordinates: {lat}, {lon}")
            uv_response = requests.get(uv_url, timeout=10)
            
            if uv_response.status_code == 200:
                uv_data = uv_response.json()
                uv_value = uv_data["value"]
                uv_level = self._get_uv_level(uv_value)
                
                protection_advice = self._get_protection_advice(uv_value)
                
                logger.info(f"Successfully retrieved UV index for {location}: {uv_value} ({uv_level})")
                dispatcher.utter_message(
                    text=f"The current UV index in {location} is {uv_value:.1f} ({uv_level}).\n{protection_advice}"
                )
            else:
                logger.error(f"Failed to fetch UV data: HTTP {uv_response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch the UV index for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"UV index API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the UV index data.")
        
        return []
        
    def _get_uv_level(self, uv_value):
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
            
    def _get_protection_advice(self, uv_value):
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

class ActionGetUVIndexForecast(Action):
    def name(self) -> Text:
        return "action_get_uv_index_forecast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        days = tracker.get_slot("days") or 1  # Default to tomorrow
        
        if isinstance(days, str) and days.isdigit():
            days = int(days)
        elif isinstance(days, str):
            days = 1
        days = min(max(1, int(days)), 5)  # Limit to 1-5 days
        
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
            geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
            logger.info(f"Fetching coordinates for location: {location}")
            geo_response = requests.get(geo_url, timeout=10)
            
            if geo_response.status_code != 200:
                logger.error(f"Failed to fetch location data: HTTP {geo_response.status_code}")
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
                
            geo_data = geo_response.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]
            
            # Get UV index forecast
            uv_url = f"http://api.openweathermap.org/data/2.5/uvi/forecast?lat={lat}&lon={lon}&appid={api_key}&cnt={days+1}"
            logger.info(f"Fetching UV index forecast for coordinates: {lat}, {lon}")
            uv_response = requests.get(uv_url, timeout=10)
            
            if uv_response.status_code == 200:
                uv_list = uv_response.json()
                
                # Skip today's forecast (index 0) if we want tomorrow
                target_day = 1 if days == 1 else days
                if len(uv_list) > target_day:
                    forecast_date = datetime.datetime.fromtimestamp(uv_list[target_day]["date"]).date()
                    date_str = forecast_date.strftime("%A, %B %d")
                    
                    uv_value = uv_list[target_day]["value"]
                    uv_level = self._get_uv_level(uv_value)
                    protection_advice = self._get_protection_advice(uv_value)
                    
                    day_description = "tomorrow" if target_day == 1 else f"in {target_day} days"
                    
                    logger.info(f"Successfully retrieved UV index forecast for {location}: {uv_value} ({uv_level})")
                    dispatcher.utter_message(
                        text=f"The UV index in {location} {day_description} ({date_str}) is forecast to be {uv_value:.1f} ({uv_level}).\n{protection_advice}"
                    )
                else:
                    logger.error(f"No forecast data available for the requested day")
                    dispatcher.utter_message(text=f"I couldn't get the UV forecast for {days} days ahead. Try a shorter forecast period.")
            else:
                logger.error(f"Failed to fetch UV forecast data: HTTP {uv_response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch the UV index forecast for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"UV index forecast API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the UV index forecast data.")
        
        return []
        
    def _get_uv_level(self, uv_value):
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
            
    def _get_protection_advice(self, uv_value):
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

class ActionGetTemperatureRange(Action):
    def name(self) -> Text:
        return "action_get_temperature_range"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        time_period = tracker.get_slot("time_period") or "today"
        temp_type = tracker.get_slot("temp_type") or "range"  # range, min, max
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:
            # For today's temperature range, use current weather API
            if time_period.lower() == "today":
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                logger.info(f"Fetching current weather data for location: {location}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    temp_min = data["main"]["temp_min"]
                    temp_max = data["main"]["temp_max"]
                    current_temp = data["main"]["temp"]
                    
                    if temp_type.lower() == "min":
                        dispatcher.utter_message(
                            text=f"The minimum temperature in {location} today is {temp_min}°C."
                        )
                    elif temp_type.lower() == "max":
                        dispatcher.utter_message(
                            text=f"The maximum temperature in {location} today is {temp_max}°C."
                        )
                    else:  # range
                        dispatcher.utter_message(
                            text=f"The temperature range in {location} today is between {temp_min}°C and {temp_max}°C. Currently it's {current_temp}°C."
                        )
                else:
                    logger.error(f"Failed to fetch weather data: HTTP {response.status_code} for location {location}")
                    dispatcher.utter_message(text="I couldn't fetch the weather for that location. Try again.")
            
            # For tomorrow's temperature range, use forecast API
            else:
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
                logger.info(f"Fetching forecast data for location: {location}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Get tomorrow's date
                    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
                    
                    # Filter forecast items for tomorrow
                    tomorrow_forecasts = [
                        item for item in data["list"] 
                        if datetime.datetime.fromtimestamp(item["dt"]).date() == tomorrow
                    ]
                    
                    if tomorrow_forecasts:
                        # Find min and max temperatures
                        temp_min = min(item["main"]["temp_min"] for item in tomorrow_forecasts)
                        temp_max = max(item["main"]["temp_max"] for item in tomorrow_forecasts)
                        
                        if temp_type.lower() == "min":
                            dispatcher.utter_message(
                                text=f"The minimum temperature in {location} tomorrow will be around {temp_min}°C."
                            )
                        elif temp_type.lower() == "max":
                            dispatcher.utter_message(
                                text=f"The maximum temperature in {location} tomorrow will be around {temp_max}°C."
                            )
                        else:  # range
                            dispatcher.utter_message(
                                text=f"The temperature in {location} tomorrow will range between {temp_min}°C and {temp_max}°C."
                            )
                    else:
                        dispatcher.utter_message(
                            text=f"I couldn't find forecast data for {location} tomorrow."
                        )
                else:
                    logger.error(f"Failed to fetch forecast data: HTTP {response.status_code} for location {location}")
                    dispatcher.utter_message(text="I couldn't fetch the forecast for that location. Try again.")
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather data.")
        
        return []

class ActionGetAirPollution(Action):
    def name(self) -> Text:
        return "action_get_air_pollution"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Air quality service is currently unavailable.")
            return []
        
        try:
            # First get coordinates for the location
            geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
            logger.info(f"Fetching coordinates for location: {location}")
            geo_response = requests.get(geo_url, timeout=10)
            
            if geo_response.status_code != 200:
                logger.error(f"Failed to fetch location data: HTTP {geo_response.status_code}")
                dispatcher.utter_message(text="I couldn't find that location. Please try again.")
                return []
                
            geo_data = geo_response.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]
            
            # Get current air pollution data
            air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
            logger.info(f"Fetching air pollution data for coordinates: {lat}, {lon}")
            air_response = requests.get(air_url, timeout=10)
            
            if air_response.status_code == 200:
                air_data = air_response.json()
                aqi = air_data["list"][0]["main"]["aqi"]
                components = air_data["list"][0]["components"]
                
                # Extract key pollutants
                pm2_5 = components.get("pm2_5", 0)
                pm10 = components.get("pm10", 0)
                no2 = components.get("no2", 0)
                o3 = components.get("o3", 0)
                
                aqi_level = self._get_aqi_level(aqi)
                health_implications = self._get_health_implications(aqi)
                
                logger.info(f"Successfully retrieved air quality for {location}: AQI {aqi} ({aqi_level})")
                
                message = (
                    f"The current air quality in {location} is {aqi_level} (AQI: {aqi}).\n"
                    f"Key pollutants:\n"
                    f"• PM2.5: {pm2_5:.1f} μg/m³\n"
                    f"• PM10: {pm10:.1f} μg/m³\n"
                    f"• NO₂: {no2:.1f} μg/m³\n"
                    f"• O₃: {o3:.1f} μg/m³\n\n"
                    f"{health_implications}"
                )
                
                dispatcher.utter_message(text=message)
            else:
                logger.error(f"Failed to fetch air quality data: HTTP {air_response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch the air quality for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Air quality API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the air quality data.")
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing air quality data for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I couldn't process the air quality data for that location.")
        
        return []
        
    def _get_aqi_level(self, aqi):
        """Convert AQI numerical value to descriptive level."""
        levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return levels.get(aqi, "Unknown")
            
    def _get_health_implications(self, aqi):
        """Get health implications based on AQI level."""
        implications = {
            1: "Air quality is considered satisfactory, and air pollution poses little or no risk.",
            2: "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.",
            3: "Members of sensitive groups may experience health effects. The general public is not likely to be affected.",
            4: "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.",
            5: "Health warnings of emergency conditions. The entire population is more likely to be affected."
        }
        return implications.get(aqi, "Health implications unknown.")