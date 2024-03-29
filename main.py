import subprocess
import requests
import sys
import os

FLIXQUEST_API_BASE_URL = "https://flixquest-api.vercel.app"

def fetch_media_data(media_type, tmdb_id, season=None, episode=None, provider=None):
    if media_type == "movie":
        url = f"{FLIXQUEST_API_BASE_URL}/{provider}/watch-movie?tmdbId={tmdb_id}"
    elif media_type == "tv":
        url = f"{FLIXQUEST_API_BASE_URL}/{provider}/watch-tv?tmdbId={tmdb_id}&season={season}&episode={episode}"
    else:
        return None

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def play_video(video_url):
    # Starting playback and redirecting stderr to /dev/null to hide additional output
    subprocess.run(["mpv", video_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def select_fzf(prompt, options):
    try:
        selected_option = os.popen(f"echo '{options}' | fzf").read().strip()
        return selected_option
    except FileNotFoundError:
        print("Error: fzf is not installed. Please install fzf to use this program.")
        sys.exit(1)

def select_provider():
    providers = "\n".join([
        "daddylive", "flixhq", "gomovies", "goojara", "index",
        "kissasian", "nepu", "remotestream", "ridomovies", "showbox",
        "smashystream", "vidsrc", "vidsrcto", "zoe"
    ])
    selected_provider = select_fzf("Select a provider:", providers)
    return selected_provider

def select_quality(qualities):
    selected_quality = select_fzf("Select video quality:", qualities)
    return selected_quality

def main():
    while True:
        media_id = input("Enter the movie or TV show ID (or 'quit' to exit): ")
        if media_id.lower() == 'quit':
            sys.exit(0)

        if media_id.isdigit():
            tmdb_id = int(media_id)
            selected_provider = select_provider()
            selected_media = select_fzf("Select media type:", "movie\ntv")

            if selected_media in ["movie", "tv"]:
                print(f"Fetching data for TMDB ID {tmdb_id}...")
                if selected_media == "tv":
                    season = input("Enter season number: ")
                    episode = input("Enter episode number: ")
                    media_data = fetch_media_data(selected_media, tmdb_id, season, episode, selected_provider)
                else:
                    media_data = fetch_media_data(selected_media, tmdb_id, provider=selected_provider)

                if media_data:
                    print("Media data fetched.")

                    sources = media_data.get('sources', [])
                    if sources:
                        qualities = []
                        urls = {}
                        for source in sources:
                            quality = source.get('quality', 'auto')
                            url = source.get('url')
                            qualities.append(quality)
                            urls[quality] = url

                        selected_quality = select_quality("\n".join(qualities))
                        selected_url = urls.get(selected_quality)

                        if selected_url:
                            print("Starting playback...")
                            play_video(selected_url)

                            # After video starts playing, provide additional options
                            while True:
                                if selected_media == "movie":
                                    additional_options = "rewatch\nchange quality\nsearch another\nquit"
                                else:
                                    additional_options = "previous episode\nnext episode\nrewatch\nchange quality\nsearch another show\nquit"

                                selected_option = select_fzf("Select an option:", additional_options)
                                # Perform actions based on selected option
                                if selected_option == "rewatch":
                                    play_video(selected_url)
                                elif selected_option == "change quality":
                                    selected_quality = select_quality("\n".join(qualities))
                                    selected_url = urls.get(selected_quality)
                                    if selected_url:
                                        play_video(selected_url)
                                    else:
                                        print("No valid source selected")
                                elif selected_option == "search another":
                                    break  # Break the loop and restart the main loop for another media search
                                elif selected_option == "quit":
                                    sys.exit(0)
                                elif selected_option == "previous episode":
                                    # Implement logic for previous episode (if applicable)
                                    pass
                                elif selected_option == "next episode":
                                    # Implement logic for next episode (if applicable)
                                    pass
                    else:
                        print("No sources found for the selected media")
                else:
                    print("Failed to fetch media data from FlixQuest API")
            else:
                print("Invalid media type")
        else:
            print("Invalid media ID")

if __name__ == "__main__":
    main()
