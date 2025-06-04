#!/bin/bash
# Script to run all code quality checks

echo "Running Bandit security scan..."
bandit -r . -x .git,__pycache__,.pytest_cache,venv,env,tests,htmlcov -ll

echo -e "\nRunning Pylint static analysis..."
pylint --disable=C0111,C0103 actions/

echo -e "\nChecking for vulnerable dependencies..."
safety check -r requirements.txt --ignore-unpinned

echo -e "\nRunning tests with coverage..."
pytest --cov=actions tests/

echo -e "\nAll code quality checks completed."