import requests
import json
import os

# ==========================
# CONFIG
# ==========================

API_KEY = "AIzaSyBETSjK67SbQrVqB4rgeQ9stH6NUYFR9J0"

CHANNEL_IDS = [
    "UCfSrgydQps6YOFE8r3lGOpg",
]

LARK_WEBHOOK = "https://open.larksuite.com/open-apis/bot/v2/hook/d55067f6-7455-43dc-ac49-7e98501cb1ae"

DATA_FILE = "sent_videos.json"


# ==========================
# LOAD SENT VIDEOS
# ==========================

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        sent_videos = set(json.load(f))
else:
    sent_videos = set()


# ==========================
# SAVE SENT VIDEOS
# ==========================

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
        "maxResults": 1
    }

    res = requests.get(url, params=params)

    print(res.text)   # debug API response

    data = res.json()

    if "items" not in data:
        return []

    return data["items"]


# ==========================
# MAIN
# ==========================

def main():

    for channel in CHANNEL_IDS:

        videos = fetch_videos(channel)

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