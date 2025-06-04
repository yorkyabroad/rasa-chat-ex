import pytest
from unittest.mock import patch, MagicMock
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.actions_weather_extended import (
    ActionGetSevereWeatherAlerts,
    ActionGetPrecipitation,
    ActionGetWindConditions,
    ActionGetSunriseSunset,
    ActionGetWeatherComparison
)

class TestActionsWeatherExtended:
    
    @pytest.fixture
    def dispatcher(self):
        return MagicMock(spec=CollectingDispatcher)
    
    @pytest.fixture
    def tracker(self):
        tracker = MagicMock(spec=Tracker)
        tracker.get_slot.return_value = "London"
        return tracker
    
    @pytest.fixture
    def domain(self):
        return {}
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_severe_weather_alerts_no_alerts(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Mock response with no alerts
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "alerts": []
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSevereWeatherAlerts()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "no weather alerts" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_precipitation(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Mock response with precipitation data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "hourly": [
                {"dt": 1609459200, "temp": 5, "pop": 0.5},
                {"dt": 1609462800, "temp": 6, "pop": 0.7, "rain": {"1h": 1.2}}
            ],
            "daily": [
                {"dt": 1609459200, "temp": {"day": 5}, "pop": 0.2},
                {"dt": 1609545600, "temp": {"day": 6}, "pop": 0.6, "rain": 2.5}
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetPrecipitation()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "precipitation forecast" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_wind_conditions(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response with wind data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "wind": {
                "speed": 5.2,
                "deg": 180
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetWindConditions()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "wind conditions" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_sunrise_sunset(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response with sunrise/sunset data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "sys": {
                "sunrise": 1609484400,  # Example timestamp
                "sunset": 1609513200    # Example timestamp
            },
            "timezone": 0
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSunriseSunset()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "sunrise and sunset" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_weather_comparison(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for current weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "name": "London",
            "main": {"temp": 10.5},
            "weather": [{"description": "cloudy"}],
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock response for historical weather
        hist_response = MagicMock()
        hist_response.status_code = 200
        hist_response.json.return_value = {
            "data": [
                {
                    "temp": 8.5,
                    "weather": [{"description": "rainy"}]
                }
            ]
        }
        
        # Configure mock to return different responses
        mock_requests_get.side_effect = [current_response, hist_response]
        
        # Execute action
        action = ActionGetWeatherComparison()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "weather comparison" in dispatcher.utter_message.call_args[1]['text'].lower()