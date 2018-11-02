#!/usr/bin/env python

import os

def get_and_make_artist_and_album_dirs(artist, album, target):

    artist_dir = os.path.join(target, artist)
    album_dir = os.path.join(artist_dir, album)

    if not os.path.exists(artist_dir):
        os.mkdir(artist_dir)

    if not os.path.exists(album_dir):
        os.mkdir(album_dir)

    return (artist_dir, album_dir)
