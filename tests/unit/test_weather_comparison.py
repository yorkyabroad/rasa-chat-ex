import pytest
from unittest.mock import MagicMock, patch
from actions.actions_weather_extended import ActionGetWeatherComparison

class TestActionGetWeatherComparison:
    def setup_method(self):
        self.action = ActionGetWeatherComparison()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_weather_comparison_warmer(self, mock_env_get, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock responses for current and historical weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "main": {
                "temp": 25.0  # 25°C today
            },
            "weather": [
                {"description": "clear sky"}
            ],
            "coord": {
                "lat": 51.5074,
                "lon": -0.1278
            }
        }
        
        hist_response = MagicMock()
        hist_response.status_code = 200
        hist_response.json.return_value = {
            "data": [
                {
                    "temp": 20.0,  # 20°C yesterday (5°C cooler)
                    "weather": [
                        {"description": "cloudy"}
                    ]
                }
            ]
        }
        
        # Set up the mock to return different responses for different URLs
        def mock_get_side_effect(url, timeout):
            if "onecall/timemachine" in url:
                return hist_response
            return current_response
            
        mock_requests_get.side_effect = mock_get_side_effect
        
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the comparison was reported correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Weather comparison for London" in call_args
        assert "Today: clear sky, 25.0°C" in call_args
        assert "Yesterday: cloudy, 20.0°C" in call_args
        assert "Today is 5.0°C warmer than yesterday" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_weather_comparison_cooler(self, mock_env_get, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock responses for current and historical weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "main": {
                "temp": 15.0  # 15°C today
            },
            "weather": [
                {"description": "light rain"}
            ],
            "coord": {
                "lat": 51.5074,
                "lon": -0.1278
            }
        }
        
        hist_response = MagicMock()
        hist_response.status_code = 200
        hist_response.json.return_value = {
            "data": [
                {
                    "temp": 22.0,  # 22°C yesterday (7°C warmer)
                    "weather": [
                        {"description": "sunny"}
                    ]
                }
            ]
        }
        
        # Set up the mock to return different responses for different URLs
        def mock_get_side_effect(url, timeout):
            if "onecall/timemachine" in url:
                return hist_response
            return current_response
            
        mock_requests_get.side_effect = mock_get_side_effect
        
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the comparison was reported correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Weather comparison for London" in call_args
        assert "Today: light rain, 15.0°C" in call_args
        assert "Yesterday: sunny, 22.0°C" in call_args
        assert "Today is 7.0°C cooler than yesterday" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_weather_comparison_same(self, mock_env_get, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock responses for current and historical weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "main": {
                "temp": 18.5  # 18.5°C today
            },
            "weather": [
                {"description": "partly cloudy"}
            ],
            "coord": {
                "lat": 51.5074,
                "lon": -0.1278
            }
        }
        
        hist_response = MagicMock()
        hist_response.status_code = 200
        hist_response.json.return_value = {
            "data": [
                {
                    "temp": 18.0,  # 18°C yesterday (0.5°C difference, considered "same")
                    "weather": [
                        {"description": "partly cloudy"}
                    ]
                }
            ]
        }
        
        # Set up the mock to return different responses for different URLs
        def mock_get_side_effect(url, timeout):
            if "onecall/timemachine" in url:
                return hist_response
            return current_response
            
        mock_requests_get.side_effect = mock_get_side_effect
        
        self.tracker.get_slot.return_value = "London"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the comparison was reported correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Weather comparison for London" in call_args
        assert "Today: partly cloudy, 18.5°C" in call_args
        assert "Yesterday: partly cloudy, 18.0°C" in call_args
        assert "Today is about the same temperature as yesterday" in call_args