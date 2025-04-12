# Email notifier module
# autoscaler/notifier.py

import requests
from autoscaler.config import WEBEX_BOT_TOKEN, WEBEX_ROOM_ID, ENABLE_NOTIFY

def send_webex_message(message: str):
    if not ENABLE_NOTIFY or not WEBEX_BOT_TOKEN or not WEBEX_ROOM_ID:
        print("⚠️  Cảnh báo: Thiếu WEBEX_BOT_TOKEN hoặc WEBEX_ROOM_ID (có thể skip nếu đang dev local)")
        return

    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": WEBEX_ROOM_ID,
        "markdown": message
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("✅ Đã gửi Webex message")
    else:
        print(f"❌ Lỗi gửi Webex: {response.status_code} - {response.text}")
