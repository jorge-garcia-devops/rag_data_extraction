import os
import re
import requests
from bs4 import BeautifulSoup

# Directory containing the text files
DIRECTORY = "data"

# YouTube URL format
YOUTUBE_URL = "https://www.youtube.com/watch?v="

def get_youtube_title(video_id):
    """Fetches the YouTube video title without using the API."""
    url = YOUTUBE_URL + video_id
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevents bot detection
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")

        if title_tag:
            title = title_tag.text.replace("- YouTube", "").strip()
            return re.sub(r'\W+', '', title.title())  # Remove non-alphanumeric chars & TitleCase
        else:
            print(f"⚠ Could not find title for {video_id}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching title for {video_id}: {e}")
        return None

def rename_files():
    """Renames YouTube .txt files based on their video title."""
    for filename in os.listdir(DIRECTORY):
        match = re.match(r"([a-zA-Z0-9_-]{11})\.txt$", filename)  # Matches (YouTube ID).txt

        if match:
            video_id = match.group(1)
            new_title = get_youtube_title(video_id)

            if new_title:
                new_filename = f"{new_title}.txt"
                old_path = os.path.join(DIRECTORY, filename)
                new_path = os.path.join(DIRECTORY, new_filename)

                os.rename(old_path, new_path)
                print(f"✅ Renamed: {filename} → {new_filename}")
            else:
                print(f"⚠ Skipped: {filename} (No title found)")

# Run the script
rename_files()