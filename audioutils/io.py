import os
import zipfile

from os.path import basename, splitext, join, exists

from audioutils.io import get_and_make_artist_and_album_dirs

def get_and_make_artist_and_album_dirs(artist, album, target):

    artist_dir = join(target, artist)
    album_dir = join(artist_dir, album)

    if not exists(album_dir):
        os.makedirs(album_dir)

    return (artist_dir, album_dir)


def unzip_and_save_bandcamp_album(source, target):

    name = splitext(basename(source))[0] 
    (artist, album) = name.split(' - ')
    (_, target_album_path) = get_and_make_artist_and_album_dirs(
        artist,
        album,
        target)

    with zipfile.ZipFile(source, 'r') as f:

        f.extractall(target_album_path)

    os.remove(source)

    return target_album_path
