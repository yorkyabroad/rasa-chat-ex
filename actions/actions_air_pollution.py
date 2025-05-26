# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import os
import logging
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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