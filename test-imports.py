try:
    import rasa_sdk
    import requests
    import dotenv
    print("All required packages are installed!")
except ImportError as e:
    print(f"Missing package: {e}")

