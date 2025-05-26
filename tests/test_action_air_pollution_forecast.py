# tests/test_action_air_pollution_forecast.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions_air_pollution_forecast import ActionGetAirPollutionForecast

class TestActionAirPollutionForecast:
    """Tests for the ActionGetAirPollutionForecast class."""
    
    def test_air_pollution_forecast_success(self):
        """Test successful air pollution forecast retrieval."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution_forecast.requests.get') as mock_requests_get, \
             patch('actions.actions_air_pollution_forecast.datetime') as mock_datetime:
            
            # Set up datetime mock
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            mock_datetime.datetime.now.return_value = datetime.datetime.now()
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
            mock_datetime.timedelta.side_effect = datetime.timedelta
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Create forecast data for tomorrow
            tomorrow_timestamp = int(tomorrow.timestamp())
            
            # Mock air pollution forecast response
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": tomorrow_timestamp,
                        "main": {"aqi": 2},
                        "components": {
                            "co": 230.31,
                            "no": 0.89,
                            "no2": 9.41,
                            "o3": 68.66,
                            "so2": 1.16,
                            "pm2_5": 4.51,
                            "pm10": 7.63,
                            "nh3": 0.51
                        }
                    },
                    {
                        "dt": tomorrow_timestamp + 3600,
                        "main": {"aqi": 2},
                        "components": {
                            "co": 240.31,
                            "no": 0.95,
                            "no2": 10.41,
                            "o3": 70.66,
                            "so2": 1.26,
                            "pm2_5": 5.51,
                            "pm10": 8.63,
                            "nh3": 0.61
                        }
                    }
                ]
            }
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response]
            
            # Set up tracker
            tracker.get_slot.return_value = "London"
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "air quality forecast" in message.lower()
            assert "London" in message
            assert "tomorrow" in message.lower()
            assert "Fair" in message  # AQI 2 = Fair
            assert "PM2.5" in message
            assert "PM10" in message
    
    def test_air_pollution_forecast_no_data(self):
        """Test handling of missing forecast data."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution_forecast.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock empty forecast response
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {"list": []}
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response]
            
            tracker.get_slot.return_value = "London"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't find air pollution forecast" in message.lower()
    
    def test_air_pollution_forecast_api_error(self):
        """Test error handling when forecast API fails."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution_forecast.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response success
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock forecast API error
            forecast_response = MagicMock(status_code=500)
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response]
            
            tracker.get_slot.return_value = "London"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't fetch the air quality forecast" in message.lower()