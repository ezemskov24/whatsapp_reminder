import os

from dotenv import load_dotenv

load_dotenv()

TWILIO_SID: str = os.environ.get('TWILIO_SID')
TWILIO_AUTH_TOKEN: str = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUM: str = os.environ.get('TWILIO_NUM')

REDIS_URL: str = os.environ.get('REDIS_URL')

def get_database_url():
    return os.environ.get("DATABASE_URL")
