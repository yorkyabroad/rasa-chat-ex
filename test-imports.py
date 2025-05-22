# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
from actions.logging_config import setup_logging
logger = setup_logging()

# Configure logger
logger = logging.getLogger(__name__)

try:
    import rasa_sdk
    import requests
    import dotenv
    # All required packages are installed!
    logger.info("All required packages are installed!")
except ImportError as e:
    # Log the missing package
    logger.error(f"Missing package: {e}")