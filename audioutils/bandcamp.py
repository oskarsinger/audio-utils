import os
import zipfile

from os.path import basename, splitext

from .io import get_and_make_artist_and_album_dirs

def unzip_and_save_album(source, target):

    name = splitext(basename(source))[0] 
    (artist, album) = name.split(' - ')
    (_, target_album_path) = get_and_make_artist_and_album_dirs(
        artist,
        album,
        target)

    with zipfile.ZipFile(source, 'r') as f:

        f.extractall(target_album_path)
