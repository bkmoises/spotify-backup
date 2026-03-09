import os
import json
import time
import logging
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_file_from_gist(gist_id: str, gist_token: str, file_name: str) -> Optional[Dict]:
    headers = {'Authorization': f'token {gist_token}'}
    url = f'https://api.github.com/gists/{gist_id}'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        files = data.get('files', {})
        if file_name in files:
            return json.loads(files[file_name]['content'])
        else:
            logging.warning(f"Arquivo não encontrado: {file_name}")
            return {}
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao fazer a requisição: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar o JSON: {e}")
    except KeyError as e:
        logging.error(f"Erro: Chave ausente na resposta: {e}")
    return None

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

    REFRESH_TOKEN      = os.getenv('REFRESH_TOKEN')
    GIST_TOKEN         = os.getenv('GIST_TOKEN')
    GIST_ID_DATABASE   = os.getenv('GIST_ID_DATABASE')
    GIST_FILE_DATABASE = 'spotify-backup.json'
    USER_ID            = os.getenv('USER_ID')
    CLIENT_ID          = os.getenv('CLIENT_ID')
    CLIENT_SECRET      = os.getenv('CLIENT_SECRET')

    ACCESS_TOKEN = get_access_token_from_refresh(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)

    spotify_api = 'https://api.spotify.com/v1'
    playlist_url = f'{spotify_api}/users/{USER_ID}/playlists'
    gist_url = f"https://api.github.com/gists/{GIST_ID_DATABASE}"

    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    r = requests.get(playlist_url, headers=headers)
    r.raise_for_status()
    user_playlists = r.json()

    playlists = [{"id": p['id'], "name": p['name']} for p in user_playlists.get('items', [])]

    for playlist in playlists:
        url = f'{spotify_api}/playlists/{playlist["id"]}/tracks'
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        playlist_tracks = r.json()
        tracks = [
            {
                'track_id': t['track']['id'],
                'artist': t['track']['artists'][0]['name'],
                'name': t['track']['name']
            }
            for t in playlist_tracks.get('items', []) if t.get('track')
        ]
        playlist['tracks'] = tracks

    content = json.dumps(playlists, indent=2, ensure_ascii=False)
    description = f'Backup realizado em {time.strftime("%d/%m/%Y as %H:%M:%S", time.localtime())}'
    gist_headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    data = {"description": description, "files": {GIST_FILE_DATABASE: {"content": content}}}

    response = requests.patch(gist_url, headers=gist_headers, json=data)

    if response.status_code == 200:
        logging.info("Backup realizado com sucesso!")
    else:
        logging.error(f"Falha ao realizar o backup: {response.status_code}, {response.text}")

if __name__ == '__main__':
    main()
