import os
import sys
import requests
import tidalapi
import music_tag

def set_tags(track, path):
    print('Setting tags')
    try:
        f = music_tag.load_file(path)
        f['artist'] = track.artist.name
        f['album'] = track.album.name
        f['tracktitle'] = track.name
        f['tracknumber'] = track.number
        try:
            f['year'] = track.album.release_date.year
        except AttributeError:
            pass
        f.save()
    except Exception as e:
        print(e)

def download(directory, resource):
    try:
        tracks = resource.tracks()
    except requests.exceptions.HTTPError as e:
        print(e)
        return
    if len(tracks) >= 100:
        print('Too many tracks, skipping')
        return

    for index, track in enumerate(tracks):
        track.number = index + 1
        track_name = track.name.replace('/', '|')
        path = f'{directory}/{track.artist.name} - {track_name}.flac'
        if os.path.exists(path):
            set_tags(track, path)
            continue

        try:
            r = requests.get(track.get_url())
        except requests.exceptions.HTTPError as e:
            print(e)
            continue
        try:
            os.makedirs(directory)
        except OSError:
            pass
        try:
            with open(path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print(f'Failed to save: {path} {e}')
        else:
            print(f'DOWNLOADED {path}')
            set_tags(track, path)

if len(sys.argv) < 2:
    print("Need 2 parameters <path> <mask>")
    exit(1)

config = tidalapi.Config(quality=tidalapi.Quality.master)

session = tidalapi.Session(config=config)
session.login_oauth_simple()

root = sys.argv[1]
mask = int(sys.argv[2])

if mask & 0b100:
    for pl in session.user.playlists():
        download(f'{root}/playlists/{pl.name}', pl)

if mask & 0b010:
    for album in session.user.favorites.albums():
        download(f'{root}/albums/{album.name}', album)

if mask & 0b001:
    download(f'{root}/tracks', session.user.favorites)

