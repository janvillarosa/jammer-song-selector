import os
import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials
from service.playlist_seed import PLAYLIST_SEED

CLIENT_ID = "2cc3f44677c74b45a0813be25575c494"
CLIENT_SECRET = os.environ["SPOTIFY_SECRET"]
SP = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                        client_secret=CLIENT_SECRET))

def _get_random_playlist():
    return random.choice(list(PLAYLIST_SEED.values()))

def _get_playlist_size(playlist_id):
    playlist_data = SP.playlist_items(playlist_id)
    size = playlist_data["total"]
    return size

def _call_spotify_for_track():
    random_playlist_id = _get_random_playlist()
    playlist_size = _get_playlist_size(random_playlist_id)
    random_offset = random.randrange(1, playlist_size)
    return SP.playlist_items(random_playlist_id, fields=None, limit=1, offset=random_offset, market=None, additional_types=('track',))

def _parse_spotify_results(results):
    track_obj = {}
    for item in results["items"]:
        track = item["track"]
        album = track["album"]
        artists = track["artists"]

        track_obj["id"] = track["id"]
        track_obj["song"] = track["name"]
        track_obj["album"] = album["name"]
        track_obj["preview_url"] = None
        track_obj["artists"] = []
        
        for artist in artists:
            track_obj["artists"].append(artist["name"])
        if track["preview_url"]:
            track_obj["preview_url"] = track["preview_url"]
        
        album_art_highest_res = 0
        for album_art in album["images"]:
            #Get the highest res album art available
            if album_art["height"] > album_art_highest_res:
                track_obj["album_art_url"] = album_art["url"]
                album_art_highest_res = album_art["height"]
    return track_obj

def get_random_song():
    random_song = _parse_spotify_results(_call_spotify_for_track())
    while not random_song["preview_url"]:
        random_song = _parse_spotify_results(_call_spotify_for_track())
    return random_song
    