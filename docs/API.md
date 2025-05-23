# API Documentation

## Custom Actions

### WeatherAction

This custom action retrieves weather information based on user queries.

#### Input Parameters
- `location`: The city or location to get weather for
- `time`: (Optional) Specific time for weather forecast

#### Response Format
```python
{
    "temperature": float,
    "condition": str,
    "humidity": int,
    "wind_speed": float
}
```

#### Usage Example
```python
from actions.actions import WeatherAction

action = WeatherAction()
dispatcher = Dispatcher()
tracker = Tracker()
domain = Domain()

await action.run(dispatcher, tracker, domain)
```

### Environment Variables

Required environment variables for the weather API:
```
WEATHER_API_KEY=your_api_key
WEATHER_API_URL=https://api.weather.com/v1
```

## Conversation Flow

### Intents
- `ask_weather`: User asks for weather information
- `provide_location`: User provides a location
- `confirm`: User confirms an action
- `deny`: User denies an action

### Entities
- `location`: Geographic location
- `time`: Time reference
- `weather_attribute`: Specific weather attribute (temperature, humidity, etc.)

### Slots
- `requested_location`: Stores the location for weather query
- `weather_attribute`: Stores specific weather information requested

## Error Handling

The API implements the following error handling:
1. Invalid location handling
2. API timeout management
3. Missing data fallbacks

## Rate Limiting

- Weather API calls are rate-limited to 60 requests per minute
- Caching is implemented for frequent location queries

## Testing

### Unit Tests
```bash
python -m pytest tests/test_actions.py
```

### Integration Tests
```bash
python -m pytest tests/test_stories.yml
```

## Webhook Integration

For external service integration, the following webhook endpoint is available:
```
POST /webhooks/weather
Content-Type: application/json

{
    "location": "string",
    "attributes": ["temperature", "humidity"]
}
```