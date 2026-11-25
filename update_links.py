
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


# Official YouTube Handles
CHANNEL_IDS = {
    "SOMOY TV": "@somoynews360",
    "EKHON TV": "@ekhontv",
    "EKATTOR TV": "@EkattorTelevision",
    "JAMUNA TV": "@JamunaTVbd",
    "DBC NEWS": "@dbcnewstv",
    "ATN NEWS": "@atnnewsltd",
    "NTV BANGLA": "@NTVDigitalLive",
    "RTV BANGLA": "@RtvLiveBD",
    "NEWS24 BANGLA": "@news24livetv",
    "DESH TV": "@livedeshtv",
    "INDEPENDENT": "@IndependentTelevision",
    "CHANNEL 24": "@channel24digital",
    "AL JAZEERA": "@aljazeeraenglish",
    "WILD LIVE": "@NatGeoAnimals"
    
}


# Handle থেকে আসল Channel ID বের করা
def get_channel_id(handle, keys):

    for key in keys:

        if not key:
            continue

        try:
            url = "https://www.googleapis.com/youtube/v3/channels"

            params = {
                "part": "id",
                "forHandle": handle.replace("@", ""),
                "key": key
            }

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            data = response.json()

            if response.status_code != 200:

                print(
                    "HANDLE API ERROR:",
                    data.get("error", {}).get("message")
                )

                continue

            items = data.get("items", [])

            if items:

                channel_id = items[0]["id"]

                print("CHANNEL ID FOUND:", channel_id)

                return channel_id

            print("CHANNEL HANDLE NOT FOUND:", handle)

        except (requests.RequestException, ValueError) as e:

            print("HANDLE CONNECTION ERROR:", e)

    return None


# YouTube Search API
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

            return None

        return data.get("items", [])

    except (requests.RequestException, ValueError) as e:

        print("CONNECTION ERROR:", e)

        return None


# Live Video Search
def get_live_url(query, keys, channel_id=None):

    for key in keys:

        if not key:
            continue

        search_modes = []

        # প্রথমে নির্দিষ্ট Channel ID
        if channel_id:

            search_modes.append({
                "channelId": channel_id
            })

        # এরপর আগের Keyword Search
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

            print("SEARCHING:", search_filter)

            items = search_youtube(params, key)

            if items is None:
                break

            for item in items:

                video_id = item.get(
                    "id", {}
                ).get("videoId")

                snippet = item.get("snippet", {})

                video_channel = snippet.get("channelId")

                video_title = snippet.get("title", "")

                if not video_id:
                    continue

                # Channel ID অবশ্যই মিলতে হবে
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

                print("CHANNEL ID LIVE NOT FOUND")

                print("TRYING KEYWORD SEARCH...")

    return None


# পুরোনো JSON লোড করা
try:

    with open(FILE_NAME, "r", encoding="utf-8") as f:

        old_results = json.load(f)

except (FileNotFoundError, json.JSONDecodeError):

    old_results = []


# পুরোনো URL সংরক্ষণ
old_links = {

    item["name"].upper(): item["url"]

    for item in old_results

    if isinstance(item, dict)
    and "name" in item
    and "url" in item
}


# সব চ্যানেল চেক
new_results = []

for display_name, search_query in CHANNELS_MAP.items():

    print("\n" + "=" * 45)

    print("CHECKING:", display_name)

    print("=" * 45)

    # Handle থেকে Channel ID বের করা
    channel_handle = CHANNEL_IDS.get(display_name)

    channel_id = None

    if channel_handle:

        print("OFFICIAL HANDLE:", channel_handle)

        channel_id = get_channel_id(
            channel_handle,
            API_KEYS
        )

    else:

        print("NO HANDLE: Using keyword search.")

    # Live Search
    new_url = get_live_url(
        search_query,
        API_KEYS,
        channel_id
    )

    if new_url:

        final_url = new_url

        print("SUCCESS: NEW LIVE LINK FOUND!")

    elif display_name in old_links:

        final_url = old_links[display_name]

        print("WARNING: KEEPING OLD URL.")

    else:

        print("WARNING: NO LIVE VIDEO FOUND.")

        continue

    new_results.append({

        "name": display_name.upper(),

        "url": final_url

    })

    time.sleep(1)


# JSON Update
with open(FILE_NAME, "w", encoding="utf-8") as f:

    json.dump(
        new_results,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\nসবগুলো লিংক আপডেট সম্পন্ন হয়েছে!")

