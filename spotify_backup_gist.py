import os
import json
import time
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_access_token_from_refresh(refresh_token, client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def main():
    load_dotenv()
    
    GIST_ID       = os.getenv('GIST_ID')
    GIST_TOKEN    = os.getenv('GIST_TOKEN')
    USER_ID       = os.getenv('USER_ID')
    CLIENT_ID     = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

    spotify_api   = 'https://api.spotify.com/v1'
    playlist_url  = f'{spotify_api}/users/{USER_ID}/playlists'
    gist_url      = f"https://api.github.com/gists/{GIST_ID}"
    gist_file     = 'spotify-backup.json'

    ACCESS_TOKEN  = get_access_token_from_refresh(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
        
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    user_playlists = requests.get(playlist_url, headers=headers).json()

    playlists = [{"id": playlist['id'], "name": playlist['name']} for playlist in user_playlists['items']]
    for playlist in playlists:
        playlist_tracks = []
        url = f"{spotify_api}/playlists/{playlist['id']}/tracks"
        while url:
            playlist_node = requests.get(url, headers=headers).json()
            playlist_tracks.extend(playlist_node.get("items", []))
            url = playlist_node.get("next")
        
        playlist['tracks'] = [{'track_id': track['track']['id'], 'artist': track['track']['artists'][0]['name'], 'name': track['track']['name']} for track in playlist_tracks]
        
    content = json.dumps(playlists, indent=2)
    description = f'Backup realizado em {time.strftime("%d/%m/%Y as %H:%M:%S", time.localtime())}'
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"description": description, "files": {gist_file: {"content": content}}}
    
    response = requests.patch(gist_url, headers=headers, json=data)

    if response.status_code == 200:
        logging.info("Backup realizado com sucesso!")
    else:
        logging.error(f"Falha ao realizar o backup: {response.status_code}, {response.text}")

if __name__ == '__main__':
    main()
