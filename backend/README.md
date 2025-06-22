# Weather Chatbot Backend

Rasa-powered chatbot backend that provides comprehensive weather information using the OpenWeather API. This backend serves the React frontend through REST API endpoints.

## Features

### Core Weather Services
- Current weather conditions for any location
- Weather forecasts (up to 3 days)
- Temperature ranges, minimums, and maximums
- Humidity and precipitation details
- Wind conditions with speed, direction, and recommendations
- Sunrise and sunset times

### Advanced Weather Features
- UV index information and safety recommendations
- UV index forecasts for future days
- Air pollution data and health recommendations
- Air pollution forecasts for tomorrow
- Severe weather alerts and warnings
- Weather comparisons (today vs. yesterday, historical averages)
- Local time for any location worldwide

## Prerequisites

- Python 3.8+
- Rasa 3.6+
- OpenWeather API key

## Installation

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
```
Add your OpenWeather API key to `.env`:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## Usage

### Training and Running

1. **Train the model:**
```bash
rasa train
```

2. **Start the action server:**
```bash
rasa run actions
```

3. **Start the Rasa server:**
```bash
# For frontend integration
rasa run --enable-api --cors "*" --port 5005

# For command line testing
rasa shell
```

## API Endpoints

The backend provides REST API endpoints for the frontend:

- **POST** `/webhooks/rest/webhook` - Main chat endpoint
- **GET** `/` - Health check endpoint

### Example API Usage

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user", "message": "What is the weather in London?"}'
```

## Development

### Project Structure

```
backend/
├── actions/                    # Custom weather actions
│   ├── actions.py             # Core weather actions
│   ├── actions_weather_extended.py  # Extended features
│   ├── actions_air_pollution.py     # Air quality actions
│   ├── actions_air_pollution_forecast.py  # Air quality forecasts
│   ├── weather_utils.py       # Utility functions
│   └── validate_env.py        # Environment validation
├── data/                      # Training data
│   ├── nlu.yml               # Natural language understanding
│   ├── rules.yml             # Conversation rules
│   └── stories.yml           # Training stories
├── docs/                     # Documentation
├── tests/                    # Unit and E2E tests
│   ├── unit/                 # Unit tests
│   └── e2e/                  # End-to-end tests
├── models/                   # Trained Rasa models
├── config.yml                # Rasa pipeline configuration
├── domain.yml                # Chatbot domain definition
└── endpoints.yml             # Action server configuration
```

### Testing

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=actions tests/

# Run E2E tests (requires running servers)
pytest tests/e2e/
```

### Adding New Weather Features

1. **Create action class** in appropriate `actions/` file
2. **Add to domain.yml** under `actions:` section
3. **Add training examples** to `data/nlu.yml`
4. **Create conversation flows** in `data/stories.yml`
5. **Add unit tests** in `tests/unit/`
6. **Update documentation** in `docs/`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHER_API_KEY` | OpenWeather API key | Yes |
| `RASA_ENV` | Environment (dev/prod) | No |
| `LOG_LEVEL` | Logging level | No |

## Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Weather Features](docs/WEATHER_FEATURES.md)
- [Usage Examples](docs/USAGE.md)
- [Debugging Guide](docs/DEBUGGING.md)

## Contributing

See the main project [README](../README.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
# Rasa Chat

## Code Quality

The backend includes comprehensive quality assurance:

### Quality Tools
- **Bandit**: Security vulnerability scanning
- **Pylint**: Static code analysis
- **Safety**: Dependency vulnerability checking
- **Pytest**: Unit and integration testing
- **Coverage**: Test coverage reporting

### Running Quality Checks

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Security scan
bandit -r . -x .git,__pycache__,.pytest_cache,venv,env,tests

# Code analysis
pylint actions/

# Dependency vulnerabilities
safety check -r requirements.txt

# Tests with coverage
pytest --cov=actions tests/
```

## Deployment

For production deployment:

1. **Set environment variables**
2. **Train the model**: `rasa train`
3. **Start action server**: `rasa run actions --port 5055`
4. **Start Rasa server**: `rasa run --enable-api --port 5005`

### Docker Support

```bash
# Build image
docker build -t weather-chatbot-backend .

# Run container
docker run -p 5005:5005 -e OPENWEATHER_API_KEY=your_key weather-chatbot-backend
```