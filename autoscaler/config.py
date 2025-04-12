# autoscaler/config.py

import os
from dotenv import load_dotenv

# Load .env nếu tồn tại (chạy local)
load_dotenv(dotenv_path="conf/.env", override=True)

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID", "")
ENABLE_NOTIFY = os.getenv("ENABLE_NOTIFY", "false").lower() == "true"

# Danh sách namespace không được phép scale
PROTECTED_NAMESPACES = [
    ns.strip() for ns in os.getenv("PROTECTED_NAMESPACES", "kube-system,istio-system").split(",") if ns.strip()
]
