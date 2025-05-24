"""Unit tests for Rasa custom actions that handle weather, time, and random facts."""

import unittest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import (
    ActionRandomFact, ActionCompareWeather, ActionFetchWeather, 
    ActionFetchWeatherForecast, ActionGetLocalTime, ActionGetHumidity,
    ActionGetUVIndex
)

# Test data constants
FORECAST_RESPONSE = {
    "list": [
        {
            "dt_txt": "2024-01-01 12:00:00",
            "main": {"temp": 22.5},
            "weather": [{"description": "sunny"}]
        },
        {
            "dt_txt": "2024-01-01 15:00:00",
            "main": {"temp": 24.0},
            "weather": [{"description": "partly cloudy"}]
        }
    ]
}
WEATHER_RESPONSE = {
    "main": {"temp": 20.5},
    "weather": [{"description": "clear sky"}]
}

TIMEZONE_RESPONSE = {
    "coord": {"lat": 51.5074, "lon": -0.1278},
    "timezone": 3600
}

UV_RESPONSE = {
    "value": 5.2,
    "date_iso": "2024-01-01T12:00:00Z",
    "date": 1704110400
}

class TestActionRandomFact(unittest.TestCase):
    """Tests for random fact generation action."""
    
    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionRandomFact()

    def test_name(self):
        """Verify action name is correct."""
        self.assertEqual(self.action.name(), "action_random_fact")
    
    def test_run(self):
        """Verify random fact is selected and returned."""
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not."
        ]
        called_with = self.dispatcher.utter_message.call_args[1]['text']
        self.assertTrue(any(fact == called_with for fact in facts))

class TestActionCompareWeather(unittest.TestCase):
    """Tests for weather comparison action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionCompareWeather()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    @patch('actions.actions.datetime')
    def test_run_with_location_warmer(self, mock_datetime, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test weather comparison when temperature is warmer than average."""
        mock_datetime.datetime.now.return_value = MagicMock(month=7)
        mock_env_get.return_value = "fake_api_key"
        
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {"temp": 28.5},
            "weather": [{"description": "sunny"}]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        mock_requests_get.assert_called_once()
        self.assertIn("London", mock_requests_get.call_args[0][0])
        
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("28.5°C", message)
        self.assertIn("much warmer", message)

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.tracker.get_slot.return_value = "London"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        self.assertIn("sorry", self.dispatcher.utter_message.call_args[1]['text'].lower())

class TestActionFetchWeather(unittest.TestCase):
    """Tests for weather fetching action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionFetchWeather()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test successful weather fetch for a location."""
        mock_env_get.return_value = "fake_api_key"
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = WEATHER_RESPONSE
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "Paris"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        mock_requests_get.assert_called_once()
        self.assertIn("Paris", mock_requests_get.call_args[0][0])
        
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Paris", message)
        self.assertIn("20.5°C", message)
        self.assertIn("clear sky", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        """Test handling of missing location."""
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )

class TestActionGetLocalTime(unittest.TestCase):
    """Tests for local time fetching action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetLocalTime()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    @patch('actions.actions.datetime')
    def test_run_with_location_timezone_api(self, mock_datetime, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test successful timezone fetch using timezone API."""
        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2023, 6, 15, 12, 0, 0)
        
        def get_env_var(var_name):
            return "fake_key" if var_name in ["OPENWEATHER_API_KEY", "TIMEZONE_API_KEY"] else None
        mock_env_get.side_effect = get_env_var
        
        weather_response = MagicMock(status_code=200)
        weather_response.json.return_value = TIMEZONE_RESPONSE
        
        timezone_response = MagicMock(status_code=200)
        timezone_response.json.return_value = {
            "formatted": "2023-06-15 13:00:00",
            "zoneName": "Europe/London"
        }
        
        mock_requests_get.side_effect = [weather_response, timezone_response]
        self.tracker.get_slot.return_value = "London"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertEqual(mock_requests_get.call_count, 2)
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("Europe/London", message)
        self.assertIn("13:00", message)

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.tracker.get_slot.return_value = "London"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        self.assertIn("sorry", self.dispatcher.utter_message.call_args[1]['text'].lower())

