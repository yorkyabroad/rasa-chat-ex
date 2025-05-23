import unittest
from unittest.mock import patch, MagicMock
import datetime
import json
import requests
from actions.actions import (
    ActionRandomFact, ActionCompareWeather, ActionFetchWeather, 
    ActionFetchWeatherForecast, ActionGetLocalTime, ActionGetHumidity
)


class TestActionRandomFact(unittest.TestCase):
    def test_name(self):
        action = ActionRandomFact()
        self.assertEqual(action.name(), "action_random_fact")
    
    def test_run(self):
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        action = ActionRandomFact()
        action.run(dispatcher, tracker, domain)
        
        # Check that utter_message was called once
        dispatcher.utter_message.assert_called_once()
        
        # Check that the message contains one of the facts
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not."
        ]
        
        called_with = dispatcher.utter_message.call_args[1]['text']
        self.assertTrue(any(fact == called_with for fact in facts))


class TestActionCompareWeather(unittest.TestCase):
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    @patch('actions.actions.datetime')
    def test_run_with_location_warmer(self, mock_datetime, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the datetime to return a fixed month
        mock_datetime.datetime.now.return_value = MagicMock(month=7)  # July
        
        # Mock the API key
        mock_env_get.return_value = "fake_api_key"
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 28.5},  # Much warmer than average for July (22°C)
            "weather": [{"description": "sunny"}]
        }
        mock_requests_get.return_value = mock_response
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "London"
        domain = MagicMock()
        
        action = ActionCompareWeather()
        action.run(dispatcher, tracker, domain)
        
        # Check that the API was called with the right URL
        mock_requests_get.assert_called_once()
        self.assertIn("London", mock_requests_get.call_args[0][0])
        
        # Check that the message contains the expected comparison
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("28.5°C", message)
        self.assertIn("much warmer", message)


class TestActionFetchWeather(unittest.TestCase):
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the API key
        mock_env_get.return_value = "fake_api_key"
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 20.5},
            "weather": [{"description": "clear sky"}]
        }
        mock_requests_get.return_value = mock_response
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "Paris"
        domain = MagicMock()
        
        action = ActionFetchWeather()
        action.run(dispatcher, tracker, domain)
        
        # Check that the API was called with the right URL
        mock_requests_get.assert_called_once()
        self.assertIn("Paris", mock_requests_get.call_args[0][0])
        
        # Check that the message contains the expected weather info
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Paris", message)
        self.assertIn("20.5°C", message)
        self.assertIn("clear sky", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = None  # No location provided
        domain = MagicMock()
        
        action = ActionFetchWeather()
        action.run(dispatcher, tracker, domain)
        
        # Check that the appropriate message was sent
        dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )


