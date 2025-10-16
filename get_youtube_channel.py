from googleapiclient.discovery import build
import json
import dotenv
import os
import time
# -------------------------------
# CONFIGURATION
# -------------------------------

dotenv.load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

# Example: list of YouTube channel IDs
CHANNEL_IDS = [
    "UCoS0xYkuJq07NU92yFBEfKA",  # Hit radio
    "@TouilTalks"
]

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_channel_data(channel_id):
    """Get a channel's ID and name."""
    if channel_id.startswith("@"):
        response = youtube.channels().list(
            part="id",
            forHandle=channel_id
        ).execute()
        channel_name = channel_id[1:]
        channel_id = response["items"][0]["id"]
        pass
    else:
        response = youtube.channels().list(
            part="snippet",
            id=channel_id
        ).execute()
        channel_name = response["items"][0]["snippet"]["title"]
    return channel_id, channel_name


def get_uploads_playlist_id(channel_id):
    """Get the uploads playlist ID of a channel."""
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_videos_from_playlist(playlist_id):
    """Retrieve all video IDs from a playlist."""
    videos = []
    next_page_token = None
    
    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        for item in response["items"]:
            videos.append(item["contentDetails"]["videoId"])
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return videos


def get_video_details(video_ids, channel_name):
    """Get detailed info for a list of video IDs."""
    stats = []
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids[i:i+50])
        ).execute()
        
        for video in response["items"]:
            video_id = video["id"]
            info = {
                "channel": channel_name,
                "title": video["snippet"]["title"],
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "published_at": video["snippet"]["publishedAt"],
                "duration": video["contentDetails"]["duration"],
                "views": int(video["statistics"].get("viewCount", 0)),
                "likes": int(video["statistics"].get("likeCount", 0)),
                "comments": int(video["statistics"].get("commentCount", 0))
            }
            stats.append(info)
    return stats


def main():
    all_data = []
    output_file = "youtube_channels_data.json"
    
    for given_channel_id in CHANNEL_IDS:
        try:
            channel_id, channel_name = get_channel_data(given_channel_id)
            print(f"\n🔍 Processing channel: {channel_name} ({channel_id})")
            
            playlist_id = get_uploads_playlist_id(channel_id)
            video_ids = get_all_videos_from_playlist(playlist_id)
            print(f"   Found {len(video_ids)} videos.")
            
            videos_data = get_video_details(video_ids, channel_name)
            all_data.extend(videos_data)
            
            # Respect API quotas
            time.sleep(1)
        
        except Exception as e:
            print(f"⚠️ Error processing {channel_id}: {e}")
    
    # Save all results to a JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    
    print("\n✅ Data collection complete!")
    print(f"Total videos processed: {len(all_data)}")
    print(f"Saved to {output_file}")
    if all_data:
        print("\nSample entry:")
        print(json.dumps(all_data[int(time.time()) % len(all_data)], indent=4))


if __name__ == "__main__":
    main()
