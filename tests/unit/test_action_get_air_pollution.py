# tests/test_action_get_air_pollution.py
import pytest
from unittest.mock import patch, MagicMock
import requests
from actions.actions import ActionGetAirPollution

class TestActionGetAirPollution:
    """Tests for the ActionGetAirPollution class."""
    
    def test_air_pollution_success(self):
        """Test successful air pollution data retrieval."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
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
            assert "PM2.5: 4.5" in message
            assert "PM10: 7.6" in message
            assert "NO₂: 9.4" in message
            assert "O₃: 68.7" in message
    
    def test_air_pollution_geo_error(self):
        """Test error handling when geo API fails."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
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
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
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
    
    def test_air_pollution_parse_error(self):
        """Test error handling when parsing air pollution data fails."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response success
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock air pollution response with invalid data
            air_response = MagicMock(status_code=200)
            air_response.json.return_value = {
                "list": []  # Empty list will cause IndexError
            }
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, air_response]
            
            tracker.get_slot.return_value = "London"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't process the air quality data" in message.lower()
    
    def test_aqi_level_mapping(self):
        """Test the AQI level mapping function."""
        action = ActionGetAirPollution()
        
        # Test all AQI levels
        assert action._get_aqi_level(1) == "Good"
        assert action._get_aqi_level(2) == "Fair"
        assert action._get_aqi_level(3) == "Moderate"
        assert action._get_aqi_level(4) == "Poor"
        assert action._get_aqi_level(5) == "Very Poor"
        assert action._get_aqi_level(6) == "Unknown"  # Invalid AQI
    
    def test_health_implications(self):
        """Test the health implications function."""
        action = ActionGetAirPollution()
        
        # Test health implications for each AQI level
        assert "satisfactory" in action._get_health_implications(1)
        assert "acceptable" in action._get_health_implications(2)
        assert "sensitive groups" in action._get_health_implications(3)
        assert "Everyone may begin to experience" in action._get_health_implications(4)
        assert "Health warnings" in action._get_health_implications(5)
        assert "unknown" in action._get_health_implications(6)  # Invalid AQI