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
    tracks = resource.tracks()

    for index, track in enumerate(tracks):
        track.number = index
        path = f'{directory}/{track.artist.name} - {track.name}.flac'
        print(path)
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
            print('DOWNLOADED')
            set_tags(track, path)

config = tidalapi.Config(quality=tidalapi.Quality.master)

session = tidalapi.Session(config=config)
session.login_oauth_simple()

root = sys.argv[1]
"""
playlists = session.user.playlists()
for pl in playlists:
    download(f'{root}/playlists/{pl.name}', pl)
"""
albums = session.user.favorites.albums()
for album in albums:
    download(f'{root}/albums/{album.name}', album)

