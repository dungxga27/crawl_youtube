import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
LARK_WEBHOOK = os.getenv("LARK_WEBHOOK")

# lấy list channel từ env
CHANNEL_IDS = os.getenv("CHANNEL_IDS", "").split(",")

DATA_FILE = "sent_videos.json"


# ==========================
# LOAD SENT VIDEOS (FIXED)
# ==========================

sent_videos = set()

if os.path.exists(DATA_FILE):
    # Fix: Check if file has content and is valid JSON
    if os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, "r") as f:
            try:
                sent_videos = set(json.load(f))
            except json.JSONDecodeError:
                print("JSON corrupted, resetting database.")
                sent_videos = set()
    else:
        sent_videos = set()
else:
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
        requests.post(LARK_WEBHOOK, json=data)
    except Exception as e:
        print("Lark error:", e)


# ==========================
# FETCH VIDEOS
# ==========================

def fetch_videos(channel_id):

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
        "type": "video"
    }

    res = requests.get(url, params=params)
    data = res.json()

    if "items" not in data:
        return []

    return data["items"]


# ==========================
# MAIN
# ==========================

def main():

    for channel in CHANNEL_IDS:
        channel_id = channel.strip()
        if not channel_id: continue

        videos = fetch_videos(channel_id)

        for item in videos:

            if item["id"]["kind"] != "youtube#video":
                continue

            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_name = item["snippet"]["channelTitle"]

            if video_id in sent_videos:
                continue

            video_url = f"https://youtube.com/watch?v={video_id}"

            print("New video:", title)

            send_lark(title, video_url, channel_name)

            sent_videos.add(video_id)

    save_sent()


if __name__ == "__main__":
    main()