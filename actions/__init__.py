# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging

# Configure logger
logger = logging.getLogger(__name__)

# Skip environment validation for tests
# The actual validation will happen in the main application
logger.info("Initializing actions module")