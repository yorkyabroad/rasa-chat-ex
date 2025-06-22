# Rasa Weather Chatbot

A full-stack weather assistant application built with Rasa (backend) and React (frontend) that provides comprehensive weather information through a conversational interface.

## Overview

This project consists of two main components:
- **Backend**: Rasa-powered chatbot with OpenWeather API integration
- **Frontend**: React-based chat interface with quick actions and responsive design

## Features

### Weather Capabilities
- Current weather conditions for any location
- Weather forecasts (up to 3 days)
- UV index information and safety recommendations
- Air pollution data and health advice
- Temperature ranges and extremes
- Wind conditions and recommendations
- Precipitation forecasts (rain/snow)
- Sunrise/sunset times
- Severe weather alerts
- Historical weather comparisons

### User Interface
- Interactive chat interface
- Quick action buttons for common requests
- Pre-configured popular locations
- Real-time communication with Rasa backend
- Responsive design for desktop and mobile
- Visual weather icons and loading states

## Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 14+
- OpenWeather API key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd rasa-chat
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your OPENWEATHER_API_KEY
rasa train
```

3. **Frontend Setup**
```bash
cd ../frontend
npm install
```

### Running the Application

1. **Start the backend services**
```bash
cd backend
# Terminal 1: Start action server
rasa run actions

# Terminal 2: Start Rasa server
rasa run --enable-api --cors "*"
```

2. **Start the frontend**
```bash
cd frontend
npm start
```

3. **Access the application**
Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
rasa-chat/
├── backend/                 # Rasa chatbot backend
│   ├── actions/            # Custom weather actions
│   ├── data/              # Training data (NLU, stories, rules)
│   ├── docs/              # Backend documentation
│   ├── tests/             # Unit and E2E tests
│   └── models/            # Trained Rasa models
├── frontend/               # React frontend
│   ├── src/               # React components
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
└── .github/workflows/     # CI/CD pipelines
```

## Development

### Backend Development
See [backend/README.md](backend/README.md) for detailed backend setup, API documentation, and development guidelines.

### Frontend Development
See [frontend/README.md](frontend/README.md) for frontend-specific setup and development instructions.

### Testing
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Code Quality
The project includes automated code quality checks:
- Bandit (security scanning)
- Pylint (static analysis)
- Safety (dependency vulnerabilities)
- Test coverage reporting

## API Integration

The application uses the OpenWeather API for weather data. You'll need to:
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add it to `backend/.env` as `OPENWEATHER_API_KEY`

## Deployment

The project includes GitHub Actions workflows for:
- Automated testing
- Code quality checks
- Security scanning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code quality checks pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](backend/LICENSE) file for details.