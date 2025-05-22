# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
from actions.logging_config import setup_logging

# Set up logging for the entire package
setup_logging()

# Configure logger for this module
logger = logging.getLogger(__name__)

# Skip environment validation for tests
# The actual validation will happen in the main application
logger.info("Initializing actions module")