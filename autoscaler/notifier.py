# autoscaler/notifier.py

import requests
from autoscaler.config import WEBEX_BOT_TOKEN, WEBEX_ROOM_ID

def send_webex_message(message: str):
    if not WEBEX_BOT_TOKEN or not WEBEX_ROOM_ID:
        print("⚠️  Cảnh báo: Thiếu WEBEX_BOT_TOKEN hoặc WEBEX_ROOM_ID")
        return
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "roomId": WEBEX_ROOM_ID,
        "markdown": message
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Đã gửi Webex message")
    else:
        print(f"❌ Lỗi gửi Webex: {response.status_code} - {response.text}")
