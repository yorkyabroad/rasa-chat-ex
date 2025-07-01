import pytest
from unittest.mock import MagicMock, patch
from actions.actions_weather_extended import ActionGetPrecipitation


class TestPrecipitationTomorrow:
    """Test precipitation action with tomorrow time period."""
    
    def setup_method(self):
        self.action = ActionGetPrecipitation()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    def test_tomorrow_entity_extraction(self):
        """Test that tomorrow is properly extracted from slots."""
        # Mock tracker with tomorrow time period
        self.tracker.get_slot.side_effect = lambda slot: {
            "location": "Stockholm",
            "time_period": "tomorrow"
        }.get(slot)
        
        # Mock latest_message for debugging
        self.tracker.latest_message = {
            "text": "will it rain in Stockholm tomorrow?",
            "entities": [
                {"entity": "location", "value": "Stockholm"},
                {"entity": "time_period", "value": "tomorrow"}
            ]
        }
        
        with patch('actions.actions_weather_extended.load_dotenv'), \
             patch('actions.actions_weather_extended.os.environ.get') as mock_env, \
             patch('actions.actions_weather_extended.get_coordinates') as mock_coords, \
             patch('actions.actions_weather_extended.requests.get') as mock_get:
            
            mock_env.return_value = "test_api_key"
            mock_coords.return_value = (59.3293, 18.0686)  # Stockholm coordinates
            
            # Mock forecast response with tomorrow's data
            from datetime import datetime, timedelta
            tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "list": [
                    {
                        "dt_txt": f"{tomorrow_date} 12:00:00",  # Tomorrow at noon
                        "pop": 0.8,
                        "rain": {"3h": 2.5}
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            # Run action
            self.action.run(self.dispatcher, self.tracker, self.domain)
            
            # Check that message mentions tomorrow
            call_args = self.dispatcher.utter_message.call_args
            message = call_args[1]['text'] if call_args else ""
            
            print(f"Generated message: {message}")
            assert "tomorrow" in message.lower()
            assert "2.5" in message  # Expected rainfall amount
    
    def test_time_period_slot_debugging(self):
        """Debug what's in the time_period slot."""
        test_cases = [
            ("will it rain in Stockholm tomorrow?", "tomorrow"),
            ("what's the chance of rain in London tomorrow?", "tomorrow"),
            ("will it rain today?", "today"),
        ]
        
        for query, expected_period in test_cases:
            print(f"\nTesting query: '{query}'")
            print(f"Expected time_period: '{expected_period}'")
            
            # This would normally be set by NLU
            self.tracker.get_slot.side_effect = lambda slot: {
                "location": "Stockholm" if "Stockholm" in query else "London",
                "time_period": expected_period
            }.get(slot)
            
            location = self.tracker.get_slot("location")
            time_period = self.tracker.get_slot("time_period")
            
            print(f"Extracted location: '{location}'")
            print(f"Extracted time_period: '{time_period}'")
            
            assert location in ["Stockholm", "London"]
            assert time_period == expected_period