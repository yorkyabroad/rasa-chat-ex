# tests/test_action_air_pollution.py
import pytest
from unittest.mock import patch, MagicMock
import requests
from actions.actions_air_pollution import ActionGetAirPollution

class TestActionAirPollution:
    """Tests for the ActionGetAirPollution class."""
    
    def test_missing_location(self):
        """Test handling when location is not provided (lines 21-22)."""
        action = ActionGetAirPollution()
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
        """Test handling when API key is not available (lines 27-28)."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Set up tracker to return a location
        tracker.get_slot.return_value = "London"
        
        # Mock environment to return None for API key
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get:
            
            mock_env_get.return_value = None
            
            # Run the action
            result = action.run(dispatcher, tracker, domain)
            
            # Check that the appropriate message was sent
            dispatcher.utter_message.assert_called_once_with(
                text="Air quality service is currently unavailable."
            )
            # Check that an empty list is returned
            assert result == []
    
    def test_air_pollution_success(self):
        """Test successful air pollution data retrieval."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock air pollution response
            air_response = MagicMock(status_code=200)
            air_response.json.return_value = {
                "list": [
                    {
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
                    }
                ]
            }
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, air_response]
            
            # Set up tracker
            tracker.get_slot.return_value = "London"
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "air quality" in message.lower()
            assert "London" in message
            assert "Fair" in message  # AQI 2 = Fair
            assert "PM2.5" in message
            assert "PM10" in message
    
    def test_air_pollution_geo_error(self):
        """Test error handling when geo API fails."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo API error
            geo_response = MagicMock(status_code=404)
            mock_requests_get.return_value = geo_response
            
            tracker.get_slot.return_value = "NonExistentCity"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't find that location" in message.lower()
    
    def test_air_pollution_api_error(self):
        """Test error handling when air pollution API fails."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response success
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock air pollution API error
            air_response = MagicMock(status_code=500)
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, air_response]
            
            tracker.get_slot.return_value = "London"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't fetch the air quality" in message.lower()
    
    def test_extract_pollutant_components(self):
        """Test extraction of pollutant components (lines 80-85)."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock air pollution response with specific component values
            air_response = MagicMock(status_code=200)
            air_response.json.return_value = {
                "list": [
                    {
                        "main": {"aqi": 3},
                        "components": {
                            "pm2_5": 15.5,
                            "pm10": 25.3,
                            "no2": 18.7,
                            "o3": 45.2,
                            "co": 230.31,
                            "so2": 1.16,
                            "nh3": 0.51
                        }
                    }
                ]
            }
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, air_response]
            
            # Set up tracker
            tracker.get_slot.return_value = "London"
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent with the correct pollutant values
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            
            # Verify each pollutant is correctly extracted and formatted
            assert "PM2.5: 15.5 μg/m³" in message
            assert "PM10: 25.3 μg/m³" in message
            assert "NO₂: 18.7 μg/m³" in message
            assert "O₃: 45.2 μg/m³" in message
            assert "Moderate" in message  # AQI 3 = Moderate