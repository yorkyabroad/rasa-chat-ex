import unittest
from unittest.mock import patch, MagicMock
import datetime
import json
from actions.actions import ActionRandomFact, ActionCompareWeather, ActionFetchWeather


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


if __name__ == '__main__':
    unittest.main()