# common/secrets_env.py
import os
from dotenv import load_dotenv

def load_secrets_env_variables():
    load_dotenv()  # Loads .env file if exists
    # Or just rely on system env vars
    pass