class TestActionFetchWeatherForecast(unittest.TestCase):
    """Tests for weather forecast fetching action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionFetchWeatherForecast()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location_and_uv_index(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test successful forecast fetch with UV index for a location."""
        
        mock_env_get.return_value = "fake_api_key"
        
        # Mock geo response for coordinates
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 35.6895, "lon": 139.6917}
        }
        
        # Mock forecast response
        forecast_response = MagicMock(status_code=200)
        forecast_response.json.return_value = {
            "list": [
                {
                    "dt": 1704110400,  # 2024-01-01 12:00:00
                    "dt_txt": "2024-01-01 12:00:00",
                    "main": {"temp": 22.5},
                    "weather": [{"description": "sunny"}]
                },
                {
                    "dt": 1704121200,  # 2024-01-01 15:00:00
                    "dt_txt": "2024-01-01 15:00:00",
                    "main": {"temp": 24.0},
                    "weather": [{"description": "partly cloudy"}]
                }
            ]
        }
        
        # Mock UV index response
        uv_response = MagicMock(status_code=200)
        uv_response.json.return_value = [
            {
                "date": 1704110400,  # 2024-01-01
                "value": 6.5
            }
        ]
        
        # Set up the side effect to return different responses for different calls
        mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
        
        self.tracker.get_slot.return_value = "Tokyo"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that all three API calls were made
        self.assertEqual(mock_requests_get.call_count, 3)
        
        # Check the message content
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Tokyo", message)
        self.assertIn("22.5°C", message)
        self.assertIn("sunny", message)
        self.assertIn("January 01", message)
        self.assertIn("UV index: 6.5", message)
        self.assertIn("High", message)  # UV level
        
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location_without_uv_data(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test forecast fetch when UV data is unavailable."""
        
        mock_env_get.return_value = "fake_api_key"
        
        # Mock geo response for coordinates
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 35.6895, "lon": 139.6917}
        }
        
        # Mock forecast response
        forecast_response = MagicMock(status_code=200)
        forecast_response.json.return_value = {
            "list": [
                {
                    "dt": 1704110400,  # 2024-01-01 12:00:00
                    "dt_txt": "2024-01-01 12:00:00",
                    "main": {"temp": 22.5},
                    "weather": [{"description": "sunny"}]
                }
            ]
        }
        
        # Mock UV index response with error
        uv_response = MagicMock(status_code=404)
        
        # Set up the side effect to return different responses for different calls
        mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
        
        self.tracker.get_slot.return_value = "Tokyo"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that all three API calls were made
        self.assertEqual(mock_requests_get.call_count, 3)
        
        # Check the message content - should have forecast but no UV index
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Tokyo", message)
        self.assertIn("22.5°C", message)
        self.assertIn("sunny", message)
        self.assertNotIn("UV index", message)

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_api_key(self, mock_env_get, mock_load_dotenv):
        """Test handling of missing API key."""
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "Tokyo"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="Weather forecast service is currently unavailable."
        )

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        """Test handling of missing location."""
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.tracker.get_slot.return_value = "Tokyo"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        self.assertIn("sorry", self.dispatcher.utter_message.call_args[1]['text'].lower())


class TestActionGetHumidity(unittest.TestCase):
    """Tests for humidity fetching action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetHumidity()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test successful humidity fetch for a location."""
        mock_env_get.return_value = "fake_api_key"
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {"humidity": 65}
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "Berlin"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        mock_requests_get.assert_called_once()
        self.assertIn("Berlin", mock_requests_get.call_args[0][0])
        
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Berlin", message)
        self.assertIn("65%", message)

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        """Test handling of missing location."""
        self.tracker.get_slot.return_value = None
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.tracker.get_slot.return_value = "Berlin"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        self.assertIn("sorry", self.dispatcher.utter_message.call_args[1]['text'].lower())


class TestActionGetUVIndex(unittest.TestCase):
    """Tests for UV index fetching action."""

    def setUp(self):
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetUVIndex()

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test successful UV index fetch for a location."""
        mock_env_get.return_value = "fake_api_key"
        
        # Mock geo response for coordinates
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 33.44, "lon": -94.04}
        }
        
        # Mock UV index response
        uv_response = MagicMock(status_code=200)
        uv_response.json.return_value = {
            "value": 7.5
        }
        
        # Set up the side effect to return different responses for different calls
        mock_requests_get.side_effect = [geo_response, uv_response]
        
        self.tracker.get_slot.return_value = "Miami"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that both API calls were made
        self.assertEqual(mock_requests_get.call_count, 2)
        
        # Check the message content
        message = self.dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Miami", message)
        self.assertIn("7.5", message)
        self.assertIn("High", message)  # UV level
        self.assertIn("Reduce time in the sun", message)  # Protection advice

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_uv_level_categorization(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test UV index level categorization."""
        mock_env_get.return_value = "fake_api_key"
        
        # Test different UV levels
        uv_test_cases = [
            {"value": 2.0, "expected_level": "Low", "expected_advice": "No protection required"},
            {"value": 4.5, "expected_level": "Moderate", "expected_advice": "Wear sunscreen"},
            {"value": 7.0, "expected_level": "High", "expected_advice": "SPF 30+"},
            {"value": 9.5, "expected_level": "Very High", "expected_advice": "avoid sun exposure"},
            {"value": 11.5, "expected_level": "Extreme", "expected_advice": "Take all precautions"}
        ]
        
        for test_case in uv_test_cases:
            # Reset mocks
            mock_requests_get.reset_mock()
            self.dispatcher.reset_mock()
            
            # Mock geo response for coordinates
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 33.44, "lon": -94.04}
            }
            
            # Mock UV index response with test value
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = {
                "value": test_case["value"]
            }
            
            # Set up the side effect
            mock_requests_get.side_effect = [geo_response, uv_response]
            
            self.tracker.get_slot.return_value = "TestCity"
            self.action.run(self.dispatcher, self.tracker, self.domain)
            
            # Check the message content for expected level and advice
            message = self.dispatcher.utter_message.call_args[1]['text']
            self.assertIn(f"{test_case['value']:.1f}", message)
            self.assertIn(test_case["expected_level"], message)
            self.assertIn(test_case["expected_advice"], message)

    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        """Test handling of API errors."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.tracker.get_slot.return_value = "Miami"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        self.dispatcher.utter_message.assert_called_once()
        self.assertIn("sorry", self.dispatcher.utter_message.call_args[1]['text'].lower())