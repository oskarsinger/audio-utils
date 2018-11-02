#!/usr/bin/env python

import click

from audioutils.io import get_and_make_artist_and_album_dirs
from audioutils.conversion import convert_album

@click.command()
@click.option('--source')
@click.option('--target')
@click.option('--target-format', default='mp3')
@click.option('--bitrate', default='128k')
@click.option('--copy-non-sound', default=False)
@click.option('--num-processes', default=1)
def run_tings_all_day_bb(
    source,
    target,
    target_format,
    bitrate,
    copy_non_sound,
    num_processes):

    (artist, album) = source.split('/')[-2:]
    (artist_dir, album_dir) = get_and_make_artist_and_album_dirs(
        artist,
        album,
        target)
    convert_album(
        album_dir,
        target_format,
        source,
        bitrate,
        copy_non_sound,
        num_processes)

if __name__=='__main__':
    run_tings_all_day_bb()
