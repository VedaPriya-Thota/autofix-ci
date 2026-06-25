import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration for AutoFix CI system
    """

    # Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Optional: future extensions
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    # Model configuration
    GEMINI_MODEL = "gemini-1.5-flash"

    # Safety / tuning
    MAX_RETRIES = 2
    TEMPERATURE = 0.2


config = Config()