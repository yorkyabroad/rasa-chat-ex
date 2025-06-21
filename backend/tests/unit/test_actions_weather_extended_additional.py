import pytest
import datetime
from unittest.mock import MagicMock, patch
from actions.actions_weather_extended import (
    ActionGetSevereWeatherAlerts,
    ActionGetPrecipitation,
    ActionGetWindConditions,
    ActionGetSunriseSunset,
    ActionGetWeatherComparison
)

class TestActionGetSevereWeatherAlertsAdditional:
    def setup_method(self):
        self.action = ActionGetSevereWeatherAlerts()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_alerts_api_feature(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Test the special handling for the "alerts" feature in the API
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (40.7128, -74.0060)  # NYC coordinates
        
        # Create mock response with alerts data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "alerts": [
                {
                    "event": "Flood Warning",
                    "description": "Flooding caused by excessive rainfall is expected",
                    "sender_name": "NWS",
                    "start": 1609570800,  # Example timestamp
                    "end": 1609599600     # Example timestamp
                },
                {
                    "event": "Wind Advisory",
                    "description": "Strong winds expected with gusts up to 45 mph",
                    "sender_name": "NWS",
                    "start": 1609570800,  # Example timestamp
                    "end": 1609599600     # Example timestamp
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "New York"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that alerts were processed correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Weather alerts for New York" in call_args
        assert "ALERT 1: Flood Warning" in call_args
        assert "ALERT 2: Wind Advisory" in call_args
        assert "Issued by: NWS" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_location(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Test when location is missing
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_api_key(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Test when API key is missing
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "New York"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="Weather alert service is currently unavailable."
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_invalid_coordinates(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Test when coordinates cannot be found
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (None, None)
        self.tracker.get_slot.return_value = "NonExistentPlace"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't find that location. Please try again."
        )

class TestActionGetWindConditionsAdditional:
    def setup_method(self):
        self.action = ActionGetWindConditions()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_message_text_parsing(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Test the message text parsing for "tomorrow"
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (48.8566, 2.3522)  # Paris coordinates
        
        # Create mock response with tomorrow's date in the forecast
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{tomorrow} 12:00:00",
                    "wind": {
                        "speed": 5.5,
                        "deg": 90,
                        "gust": 8.2
                    }
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Set up tracker with "tomorrow" in the message text but not in the slot
        self.tracker.get_slot.side_effect = lambda slot: "Paris" if slot == "location" else "today"
        self.tracker.latest_message = {'text': 'What will the wind be like in Paris tomorrow?'}
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that "tomorrow" was detected in the message text
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Wind forecast for Paris tomorrow" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_location(self, mock_env_get, mock_requests_get):
        # Test when location is missing
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_api_key(self, mock_env_get, mock_requests_get):
        # Test when API key is missing
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "Paris"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="Weather service is currently unavailable."
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_invalid_time_period(self, mock_env_get, mock_requests_get):
        # Test with invalid time period
        mock_env_get.return_value = "fake_api_key"
        self.tracker.get_slot.side_effect = lambda slot: "Paris" if slot == "location" else "next week"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I can only provide wind conditions for today or tomorrow."
        )

class TestActionGetSunriseSunsetAdditional:
    def setup_method(self):
        self.action = ActionGetSunriseSunset()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_tomorrow_sunrise_sunset(self, mock_env_get, mock_requests_get):
        # Test getting tomorrow's sunrise/sunset
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock response for coordinates
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sys": {
                "sunrise": 1609570800,  # Example timestamp for sunrise
                "sunset": 1609599600    # Example timestamp for sunset
            },
            "timezone": 3600,  # UTC+1
            "coord": {
                "lat": 51.5074,
                "lon": -0.1278
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Set up tracker for tomorrow
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "tomorrow"
        # Use a message without "sunrise" or "sunset" keywords to get both
        self.tracker.latest_message = {'text': 'What are the daylight hours in London tomorrow?'}
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that tomorrow's sunrise/sunset was reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Sunrise and sunset times for London tomorrow" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_api_error(self, mock_env_get, mock_requests_get):
        # Test API error handling
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "NonExistentPlace" if slot == "location" else "today"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the error message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't fetch sunrise and sunset times for that location. Try again."
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_exception_handling(self, mock_env_get, mock_requests_get):
        # Test exception handling
        mock_env_get.return_value = "fake_api_key"
        mock_requests_get.side_effect = Exception("Test exception")
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the error message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="Sorry, I encountered an error while fetching sunrise and sunset data."
        )

class TestActionGetWeatherComparisonAdditional:
    def setup_method(self):
        self.action = ActionGetWeatherComparison()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_location(self, mock_env_get, mock_requests_get):
        # Test when location is missing
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_api_key(self, mock_env_get, mock_requests_get):
        # Test when API key is missing
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "London"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="Weather service is currently unavailable."
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_historical_api_error(self, mock_env_get, mock_requests_get):
        # Test when historical API returns an error
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock responses
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "main": {"temp": 20.0},
            "weather": [{"description": "clear sky"}],
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        hist_response = MagicMock()
        hist_response.status_code = 404
        
        # Set up the mock to return different responses for different URLs
        def mock_get_side_effect(url, timeout):
            if "onecall/timemachine" in url:
                return hist_response
            return current_response
            
        mock_requests_get.side_effect = mock_get_side_effect
        
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that only current weather was reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "I could only get today's weather for London" in call_args