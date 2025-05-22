# This files contains validation utilities for environment variables.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import sys
import logging
from actions.weather_utils import validate_env_vars

# Configure logger
logger = logging.getLogger(__name__)

def check_required_env_vars():
    """
    Check for required environment variables and exit if any are missing.
    This should be called from the main application, not during testing.
    """
    required_vars = ["OPENWEATHER_API_KEY"]
    if not validate_env_vars(required_vars):
        logger.critical("Exiting due to missing required environment variables")
        sys.exit(1)