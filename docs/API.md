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
  - UV index with risk level (Low, Moderate, High, Very High, Extreme)

**Example Response:**
```
Weather forecast for London for the next 3 day(s):
• Monday, June 1: partly cloudy, temperature around 19°C, UV index: 4.2 (Moderate)
• Tuesday, June 2: sunny, temperature around 22°C, UV index: 6.8 (High)
• Wednesday, June 3: light rain, temperature around 17°C, UV index: 3.5 (Moderate)
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

### ActionGetUVIndex

Fetches current UV index information for a specified location.

**Slots Required:**
- `location`: The city or location to fetch UV index for

**Returns:**
- Current UV index value
- UV risk level (Low, Moderate, High, Very High, Extreme)
- Protection recommendations based on UV level

**Example Response:**
```
The current UV index in Miami is 7.5 (High).
Wear sunscreen SPF 30+, protective clothing, a hat, and sunglasses. Reduce time in the sun between 10 AM and 4 PM.
```

### ActionGetUVIndexForecast

Fetches UV index forecast for a specified location.

**Slots Required:**
- `location`: The city or location to fetch UV forecast for
- `days` (optional): Number of days ahead to forecast (1-5, default: 1)

**Returns:**
- Forecast UV index value
- UV risk level (Low, Moderate, High, Very High, Extreme)
- Protection recommendations based on UV level

**Example Response:**
```
The UV index in Miami tomorrow (Tuesday, July 11) is forecast to be 9.5 (Very High).
Wear SPF 30+ sunscreen, protective clothing, a wide-brim hat, and UV-blocking sunglasses. Try to avoid sun exposure between 10 AM and 4 PM.
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