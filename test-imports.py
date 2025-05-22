# See this guide on how to implement these action:

try:
    import rasa_sdk
    import requests
    import dotenv
    # All required packages are installed!
    import sys
    sys.stderr.write("All required packages are installed!\n")
except ImportError as e:
    # Log the missing package to stderr instead of using print
    import sys
    sys.stderr.write(f"Missing package: {e}\n")