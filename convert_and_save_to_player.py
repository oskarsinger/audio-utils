#!/usr/bin/env python

import os
import click
import datetime
import logging
import structlog
import pathlib

from audioutils.io import get_and_make_artist_and_album_dirs
from audioutils.conversion import convert_album


logfile_name = 'log_{}.txt'.format(
    datetime.datetime.now()
)
logfile_path = os.path.join(
    pathlib.Path.home(),
    '.audioutils',
    'logs',
    logfile_name
)
logging.basicConfig(
    filename=logfile_path,
    level=logging.DEBUG    
)

from structlog.stdlib import LoggerFactory
from structlog.processors import (
    JSONRenderer,
    TimeStamper
)

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[TimeStamper(), JSONRenderer()]
)

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
