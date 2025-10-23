#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
import subprocess

# -------------------------------
# CONFIGURATION
# -------------------------------

OUTPUT_DIR = "audio_downloads"
AUDIO_FORMAT = "mp3"  # Options: mp3, wav, m4a, opus, etc.
AUDIO_QUALITY = "192"  # kbps for mp3

def ensure_yt_dlp_installed():
    """Check if yt-dlp is installed, provide instructions if not."""
    try:
        subprocess.run(["yt-dlp", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp is not installed!")
        print("\nPlease install it using one of these methods:")
        print("  • pip install yt-dlp")
        print("  • sudo apt install yt-dlp (on Ubuntu/Debian)")
        print("  • brew install yt-dlp (on macOS)")
        return False


def download_audio(video_url, video_id, channel_name, output_dir):
    """Download audio from a YouTube video using yt-dlp.
    
    Returns:
        tuple: (success: bool, file_path: str or None)
    """
    # Create channel-specific subdirectory
    channel_dir = Path(output_dir) / channel_name.replace("/", "_").replace(" ", "_")
    channel_dir.mkdir(parents=True, exist_ok=True)
    
    # Output template: channel/video_id.ext
    output_template = str(channel_dir / f"{video_id}.%(ext)s")
    
    # Check if file already exists
    audio_file = channel_dir / f"{video_id}.{AUDIO_FORMAT}"
    if audio_file.exists():
        print(f"   ⏭️  Already downloaded: {video_id}")
        return True, str(audio_file.resolve())
    
    try:
        # yt-dlp command to extract audio
        cmd = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", AUDIO_FORMAT,
            "--audio-quality", AUDIO_QUALITY,
            "-o", output_template,
            "--no-playlist",
            "--quiet",  # Suppress most output
            "--progress",  # Show progress bar
            video_url
        ]
        
        subprocess.run(cmd, check=True)
        print(f"   ✅ Downloaded: {video_id}")
        return True, str(audio_file.resolve())
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to download {video_id}: {e}")
        return False, None
    except Exception as e:
        print(f"   ⚠️  Unexpected error for {video_id}: {e}")
        return False, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_audio.py <data_file.json>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    # Check if yt-dlp is installed
    if not ensure_yt_dlp_installed():
        sys.exit(1)
    
    # Load video data
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        sys.exit(1)
    
    with open(data_file, "r", encoding="utf-8") as f:
        videos = json.load(f)
    
    if not videos:
        print("⚠️  No videos found in data file.")
        sys.exit(0)
    
    print(f"\n🎵 Starting audio download for {len(videos)} videos...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🎼 Audio format: {AUDIO_FORMAT} @ {AUDIO_QUALITY}kbps\n")
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Track statistics
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    # Download each video
    for idx, video in enumerate(videos, 1):
        video_id = video.get("video_id")
        video_url = video.get("video_url")
        channel_name = video.get("channel", "Unknown")
        title = video.get("title", "Unknown")
        
        print(f"[{idx}/{len(videos)}] {channel_name} - {title[:50]}...")
        
        if not video_url or not video_id:
            print("   ⚠️  Missing URL or ID, skipping...")
            skipped_count += 1
            continue
        
        # Check if already exists and has audio_file_path
        channel_dir = Path(OUTPUT_DIR) / channel_name.replace("/", "_").replace(" ", "_")
        audio_file = channel_dir / f"{video_id}.{AUDIO_FORMAT}"
        if audio_file.exists() and "audio_file_path" in video:
            print(f"   ⏭️  Already exists, skipping...")
            skipped_count += 1
            continue
        
        success, file_path = download_audio(video_url, video_id, channel_name, OUTPUT_DIR)
        if success:
            # Update the video entry with the file path
            video["audio_file_path"] = file_path
            success_count += 1
        else:
            failed_count += 1
    
    # Save updated data back to the JSON file
    print("\n💾 Updating data file with audio file paths...")
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=4, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DOWNLOAD SUMMARY")
    print("="*60)
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"⏭️  Skipped (already exists): {skipped_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Audio files saved in: {OUTPUT_DIR}/")
    print(f"📝 Data file updated: {data_file}")
    print("="*60)


if __name__ == "__main__":
    main()
