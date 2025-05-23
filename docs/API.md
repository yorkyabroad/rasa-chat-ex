# API Documentation

## Custom Actions

### ActionFetchWeather

Fetches current weather information for a specified location.

**Slots Required:**
- `location`: The city or location to fetch weather for

**Returns:**
- Current temperature in Celsius
- Weather description

**Example Response:**
```
The current weather in London is cloudy with a temperature of 18°C.
```

### ActionFetchWeatherForecast

Fetches weather forecast for a specified location.

**Slots Required:**
- `location`: The city or location to fetch forecast for
- `days` (optional): Number of days to forecast (1-3, default: 3)

**Returns:**
- Daily forecasts including:
  - Date
  - Weather description
  - Temperature in Celsius

**Example Response:**
```
Weather forecast for London for the next 3 day(s):
• Monday, June 1: partly cloudy, temperature around 19°C
• Tuesday, June 2: sunny, temperature around 22°C
• Wednesday, June 3: light rain, temperature around 17°C
```

### ActionRandomFact

Provides a random interesting fact.

**Slots Required:**
- None

**Returns:**
- A random fact from the predefined list

**Example Response:**
```
Did you know honey never spoils?
```

### ActionCompareWeather

Compares current weather with historical or forecast data.

**Slots Required:**
- `location`: The city or location to compare weather for

**Returns:**
- Weather comparison data

## Error Responses

All actions may return the following error messages:

- "I couldn't find the location. Could you please provide it?"
  - When the location slot is missing
- "Weather service is currently unavailable."
  - When the API key is missing
- "I couldn't fetch the weather for that location. Try again."
  - When the API request fails
- "Sorry, I encountered an error while fetching the weather data."
  - When an unexpected error occurs

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| OPENWEATHER_API_KEY | OpenWeather API key | Yes | - |
| RASA_ENV | Environment (development/production) | No | development |
| LOG_LEVEL | Logging level | No | INFO |

## Rate Limits

- OpenWeather API: 60 calls/minute (free tier)
- Request timeout: 10 seconds

## Error Handling

All API calls include:
- Timeout handling
- Error logging
- User-friendly error messages
- Request exception handling