# tests/test_action_air_pollution_forecast.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions_air_pollution_forecast import ActionGetAirPollutionForecast

class TestActionAirPollutionForecast:
    """Tests for the ActionGetAirPollutionForecast class."""
    
    def test_missing_location(self):
        """Test handling when location is not provided (lines 22-23)."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Set up tracker to return None for location
        tracker.get_slot.return_value = None
        
        # Run the action
        result = action.run(dispatcher, tracker, domain)
        
        # Check that the appropriate message was sent
        dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
        # Check that an empty list is returned
        assert result == []
    
    def test_missing_api_key(self):
        """Test handling when API key is not available (lines 28-29)."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Set up tracker to return a location
        tracker.get_slot.return_value = "London"
        
        # Mock environment to return None for API key
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get:
            
            mock_env_get.return_value = None
            
            # Run the action
            result = action.run(dispatcher, tracker, domain)
            
            # Check that the appropriate message was sent
            dispatcher.utter_message.assert_called_once_with(
                text="Air quality forecast service is currently unavailable."
            )
            # Check that an empty list is returned
            assert result == []
    
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
    
    def test_geo_api_error(self):
        """Test error handling when geo API fails (lines 38-40)."""
        action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution_forecast.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo API error response
            geo_response = MagicMock(status_code=404)
            mock_requests_get.return_value = geo_response
            
            tracker.get_slot.return_value = "NonExistentLocation"
            result = action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once_with(
                text="I couldn't find that location. Please try again."
            )
            # Check that an empty list is returned
            assert result == []
    
    def test_calculate_aqi_average(self):
        """Test calculation of average AQI for tomorrow (lines 71-73)."""
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
            now = datetime.datetime(2023, 5, 1, 12, 0)
            tomorrow = now + datetime.timedelta(days=1)
            tomorrow_date = tomorrow.date()
            
            mock_datetime.datetime.now.return_value = now
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
            mock_datetime.timedelta.side_effect = datetime.timedelta
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Create forecast data with different AQI values
            tomorrow_timestamp = int(tomorrow.timestamp())
            
            # Mock air pollution forecast response with different AQI values
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": tomorrow_timestamp,
                        "main": {"aqi": 1},  # Good
                        "components": {
                            "pm2_5": 4.51,
                            "pm10": 7.63,
                            "no2": 9.41,
                            "o3": 68.66
                        }
                    },
                    {
                        "dt": tomorrow_timestamp + 3600,
                        "main": {"aqi": 2},  # Fair
                        "components": {
                            "pm2_5": 5.51,
                            "pm10": 8.63,
                            "no2": 10.41,
                            "o3": 70.66
                        }
                    },
                    {
                        "dt": tomorrow_timestamp + 7200,
                        "main": {"aqi": 2},  # Fair (most common)
                        "components": {
                            "pm2_5": 6.51,
                            "pm10": 9.63,
                            "no2": 11.41,
                            "o3": 72.66
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
            
            # Check that the message was sent with the most common AQI (2 - Fair)
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "Fair" in message  # Most common AQI is 2 (Fair)
            assert "AQI: 2" in message
    
    def test_get_health_implications(self):
        """Test the _get_health_implications method (lines 115-120)."""
        action = ActionGetAirPollutionForecast()
        
        # Test each AQI level
        assert "satisfactory" in action._get_health_implications(1)
        assert "acceptable" in action._get_health_implications(2)
        assert "sensitive groups" in action._get_health_implications(3)
        assert "Everyone may begin to experience" in action._get_health_implications(4)
        assert "emergency conditions" in action._get_health_implications(5)
        assert "unknown" in action._get_health_implications(6)  # Invalid AQI