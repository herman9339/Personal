import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env into environment

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHOP_URL = os.getenv("SHOP_URL")
SHOP_TOKEN = os.getenv("SHOP_TOKEN")

def check_env_vars():
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not SHOP_URL:
        missing.append("SHOP_URL")
    if not SHOP_TOKEN:
        missing.append("SHOP_TOKEN")
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
