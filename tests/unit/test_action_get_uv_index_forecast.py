# tests/test_action_get_uv_index_forecast.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import ActionGetUVIndexForecast

class TestActionGetUVIndexForecast:
    """Tests for the ActionGetUVIndexForecast class."""
    
    def test_uv_index_forecast_success(self):
        """Test successful UV index forecast retrieval."""
        action = ActionGetUVIndexForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get, \
             patch('actions.actions.datetime') as mock_datetime:
            
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
            
            # Mock UV forecast response
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = [
                {
                    "date": int(datetime.datetime.now().timestamp()),  # Today
                    "value": 2.5
                },
                {
                    "date": tomorrow_timestamp,  # Tomorrow
                    "value": 4.5
                }
            ]
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 1
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "UV index" in message
            assert "London" in message
            assert "tomorrow" in message
            assert "4.5" in message
            assert "Moderate" in message  # UV 4.5 = Moderate
    
    def test_uv_index_forecast_no_data(self):
        """Test handling of missing forecast data."""
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
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock empty UV forecast response
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = []
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 1
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't get the uv forecast for" in message.lower()
    
    def test_uv_index_forecast_api_error(self):
        """Test error handling when UV forecast API fails."""
        action = ActionGetUVIndexForecast()
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
            
            # Mock UV forecast API error
            uv_response = MagicMock(status_code=500)
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 1
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check error message
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "couldn't fetch the uv index forecast for that location" in message.lower()
    
    def test_uv_index_forecast_days_parameter(self):
        """Test handling of different days parameter values."""
        action = ActionGetUVIndexForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Test cases for days parameter
        test_cases = [
            ("2", 2),  # String digit
            ("invalid", 1),  # Invalid string defaults to 1
            (3, 3),  # Integer within range
            (10, 5)  # Integer exceeding max (should be capped at 5)
        ]
        
        for days_input, expected_days in test_cases:
            # Reset mocks
            dispatcher.reset_mock()
            
            with patch('actions.actions.load_dotenv'), \
                 patch('actions.actions.os.environ.get') as mock_env_get, \
                 patch('actions.actions.requests.get') as mock_requests_get:
                
                mock_env_get.return_value = "fake_api_key"
                
                # Mock geo response
                geo_response = MagicMock(status_code=200)
                geo_response.json.return_value = {
                    "coord": {"lat": 51.5074, "lon": -0.1278}
                }
                
                # Create forecast data for multiple days
                uv_data = []
                now = datetime.datetime.now()
                for i in range(expected_days + 1):  # +1 because we need today plus forecast days
                    day = now + datetime.timedelta(days=i)
                    uv_data.append({
                        "date": int(day.timestamp()),
                        "value": 2.0 + i  # Different UV values for each day
                    })
                
                # Mock UV forecast response
                uv_response = MagicMock(status_code=200)
                uv_response.json.return_value = uv_data
                
                # Set up the side effect to return different responses
                mock_requests_get.side_effect = [geo_response, uv_response]
                
                # Set up tracker with the current test case days value
                tracker.get_slot.side_effect = lambda name: "London" if name == "location" else days_input
                
                # Run the action
                action.run(dispatcher, tracker, domain)
                
                # Check that the message was sent
                dispatcher.utter_message.assert_called_once()
                message = dispatcher.utter_message.call_args[1]['text']
                
                # For days=1, we expect "tomorrow", otherwise "in X days"
                if expected_days == 1:
                    assert "tomorrow" in message.lower()
                else:
                    assert f"in {expected_days} days" in message.lower()