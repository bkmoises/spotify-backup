# Spotify Backup

![GitHub Workflow Status](https://github.com/bkmoises/spotify-backup/actions/workflows/main.yml/badge.svg)

## Sobre

Este projeto realiza o **backup automático das playlists do Spotify** do usuário e armazena os dados em um arquivo JSON hospedado em um [Gist](https://gist.github.com/) do GitHub. O objetivo é facilitar o versionamento e a recuperação rápida das playlists, músicas e artistas favoritos de um usuário Spotify.

O backup é executado automaticamente via **GitHub Actions** todos os dias às 3h da manhã (UTC), podendo ser disparado manualmente conforme necessário.

## Como Funciona

1. O script Python se conecta à API do Spotify utilizando autenticação via OAuth (Token de Atualização).
2. Ele coleta todas as playlists do usuário, incluindo todas as faixas (usando paginação quando necessário).
3. O arquivo `spotify-backup.json` é atualizado em um Gist privado do usuário autenticado no GitHub.
4. Logs e status são facilmente verificados pelo GitHub Actions.

## Estrutura

- `spotify_backup_gist.py` — Script principal responsável pelo backup das playlists.
- `.github/workflows/main.yml` — Workflow do GitHub Actions para execução automática e agendada do script.

## Configuração

### 1. Criar um Gist Privado

- Crie um novo gist privado em [gist.github.com](https://gist.github.com) e anote seu **ID** (aparece na URL após `/gists/`).

### 2. Registrar um Aplicativo no Spotify

- Cadastre um app em [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
- Copie o **Client ID**, **Client Secret** e gere o **Refresh Token**.

### 3. Adicionar Secrets no repositório GitHub

No seu repositório, acesse **Settings > Secrets and variables > Actions** e adicione os seguintes secrets:

- `CLIENT_ID`: Seu Client ID do Spotify.
- `CLIENT_SECRET`: Seu Client Secret do Spotify.
- `REFRESH_TOKEN`: Seu Refresh Token do Spotify.
- `USER_ID`: Seu ID de usuário do Spotify.
- `GIST_ID`: O ID do gist que irá armazenar o backup.
- `GIST_TOKEN`: Token de acesso do GitHub com permissão de escrita no gist.

### 4. Estrutura do arquivo de workflow (`.github/workflows/main.yml`)

Exemplo de configuração:

```yaml
name: Spotify Playlist Backup

on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout do repositório
        uses: actions/checkout@v4

      - name: Instalar dependências
        run: pip install requests python-dotenv

      - name: Executar backup do Spotify para o Gist
        run: python spotify_backup_script.py
        env:
          REFRESH_TOKEN: ${{ secrets.REFRESH_TOKEN }}
          GIST_TOKEN: ${{ secrets.GIST_TOKEN }}
          GIST_ID: ${{ secrets.GIST_ID }}
          USER_ID: ${{ secrets.USER_ID }}
          CLIENT_ID: ${{ secrets.CLIENT_ID }}
          CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
```

## Exemplo de Saída

O Gist atualizado conterá um JSON com estrutura semelhante a:

```json
[
  {
    "id": "playlist_id",
    "name": "Nome da Playlist",
    "tracks": [
      {
        "track_id": "id_da_musica",
        "artist": "Nome do Artista",
        "name": "Nome da Música"
      },
      ...
    ]
  },
  ...
]
```

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).

---

Projeto desenvolvido por [@bkmoises](https://github.com/bkmoises)
