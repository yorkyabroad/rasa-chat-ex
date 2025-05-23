# Rasa Weather Bot

A Rasa-powered chatbot that provides weather information and forecasts using the OpenWeather API.

## Features

- Get current weather for any location
- Get weather forecasts for up to 3 days
- Compare weather conditions
- Get random interesting facts

## Prerequisites

- Python 3.8 or higher
- Rasa 3.0 or higher
- OpenWeather API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rasa-chat
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your OpenWeather API key:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## Usage

1. Train the model:
```bash
rasa train
```

2. Start the action server:
```bash
rasa run actions
```

3. Start the Rasa server:
```bash
rasa shell  # For command line interface
# or
rasa run    # For REST API
```

## Development

### Project Structure

```
rasa-chat/
├── actions/          # Custom actions
├── data/            # Training data
├── models/          # Trained models
├── tests/           # Test files
└── config/          # Configuration files
```

### Running Tests

```bash
pytest tests/
```

### Adding New Actions

1. Create a new action class in `actions/actions.py`
2. Add the action to `domain.yml`
3. Add training examples to `data/nlu.yml`
4. Add stories to `data/stories.yml`
5. Add any necessary tests

## Environment Variables

- `OPENWEATHER_API_KEY`: Your OpenWeather API key (required)
- `RASA_ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.