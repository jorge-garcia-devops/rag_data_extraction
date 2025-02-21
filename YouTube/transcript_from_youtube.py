import os
import re
from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# User-configurable settings
URL = "https://youtube.com/playlist?list=PL4o9bTT3px_idofrSWZ3jWN3pJqWglvW2&si=AjErTqgRM6wKR0Y_"  # Change this to a single video URL or playlist
PREFERRED_LANGUAGE = "en"  # Change this to your desired language code
OUTPUT_FORMAT = "txt"  # Change to "md" if you want Markdown files
OUTPUT_DIR = "../data"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r"(?:v=|\/embed\/|\/v\/|youtu.be\/|\/e\/|watch\?v=|\?v=)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_video_transcript(video_id, language):
    """Fetch and save transcript for a single video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to fetch transcript in the preferred language
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            print(f"⚠ No '{language}' transcript for video {video_id}. Trying default...")
            transcript = transcript_list.find_generated_transcript(transcript_list._manually_created_transcripts + transcript_list._generated_transcripts)
        
        transcript_data = transcript.fetch()
        transcript_text = "\n".join([f"{t['start']:.2f} - {t['text']}" for t in transcript_data])
        
        # Save to file
        filename = os.path.join(OUTPUT_DIR, f"{video_id}.{OUTPUT_FORMAT}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        
        print(f"✅ Saved transcript: {filename}")
    except TranscriptsDisabled:
        print(f"❌ Transcripts are disabled for video {video_id}. Skipping.")
    except Exception as e:
        print(f"❌ Failed to get transcript for video {video_id}: {e}")

def process_url(url, language):
    """Detect if the URL is a playlist or a single video and process accordingly."""
    if "playlist?list=" in url:
        playlist = Playlist(url)
        print(f"📜 Found {len(playlist.video_urls)} videos in the playlist.")
        for video_url in playlist.video_urls:
            video_id = extract_video_id(video_url)
            if video_id:
                get_video_transcript(video_id, language)
    else:
        video_id = extract_video_id(url)
        if video_id:
            get_video_transcript(video_id, language)
        else:
            print("❌ Invalid YouTube URL.")

# Run the script
process_url(URL, PREFERRED_LANGUAGE)
