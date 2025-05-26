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

logger = logging.getLogger(__name__)

class ActionGetAirPollutionForecast(Action):
    def name(self) -> Text:
        return "action_get_air_pollution_forecast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        if not location:
            dispatcher.utter_message(text="I couldn't find the location. Could you please provide it?")
            return []

        load_dotenv()
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            dispatcher.utter_message(text="Air quality forecast service is currently unavailable.")
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
            
            # Get air pollution forecast data
            forecast_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
            logger.info(f"Fetching air pollution forecast for coordinates: {lat}, {lon}")
            forecast_response = requests.get(forecast_url, timeout=10)
            
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                
                if not forecast_data.get("list"):
                    logger.error("No forecast data available")
                    dispatcher.utter_message(text=f"I couldn't find air pollution forecast data for {location}.")
                    return []
                
                # Get tomorrow's date
                tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                tomorrow_date = tomorrow.date()
                
                # Filter forecast data for tomorrow
                tomorrow_forecasts = []
                for item in forecast_data["list"]:
                    forecast_time = datetime.datetime.fromtimestamp(item["dt"])
                    if forecast_time.date() == tomorrow_date:
                        tomorrow_forecasts.append(item)
                
                if not tomorrow_forecasts:
                    logger.error("No forecast data available for tomorrow")
                    dispatcher.utter_message(text=f"I couldn't find tomorrow's air pollution forecast for {location}.")
                    return []
                
                # Calculate average AQI for tomorrow
                aqi_values = [item["main"]["aqi"] for item in tomorrow_forecasts]
                avg_aqi = sum(aqi_values) / len(aqi_values)
                most_common_aqi = max(set(aqi_values), key=aqi_values.count)
                
                # Get components from midday forecast if available, otherwise use the first forecast
                midday_forecasts = [f for f in tomorrow_forecasts if 
                                   datetime.datetime.fromtimestamp(f["dt"]).hour >= 11 and
                                   datetime.datetime.fromtimestamp(f["dt"]).hour <= 13]
                
                forecast_item = midday_forecasts[0] if midday_forecasts else tomorrow_forecasts[0]
                components = forecast_item["components"]
                
                # Extract key pollutants
                pm2_5 = components.get("pm2_5", 0)
                pm10 = components.get("pm10", 0)
                no2 = components.get("no2", 0)
                o3 = components.get("o3", 0)
                
                aqi_level = self._get_aqi_level(most_common_aqi)
                health_implications = self._get_health_implications(most_common_aqi)
                
                tomorrow_str = tomorrow_date.strftime("%A, %B %d")
                
                logger.info(f"Successfully retrieved air quality forecast for {location}: AQI {most_common_aqi} ({aqi_level})")
                
                message = (
                    f"The air quality forecast for {location} tomorrow ({tomorrow_str}) is {aqi_level} (AQI: {most_common_aqi}).\n"
                    f"Expected pollutant levels:\n"
                    f"• PM2.5: {pm2_5:.1f} μg/m³\n"
                    f"• PM10: {pm10:.1f} μg/m³\n"
                    f"• NO₂: {no2:.1f} μg/m³\n"
                    f"• O₃: {o3:.1f} μg/m³\n\n"
                    f"{health_implications}"
                )
                
                dispatcher.utter_message(text=message)
            else:
                logger.error(f"Failed to fetch air quality forecast: HTTP {forecast_response.status_code}")
                dispatcher.utter_message(text="I couldn't fetch the air quality forecast for that location. Try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Air quality forecast API request error for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching the air quality forecast data.")
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing air quality forecast data for {location}: {str(e)}")
            dispatcher.utter_message(text="Sorry, I couldn't process the air quality forecast data for that location.")
        
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