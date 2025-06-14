# tests/test_temperature_range.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import ActionGetTemperatureRange

class TestActionGetTemperatureRange:
    """Tests for the ActionGetTemperatureRange class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetTemperatureRange()
    
    def test_name(self):
        """Test the action name."""
        assert self.action.name() == "action_get_temperature_range"
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_without_location(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test handling of missing location."""
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_api_key(self, mock_env_get, mock_load_dotenv):
        """Test handling of missing API key."""
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="Weather service is currently unavailable."
        )
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_today_range(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test temperature range for today."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for today's weather
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {
                "temp": 22.5,
                "temp_min": 18.0,
                "temp_max": 25.0
            }
        }
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "range"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the response
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "London" in message
        assert "today" in message
        assert "18.0°C and 25.0°C" in message
        assert "Currently it's 22.5°C" in message
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_today_min(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test minimum temperature for today."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for today's weather
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {
                "temp": 22.5,
                "temp_min": 18.0,
                "temp_max": 25.0
            }
        }
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "min"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the response
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "London" in message
        assert "minimum temperature" in message
        assert "18.0°C" in message
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_today_max(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test maximum temperature for today."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for today's weather
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {
                "temp": 22.5,
                "temp_min": 18.0,
                "temp_max": 25.0
            }
        }
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "max"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the response
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "London" in message
        assert "maximum temperature" in message
        assert "25.0°C" in message
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    @patch('actions.actions.datetime')
    def test_run_tomorrow_range(self, mock_datetime, mock_get, mock_env_get, mock_load_dotenv):
        """Test temperature range for tomorrow."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock current date
        today = datetime.datetime(2023, 7, 15)
        tomorrow = datetime.datetime(2023, 7, 16)
        mock_datetime.datetime.now.return_value = today
        mock_datetime.datetime.fromtimestamp.side_effect = lambda ts: datetime.datetime.fromtimestamp(ts)
        mock_datetime.timedelta.side_effect = datetime.timedelta
        
        # Mock response for tomorrow's forecast
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "list": [
                {
                    "dt": int(tomorrow.timestamp()),
                    "main": {
                        "temp_min": 17.0,
                        "temp_max": 24.0
                    }
                },
                {
                    "dt": int(tomorrow.timestamp()) + 3600 * 3,
                    "main": {
                        "temp_min": 16.0,
                        "temp_max": 26.0
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "Paris",
            "time_period": "tomorrow",
            "temp_type": "range"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the response
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "Paris" in message
        assert "tomorrow" in message
        assert "16.0°C and 26.0°C" in message
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "range"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "Sorry" in message
        assert "error" in message.lower()
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error_status(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test handling of API error status codes."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock error response
        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "NonExistentCity",
            "time_period": "today",
            "temp_type": "range"
        }.get(name)
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "couldn't fetch" in message.lower()
