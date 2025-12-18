import os
import requests
from bs4 import BeautifulSoup
import pysrt

# ---------------------------------
# CONFIG
# ---------------------------------
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
SONG_NAME = "05. Messy"
ARTIST_NAME = "Unknown Artist"

INPUT_SRT = "whisper.srt"     # Whisper output with timestamps + placeholders
OUTPUT_SRT = "original.srt"   # Final Genius-aligned subtitle file

# ---------------------------------
# GENIUS API HELPERS
# ---------------------------------
def search_song(song, artist=None):
    """Search Genius API for the best matching song."""
    url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    params = {"q": f"{song} {artist}" if artist else song}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    hits = resp.json()["response"]["hits"]
    if not hits:
        raise ValueError("No Genius results found.")
    return hits[0]["result"]["url"]

def scrape_lyrics(url):
    """Scrape lyrics text from Genius song page."""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
    if not lyrics_divs:
        raise ValueError("No lyrics container found on Genius page.")
    lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
    return [line.strip() for line in lyrics.split("\n") if line.strip()]

# ---------------------------------
# MAIN
# ---------------------------------
def main():
    if not GENIUS_API_KEY:
        raise EnvironmentError("GENIUS_API_KEY not set in environment.")

    print(f"Searching Genius for '{SONG_NAME}' by '{ARTIST_NAME}'...")
    song_url = search_song(SONG_NAME, ARTIST_NAME)
    print(f"Found Genius page: {song_url}")

    print("Scraping lyrics...")
    genius_lyrics = scrape_lyrics(song_url)

    print(f"Got {len(genius_lyrics)} lyric lines.")

    print("Loading Whisper subtitles...")
    subs = pysrt.open(INPUT_SRT)

    # Replace Whisper text with Genius lyrics
    for i, sub in enumerate(subs):
        if i < len(genius_lyrics):
            sub.text = genius_lyrics[i]
        else:
            sub.text = ""  # remove leftovers

    print(f"Writing aligned subtitles → {OUTPUT_SRT}")
    subs.save(OUTPUT_SRT, encoding="utf-8")

    print("✅ Done. Check 'original.srt'.")

if __name__ == "__main__":
    main()