class TestActionGetLocalTime(unittest.TestCase):
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    @patch('actions.actions.datetime')
    def test_run_with_location_timezone_api(self, mock_datetime, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the datetime
        mock_datetime.datetime.utcnow.return_value = datetime.datetime(2023, 6, 15, 12, 0, 0)
        
        # Mock the API keys
        def get_env_var(var_name):
            if var_name == "OPENWEATHER_API_KEY":
                return "fake_weather_key"
            elif var_name == "TIMEZONE_API_KEY":
                return "fake_timezone_key"
            return None
        
        mock_env_get.side_effect = get_env_var
        
        # Mock the first API response (OpenWeatherMap)
        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            "coord": {"lat": 51.5074, "lon": -0.1278},
            "timezone": 3600  # UTC+1
        }
        
        # Mock the second API response (TimeZoneDB)
        timezone_response = MagicMock()
        timezone_response.status_code = 200
        timezone_response.json.return_value = {
            "formatted": "2023-06-15 13:00:00",  # UTC+1
            "zoneName": "Europe/London"
        }
        
        # Set up the requests.get to return different responses
        mock_requests_get.side_effect = [weather_response, timezone_response]
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "London"
        domain = MagicMock()
        
        action = ActionGetLocalTime()
        action.run(dispatcher, tracker, domain)
        
        # Check that the APIs were called with the right URLs
        self.assertEqual(mock_requests_get.call_count, 2)
        self.assertIn("London", mock_requests_get.call_args_list[0][0][0])
        self.assertIn("lat=51.5074", mock_requests_get.call_args_list[1][0][0])
        self.assertIn("lng=-0.1278", mock_requests_get.call_args_list[1][0][0])
        
        # Check that the message contains the expected time info
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("Europe/London", message)
        self.assertIn("13:00", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location_fallback(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the API keys - only weather API key available
        def get_env_var(var_name):
            if var_name == "OPENWEATHER_API_KEY":
                return "fake_weather_key"
            return None
        
        mock_env_get.side_effect = get_env_var
        
        # Mock the API response
        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            "coord": {"lat": 51.5074, "lon": -0.1278},
            "timezone": 3600  # UTC+1
        }
        
        mock_requests_get.return_value = weather_response
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "London"
        domain = MagicMock()
        
        # Skip testing the exact time formatting and just check the message format
        action = ActionGetLocalTime()
        
        # Use a simpler approach to mocking
        with patch('actions.actions.datetime') as mock_datetime:
            # Create a mock datetime object that will be returned by utcnow()
            mock_utc_time = MagicMock()
            # Configure the mock to return a formatted time string
            mock_utc_time.strftime.return_value = "13:00"
            # Make utcnow return our mock
            mock_datetime.datetime.utcnow.return_value = mock_utc_time
            # Make timedelta return a real timedelta object
            mock_datetime.timedelta.return_value = datetime.timedelta(seconds=3600)
            # Make the + operator on our mock return the same mock
            mock_utc_time.__add__.return_value = mock_utc_time
            
            # Run the action
            action.run(dispatcher, tracker, domain)
        
        # Check that the API was called with the right URL
        mock_requests_get.assert_called_once()
        self.assertIn("London", mock_requests_get.call_args[0][0])
        
        # Check that the message contains the expected location and format
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("based on timezone offset", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = None  # No location provided
        domain = MagicMock()
        
        action = ActionGetLocalTime()
        action.run(dispatcher, tracker, domain)
        
        # Check that the appropriate message was sent
        dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )


class TestActionGetHumidity(unittest.TestCase):
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the API key
        mock_env_get.return_value = "fake_api_key"
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"humidity": 75}
        }
        mock_requests_get.return_value = mock_response
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "London"
        domain = MagicMock()
        
        action = ActionGetHumidity()
        action.run(dispatcher, tracker, domain)
        
        # Check that the API was called with the right URL
        mock_requests_get.assert_called_once()
        self.assertIn("London", mock_requests_get.call_args[0][0])
        
        # Check that the message contains the humidity info
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("London", message)
        self.assertIn("75%", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_run_without_location(self, mock_env_get, mock_load_dotenv):
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = None  # No location provided
        domain = MagicMock()
        
        action = ActionGetHumidity()
        action.run(dispatcher, tracker, domain)
        
        # Check that the appropriate message was sent
        dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )

if __name__ == '__main__':
    unittest.main()

class TestActionFetchWeatherForecast(unittest.TestCase):
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_run_with_location(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the API key
        mock_env_get.return_value = "fake_api_key"
        
        # Create a mock forecast response with data for 3 days
        forecast_data = {
            "list": [
                # Day 1 - noon forecast
                {
                    "dt": int(datetime.datetime(2023, 6, 15, 12, 0).timestamp()),
                    "main": {"temp": 22.5},
                    "weather": [{"description": "sunny"}]
                },
                # Day 2 - noon forecast
                {
                    "dt": int(datetime.datetime(2023, 6, 16, 12, 0).timestamp()),
                    "main": {"temp": 24.0},
                    "weather": [{"description": "partly cloudy"}]
                },
                # Day 3 - noon forecast
                {
                    "dt": int(datetime.datetime(2023, 6, 17, 12, 0).timestamp()),
                    "main": {"temp": 21.0},
                    "weather": [{"description": "light rain"}]
                }
            ]
        }
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = forecast_data
        mock_requests_get.return_value = mock_response
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.side_effect = lambda slot_name: "Paris" if slot_name == "location" else 3
        domain = MagicMock()
        
        action = ActionFetchWeatherForecast()
        action.run(dispatcher, tracker, domain)
        
        # Check that the API was called with the right URL
        mock_requests_get.assert_called_once()
        self.assertIn("Paris", mock_requests_get.call_args[0][0])
        
        # Check that the message contains forecast information
        dispatcher.utter_message.assert_called_once()
        message = dispatcher.utter_message.call_args[1]['text']
        self.assertIn("Paris", message)
        self.assertIn("3 day(s)", message)
        self.assertIn("sunny", message)
        self.assertIn("partly cloudy", message)
        self.assertIn("light rain", message)
    
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_api_error_handling(self, mock_requests_get, mock_env_get, mock_load_dotenv):
        # Mock the API key
        mock_env_get.return_value = "fake_api_key"
        
        # Mock the API to raise an exception
        mock_requests_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Set up the action
        dispatcher = MagicMock()
        tracker = MagicMock()
        tracker.get_slot.return_value = "Paris"
        domain = MagicMock()
        
        action = ActionFetchWeatherForecast()
        action.run(dispatcher, tracker, domain)
        
        # Check that the error message was sent
        dispatcher.utter_message.assert_called_once_with(
            text="Sorry, I encountered an error while fetching the weather forecast data."
        )