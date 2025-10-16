from googleapiclient.discovery import build
import json
import dotenv
import os
# -------------------------------
# CONFIGURATION
# -------------------------------

dotenv.load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # Example: Google Developers
youtube = build("youtube", "v3", developerKey=API_KEY)


def get_uploads_playlist_id(channel_id):
    """Get the uploads playlist ID of a channel."""
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return uploads_playlist_id


def get_all_videos_from_playlist(playlist_id):
    """Retrieve all videos from a playlist."""
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


def get_video_details(video_ids):
    """Get details for a list of video IDs."""
    stats = []
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids[i:i+50])
        ).execute()
        
        for video in response["items"]:
            info = {
                "title": video["snippet"]["title"],
                "video_id": video["id"],
                "published_at": video["snippet"]["publishedAt"],
                "duration": video["contentDetails"]["duration"],
                "views": video["statistics"].get("viewCount", 0),
                "likes": video["statistics"].get("likeCount", 0),
                "comments": video["statistics"].get("commentCount", 0)
            }
            stats.append(info)
    return stats


def main():
    print("Fetching uploads playlist...")
    playlist_id = get_uploads_playlist_id(CHANNEL_ID)
    
    print("Fetching all video IDs...")
    video_ids = get_all_videos_from_playlist(playlist_id)
    print(f"Found {len(video_ids)} videos.")
    
    print("Fetching video details...")
    video_data = get_video_details(video_ids)
    
    # Save as JSON file
    with open("youtube_channel_videos.json", "w", encoding="utf-8") as f:
        json.dump(video_data, f, indent=4)
    
    print("Data saved to youtube_channel_videos.json")
    print(f"Sample video:\n{json.dumps(video_data[0], indent=4)}")


if __name__ == "__main__":
    main()
