# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


import os
import requests
import datetime
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Dict, Text, Any, List
from dotenv import load_dotenv

class ActionFetchWeather(Action):
    def name(self) -> Text:
        return "action_fetch_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        # Load environment variables
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY")

        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:    
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temperature = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                dispatcher.utter_message(
                    text=f"The current weather in {location} is {weather} with a temperature of {temperature}°C."
                )
            else:
                dispatcher.utter_message(text="I couldn't fetch the weather for that location. Try again.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather data.")
        
        return []

class ActionRandomFact(Action):
    def name(self) -> Text:
        return "action_random_fact"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not."
        ]
        dispatcher.utter_message(text=random.choice(facts))
        return []


class ActionFetchWeatherForecast(Action):
    def name(self) -> Text:
        return "action_fetch_weather_forecast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        days = tracker.get_slot("days") or 3  # Default to 3 days if not specified
        
        # Convert to integer if it's a string
        if isinstance(days, str) and days.isdigit():
            days = int(days)
        elif isinstance(days, str):
            days = 3  # Default to 3 if it's a non-numeric string
        # Limit to 1-3 days
        days = min(max(1, int(days)), 3)
        
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        # Load environment variables
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather forecast service is currently unavailable.")
            return []
        
        try:    
            # OpenWeatherMap 5-day forecast API (provides forecast in 3-hour steps)
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process forecast data
                forecast_message = f"Weather forecast for {location} for the next {days} day(s):\n"
                
                # Group forecasts by day
                current_date = None
                day_count = 0
                
                for item in data["list"]:
                    forecast_date = datetime.datetime.fromtimestamp(item["dt"]).date()
                    
                    # If we've moved to a new day
                    if forecast_date != current_date:
                        if day_count >= days:
                            break
                        
                        current_date = forecast_date
                        day_count += 1
                        
                        # Format the date
                        date_str = forecast_date.strftime("%A, %B %d")
                        
                        # Get the day's weather (using noon forecast as representative)
                        noon_forecasts = [f for f in data["list"] if 
                                         datetime.datetime.fromtimestamp(f["dt"]).date() == forecast_date and
                                         datetime.datetime.fromtimestamp(f["dt"]).hour >= 11 and
                                         datetime.datetime.fromtimestamp(f["dt"]).hour <= 13]
                        
                        if noon_forecasts:
                            day_forecast = noon_forecasts[0]
                            temp = day_forecast["main"]["temp"]
                            weather = day_forecast["weather"][0]["description"]
                            forecast_message += f"\n• {date_str}: {weather}, temperature around {temp}°C"
                
                dispatcher.utter_message(text=forecast_message)
            else:
                dispatcher.utter_message(text="I couldn't fetch the weather forecast for that location. Try again.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather forecast data.")
        
        return []


class ActionCompareWeather(Action):
    def name(self) -> Text:
        return "action_compare_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        # Load environment variables
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Weather service is currently unavailable.")
            return []
        
        try:    
            # Get current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
            response = requests.get(current_url, timeout=10)
            
            if response.status_code != 200:
                dispatcher.utter_message(text="I couldn't fetch the weather for that location. Try again.")
                return []
                
            current_data = response.json()
            current_temp = current_data["main"]["temp"]
            current_weather = current_data["weather"][0]["description"]
            
            # Get historical average data
            # Note: OpenWeatherMap's free tier doesn't provide historical averages
            # This is a simplified example using a mock API or database lookup
            # In a real implementation, you would need a weather API with historical data
            
            # Get current month
            current_month = datetime.datetime.now().month
            
            # Mock average temperatures by month (replace with actual API call)
            average_temps = {
                # Replace these with actual average temperatures for the location
                1: 5.0,   # January
                2: 6.0,   # February
                3: 9.0,   # March
                4: 12.0,  # April
                5: 16.0,  # May
                6: 19.0,  # June
                7: 22.0,  # July
                8: 21.0,  # August
                9: 18.0,  # September
                10: 14.0, # October
                11: 9.0,  # November
                12: 6.0   # December
            }
            
            # Get average temperature for current month
            avg_temp = average_temps.get(current_month, 15.0)  # Default to 15°C if month not found
            
            # Compare current temperature with average
            diff = current_temp - avg_temp
            
            if diff > 5:
                comparison = f"It's much warmer than the average {avg_temp}°C for this time of year."
            elif diff > 2:
                comparison = f"It's a bit warmer than the average {avg_temp}°C for this time of year."
            elif diff < -5:
                comparison = f"It's much colder than the average {avg_temp}°C for this time of year."
            elif diff < -2:
                comparison = f"It's a bit colder than the average {avg_temp}°C for this time of year."
            else:
                comparison = f"It's close to the average {avg_temp}°C for this time of year."
                
            dispatcher.utter_message(
                text=f"The current weather in {location} is {current_weather} with a temperature of {current_temp}°C. {comparison}"
            )
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the weather data.")
            
        return []


class ActionGetLocalTime(Action):
    def name(self) -> Text:
        return "action_get_local_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        # Load environment variables
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Time service is currently unavailable.")
            return []
            
        # First get coordinates from OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]
                
                # Now use TimeZoneDB API to get the local time
                # You'll need to register for a free API key at timezonedb.com
                timezone_api_key = os.environ.get("TIMEZONE_API_KEY")
                if not timezone_api_key:
                    # Fallback to using UTC offset from weather data
                    timezone_offset = data.get("timezone", 0)  # Offset in seconds from UTC
                    utc_time = datetime.datetime.utcnow()
                    local_time = utc_time + datetime.timedelta(seconds=timezone_offset)
                    
                    dispatcher.utter_message(
                        text=f"The current time in {location} is approximately {local_time.strftime('%H:%M')} (based on timezone offset)."
                    )
                else:
                    # Use TimeZoneDB for more accurate results
                    timezone_url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_api_key}&format=json&by=position&lat={lat}&lng={lon}"
                    tz_response = requests.get(timezone_url, timeout=10)
                    
                    if tz_response.status_code == 200:
                        tz_data = tz_response.json()
                        local_time_str = tz_data["formatted"].split(" ")[1]  # Extract time part
                        timezone_name = tz_data["zoneName"]
                        
                        dispatcher.utter_message(
                            text=f"The current time in {location} ({timezone_name}) is {local_time_str}."
                        )
                    else:
                        # Fallback to UTC offset method
                        timezone_offset = data.get("timezone", 0)
                        utc_time = datetime.datetime.utcnow()
                        local_time = utc_time + datetime.timedelta(seconds=timezone_offset)
                        
                        dispatcher.utter_message(
                            text=f"The current time in {location} is approximately {local_time.strftime('%H:%M')} (based on timezone offset)."
                        )
            else:
                dispatcher.utter_message(text="I couldn't find that location to determine the local time.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the time data.")
        
        return []