# tests/test_action_fetch_weather_forecast.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import ActionFetchWeatherForecast

class TestActionFetchWeatherForecast:
    """Tests for the ActionFetchWeatherForecast class."""
    
    def test_today_forecast_with_uv_data(self):
        """Test forecast for today with UV data."""
        action = ActionFetchWeatherForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get, \
             patch('actions.actions.datetime') as mock_datetime:
            
            # Set up datetime mock
            today = datetime.datetime(2023, 6, 15, 12, 0, 0)
            mock_datetime.datetime.now.return_value = today
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock forecast response
            today_timestamp = int(today.timestamp())
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": today_timestamp,
                        "main": {"temp": 22.5},
                        "weather": [{"description": "clear sky"}]
                    }
                ]
            }
            
            # Mock UV response
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = [
                {
                    "date": today_timestamp,
                    "value": 5.2
                }
            ]
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 1
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "Weather forecast for London" in message
            assert "Today" in message
            assert "clear sky" in message
            assert "22.5°C" in message
            assert "UV index: 5.2" in message
            assert "Moderate" in message  # UV 5.2 = Moderate
    
    def test_forecast_without_uv_data(self):
        """Test forecast without UV data."""
        action = ActionFetchWeatherForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get, \
             patch('actions.actions.datetime') as mock_datetime:
            
            # Set up datetime mock
            today = datetime.datetime(2023, 6, 15, 12, 0, 0)
            tomorrow = today + datetime.timedelta(days=1)
            mock_datetime.datetime.now.return_value = today
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
            mock_datetime.timedelta.side_effect = datetime.timedelta
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock forecast response with today and tomorrow
            today_timestamp = int(today.timestamp())
            tomorrow_timestamp = int(tomorrow.timestamp())
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": today_timestamp,
                        "main": {"temp": 22.5},
                        "weather": [{"description": "clear sky"}]
                    },
                    {
                        "dt": tomorrow_timestamp,
                        "main": {"temp": 24.0},
                        "weather": [{"description": "scattered clouds"}]
                    }
                ]
            }
            
            # Mock UV response with error
            uv_response = MagicMock(status_code=404)
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 2
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            assert "Weather forecast for London" in message
            assert "Today" in message
            assert "clear sky" in message
            assert "22.5°C" in message
            assert "scattered clouds" in message
            assert "24.0°C" in message
            assert "UV index" not in message  # No UV data should be included
    
    def test_days_parameter_handling(self):
        """Test handling of days parameter."""
        action = ActionFetchWeatherForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Test cases for days parameter
        test_cases = [
            ("2", 2),  # String digit
            ("invalid", 3),  # Invalid string defaults to 3
            (3, 3),  # Integer within range
            (10, 3)  # Integer exceeding max (should be capped at 3)
        ]
        
        for days_input, expected_days in test_cases:
            # Reset mocks
            dispatcher.reset_mock()
            
            with patch('actions.actions.load_dotenv'), \
                 patch('actions.actions.os.environ.get') as mock_env_get, \
                 patch('actions.actions.requests.get') as mock_requests_get, \
                 patch('actions.actions.datetime') as mock_datetime:
                
                # Set up datetime mock
                today = datetime.datetime(2023, 6, 15, 12, 0, 0)
                mock_datetime.datetime.now.return_value = today
                mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
                mock_datetime.timedelta.side_effect = datetime.timedelta
                
                mock_env_get.return_value = "fake_api_key"
                
                # Mock geo response
                geo_response = MagicMock(status_code=200)
                geo_response.json.return_value = {
                    "coord": {"lat": 51.5074, "lon": -0.1278}
                }
                
                # Create forecast data for multiple days
                forecast_list = []
                for i in range(expected_days):
                    day = today + datetime.timedelta(days=i)
                    forecast_list.append({
                        "dt": int(day.timestamp()),
                        "main": {"temp": 20.0 + i},
                        "weather": [{"description": f"day {i} weather"}]
                    })
                
                # Mock forecast response
                forecast_response = MagicMock(status_code=200)
                forecast_response.json.return_value = {"list": forecast_list}
                
                # Mock UV response
                uv_response = MagicMock(status_code=200)
                uv_response.json.return_value = []
                
                # Set up the side effect to return different responses
                mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
                
                # Set up tracker with the current test case days value
                tracker.get_slot.side_effect = lambda name: "London" if name == "location" else days_input
                
                # Run the action
                action.run(dispatcher, tracker, domain)
                
                # Check that the message was sent with correct number of days
                dispatcher.utter_message.assert_called_once()
                message = dispatcher.utter_message.call_args[1]['text']
                assert f"Weather forecast for London for the next {expected_days} day(s)" in message