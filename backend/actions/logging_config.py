# This files contains utility functions for logging configuration.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import logging
import sys
import os

# Configure logger for this module
logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging for the entire application."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("LOG_FILE", None)
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Force reconfiguration even if already configured
    )
    
    # Return the root logger
    return logging.getLogger()

# Add a test message to verify logging is working
logger.info("Logging configuration initialized")