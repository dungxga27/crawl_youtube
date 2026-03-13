import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
LARK_WEBHOOK = os.getenv("LARK_WEBHOOK")
CHANNEL_IDS = os.getenv("CHANNEL_IDS", "").split(",")
DATA_FILE = "sent_videos.json"

# ==========================
# LOAD SENT VIDEOS
# ==========================
sent_videos = set()
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    with open(DATA_FILE, "r") as f:
        try:
            sent_videos = set(json.load(f))
        except json.JSONDecodeError:
            sent_videos = set()

def save_sent():
    with open(DATA_FILE, "w") as f:
        json.dump(list(sent_videos), f)

# ==========================
# SEND LARK MESSAGE
# ==========================
def send_lark(title, video_url, channel):
    data = {
        "msg_type": "text",
        "content": {
            "text": f"📺 New Video\nChannel: {channel}\n{title}\n{video_url}"
        }
    }
    try:
        r = requests.post(LARK_WEBHOOK, json=data)
        print(f"Lark response: {r.status_code}")
    except Exception as e:
        print("Lark error:", e)

# ==========================
# FETCH VIDEOS
# ==========================
def fetch_latest_video(channel_id):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",   # Sắp xếp theo ngày mới nhất
        "maxResults": 1,   # Chỉ lấy 1 kết quả
        "type": "video"    # Chỉ lấy video (bỏ qua playlist/live stream cũ)
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Error fetching {channel_id}: {e}")
        return []

# ==========================
# MAIN
# ==========================
def main():
    if not API_KEY or not LARK_WEBHOOK:
        print("Missing API Keys or Webhook URL!")
        return

    for channel in CHANNEL_IDS:
        cid = channel.strip()
        if not cid: continue

        items = fetch_latest_video(cid)

        if items:
            video = items[0]
            video_id = video["id"]["videoId"]
            
            # Kiểm tra xem video này đã gửi chưa
            if video_id not in sent_videos:
                title = video["snippet"]["title"]
                channel_name = video["snippet"]["channelTitle"]
                video_url = f"https://youtube.com/watch?v={video_id}"

                print(f"Found new video: {title}")
                send_lark(title, video_url, channel_name)
                
                # Lưu ID vào bộ nhớ để không gửi lại
                sent_videos.add(video_id)
            else:
                print(f"No new videos for channel {cid}")

    save_sent()

if __name__ == "__main__":
    main()