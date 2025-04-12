# Configuration loader
# autoscaler/config.py

import os
from dotenv import load_dotenv

# Load từ file .env nếu tồn tại (dành cho môi trường local dev)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "conf", ".env"), override=True)

# Đọc biến môi trường
WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID", "")
ENABLE_NOTIFY = os.getenv("ENABLE_NOTIFY", "false").lower() in ["true", "1", "yes"]

# Danh sách namespace bảo vệ (không được scale dù có rule hay không)
# Có thể cấu hình trong .env hoặc config map Helm
PROTECTED_NAMESPACES =_
