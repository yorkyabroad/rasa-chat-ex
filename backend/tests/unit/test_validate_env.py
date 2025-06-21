import pytest
from unittest.mock import patch, MagicMock
import sys
from actions.validate_env import check_required_env_vars

class TestValidateEnv:
    @patch('actions.validate_env.validate_env_vars')
    def test_check_required_env_vars_success(self, mock_validate_env_vars):
        # Setup mock to return True (all variables present)
        mock_validate_env_vars.return_value = True
        
        # Call the function
        check_required_env_vars()
        
        # Verify results
        mock_validate_env_vars.assert_called_once_with(["OPENWEATHER_API_KEY"])
        
    @patch('actions.validate_env.validate_env_vars')
    @patch('actions.validate_env.sys.exit')
    def test_check_required_env_vars_missing(self, mock_exit, mock_validate_env_vars):
        # Setup mock to return False (missing variables)
        mock_validate_env_vars.return_value = False
        
        # Call the function
        check_required_env_vars()
        
        # Verify sys.exit was called
        mock_validate_env_vars.assert_called_once_with(["OPENWEATHER_API_KEY"])
        mock_exit.assert_called_once_with(1)