
import requests
import json
import os
import time

API_KEYS = [
    os.getenv("YOUTUBE_API_KEY"),
    os.getenv("YOUTUBE_API_KEY_2")
]

FILE_NAME = "links.json"

CHANNELS_MAP = {
    "SOMOY TV": "Somoy TV Live সময় টিভি লাইভ",
    "EKHON TV": "Ekhon TV Live সরাসরি এখন টিভি",
    "EKATTOR TV": "Ekattor TV Live একাত্তর টিভি লাইভ",
    "JAMUNA TV": "Jamuna TV Live যমুনা টিভি লাইভ",
    "DBC NEWS": "DBC News Live ডিবিসি নিউজ লাইভ",
    "CHANNEL I": "Channel i Live চ্যানেল আই লাইভ",
    "ATN NEWS": "ATN News Live এটিএন নিউজ লাইভ",
    "NTV BANGLA": "NTV Bangladesh Live এনটিভি লাইভ",
    "RTV BANGLA": "Rtv Bangladesh Live আরটিভি লাইভ",
    "NEWS24 BANGLA": "NEWS24 Bangladesh LIVE নিউজ২৪ লাইভ",
    "DESH TV": "Desh TV Live দেশ টিভি লাইভ",
    "INDEPENDENT": "Independent TV Live ইন্ডিপেন্ডেন্ট টিভি লাইভ",
    "CHANNEL 24": "Channel 24 Live চ্যানেল ২৪ লাইভ",
    "ZEE 24 BANGLA": "zee 24 bangla Live",
    "AL JAZEERA": "Al Jazeera English Live",
    "WILD LIVE": "National Geographic Wild Live",
    "ANIMALLS": "Discovery Live",
    "HINDI MOVIES": "Bollywood Movies Live Streaming Free",
    "BANGLA MOVIES": "Bangla new full movie latest",
    "9XM MUSIC": "9XM Live Bollywood Music"
}

# নির্দিষ্ট চ্যানেলের Channel ID
CHANNEL_IDS = {
    "EKHON TV": "UCWVqdPTigfQ-cSNwG7O9MeA",

    # উদাহরণ:
    # "SOMOY TV": "YOUR_SOMOY_CHANNEL_ID",
    # "JAMUNA TV": "YOUR_JAMUNA_CHANNEL_ID",
    # "DBC NEWS": "YOUR_DBC_CHANNEL_ID",
}


def search_youtube(params, key):

    params["key"] = key

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=params,
            timeout=20
        )

        data = response.json()

        if response.status_code != 200:
            error = data.get("error", {}).get("message", "")
            print("API ERROR:", error)

            # এই API Key-তে সমস্যা হলে পরের Key চেষ্টা
            return None

        return data.get("items", [])

    except (requests.RequestException, ValueError) as e:
        print("CONNECTION ERROR:", e)
        return None


def get_live_url(query, keys, channel_id=None):

    for key in keys:

        if not key:
            continue

        # প্রথমে Channel ID Search, এরপর Old Keyword Search
        search_modes = []

        if channel_id:
            search_modes.append({
                "channelId": channel_id
            })

        search_modes.append({
            "q": query
        })

        for search_filter in search_modes:

            params = {
                "part": "snippet",
                "eventType": "live",
                "type": "video",
                "maxResults": 10,
                "order": "date"
            }

            params.update(search_filter)

            print("Searching:", search_filter)

            items = search_youtube(params, key)

            if items is None:
                # API Key বা নেটওয়ার্ক সমস্যা হলে পরের Key
                break

            for item in items:

                video_id = item.get("id", {}).get("videoId")

                snippet = item.get("snippet", {})
                video_channel = snippet.get("channelId")
                video_title = snippet.get("title", "")

                if not video_id:
                    continue

                # Channel ID Search হলে অবশ্যই একই চ্যানেল হতে হবে
                if (
                    "channelId" in search_filter
                    and video_channel != channel_id
                ):
                    continue

                print("FOUND LIVE:", video_title)
                print("VIDEO ID:", video_id)

                return (
                    f"https://www.youtube.com/embed/"
                    f"{video_id}?autoplay=1"
                )

            if "channelId" in search_filter:
                print("No live found with Channel ID.")
                print("Trying Keyword Search...")

    return None


# পুরোনো JSON লোড করা
try:
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        old_results = json.load(f)

except (FileNotFoundError, json.JSONDecodeError):
    old_results = []

# পুরোনো লিংক সংরক্ষণ
old_links = {
    item["name"].upper(): item["url"]
    for item in old_results
    if isinstance(item, dict)
    and "name" in item
    and "url" in item
}


new_results = []

for display_name, search_query in CHANNELS_MAP.items():

    print(f"\nChecking: {display_name}...")

    channel_id = CHANNEL_IDS.get(display_name)

    new_url = get_live_url(
        search_query,
        API_KEYS,
        channel_id
    )

    if new_url:
        final_url = new_url
        print("SUCCESS: New live link found!")

    elif display_name in old_links:
        final_url = old_links[display_name]
        print("WARNING: No live found. Keeping old link.")

    else:
        print("WARNING: No live video found.")
        continue

    new_results.append({
        "name": display_name.upper(),
        "url": final_url
    })

    time.sleep(1)


with open(FILE_NAME, "w", encoding="utf-8") as f:
    json.dump(
        new_results,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\nসবগুলো লিংক আপডেট সম্পন্ন হয়েছে!")
