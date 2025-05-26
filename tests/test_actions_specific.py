# tests/test_actions_specific.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import (
    ActionFetchWeather, ActionCompareWeather, ActionGetLocalTime, ActionGetUVIndex
)

class TestActionSpecificHandling:
    """Tests for specific lines in actions.py."""
    
    # Test for ActionCompareWeather temperature comparison logic
    def test_compare_weather_temperature_ranges(self):
        """Test temperature comparison logic in ActionCompareWeather."""
        action = ActionCompareWeather()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API response
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            mock_response = MagicMock(status_code=200)
            mock_requests_get.return_value = mock_response
            tracker.get_slot.return_value = "TestCity"
            
            # Test "about average" case (abs(temp_diff) < 2)
            mock_response.json.return_value = {"main": {"temp": 21.5}, "weather": [{"description": "clear"}]}
            action.run(dispatcher, tracker, domain)
            message = dispatcher.utter_message.call_args[1]['text']
            assert "about average" in message
            
            # Test "much warmer" case (temp_diff > 5)
            dispatcher.reset_mock()
            mock_response.json.return_value = {"main": {"temp": 28.0}, "weather": [{"description": "clear"}]}
            action.run(dispatcher, tracker, domain)
            message = dispatcher.utter_message.call_args[1]['text']
            assert "much warmer" in message
            
            # Test "warmer" case (temp_diff > 2)
            dispatcher.reset_mock()
            mock_response.json.return_value = {"main": {"temp": 24.5}, "weather": [{"description": "clear"}]}
            action.run(dispatcher, tracker, domain)
            message = dispatcher.utter_message.call_args[1]['text']
            assert "warmer" in message
            
            # Test "much colder" case (temp_diff < -5)
            dispatcher.reset_mock()
            mock_response.json.return_value = {"main": {"temp": 16.0}, "weather": [{"description": "clear"}]}
            action.run(dispatcher, tracker, domain)
            message = dispatcher.utter_message.call_args[1]['text']
            assert "much colder" in message
            
            # Test "colder" case (default else branch)
            dispatcher.reset_mock()
            mock_response.json.return_value = {"main": {"temp": 19.5}, "weather": [{"description": "clear"}]}
            action.run(dispatcher, tracker, domain)
            message = dispatcher.utter_message.call_args[1]['text']
            assert "colder" in message
    
    # Test for ActionGetLocalTime timezone fallback
    def test_local_time_timezone_fallback(self):
        """Test timezone fallback in ActionGetLocalTime."""
        action = ActionGetLocalTime()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get, \
             patch('actions.actions.datetime') as mock_datetime:
            
            # Set up mocks for the test
            mock_datetime.datetime.utcnow.return_value = datetime.datetime(2023, 6, 15, 12, 0, 0)
            
            # Mock environment variables - return API key only for weather API
            def mock_env_var(var_name):
                if var_name == "OPENWEATHER_API_KEY":
                    return "fake_api_key"
                return None
            mock_env_get.side_effect = mock_env_var
            
            # Mock weather response with timezone offset
            weather_response = MagicMock(status_code=200)
            weather_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278},
                "timezone": 3600  # 1 hour offset
            }
            
            # Only return the weather response, no timezone API response needed
            mock_requests_get.return_value = weather_response
            tracker.get_slot.return_value = "London"
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the fallback logic was used
            message = dispatcher.utter_message.call_args[1]['text']
            assert "approximately" in message
            assert "based on timezone offset" in message
    
    # Test for ActionGetUVIndex error handling
    def test_uv_index_geo_error_handling(self):
        """Test geo error handling in ActionGetUVIndex."""
        action = ActionGetUVIndex()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Test geo API error
            geo_response = MagicMock(status_code=404)
            mock_requests_get.return_value = geo_response
            
            tracker.get_slot.return_value = "NonExistentCity"
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "I couldn't find that location" in message
    
    # Test for ActionGetUVIndexForecast error handling
    def test_uv_forecast_no_data_handling(self):
        """Test handling of missing forecast data in ActionGetUVIndexForecast."""
        from actions.actions import ActionGetUVIndexForecast
        
        action = ActionGetUVIndexForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 33.44, "lon": -94.04}
            }
            
            # Mock UV forecast response with empty data
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = []
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "Miami" if name == "location" else 2
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check error message - use a more general assertion that will match
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text'].lower()
            assert "couldn't" in message and "uv forecast" in message
