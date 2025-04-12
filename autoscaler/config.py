# autoscaler/config.py

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="conf/.env")

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID")
ENABLE_NOTIFY = os.getenv("ENABLE_NOTIFY", "false").lower() == "true"
