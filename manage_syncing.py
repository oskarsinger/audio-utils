import click
import dropbox
import os
import pathlib
import yaml
import logging
import structlog
import datetime
import copy

from os.path import basename, dirname, join, exists
from collections import defaultdict
from shutil import move
from tqdm import tqdm

from audioutils.parallel import do_parallel_with_pbar
from audioutils.io import unzip_and_save_bandcamp_album
from audioutils.metadata import get_metadata
from audioutils.dropbox.utils import (
    get_remote_only_files,
    get_local_only_files
)
from audioutils.dropbox.loading import (
    dropbox_download_file,
    dropbox_upload_file
)
from audioutils.db.session import get_session_maker
from audioutils.db.tables import (
    IncompleteDropboxDownload,
    IncompleteDropboxUpload
)

logfile_name = 'manage_dropbox_log_{}.txt'.format(
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

LOGGER = structlog.get_logger()
DBX_MUSIC_DIR = '/Music'


@click.group()
@click.option('--media-dir')
@click.pass_context
def syncing_cli(ctx, media_dir):

    if media_dir[-1] == '/':
        media_dir = media_dir[:-1]

    ctx.obj['media_dir'] = media_dir 
    
    if not exists(media_dir):
        os.makedirs(media_dir)

    oauth_key = None
    home = pathlib.Path.home()
    ok_path = join(
        home, 
        '.dropbox_access_key'
    )

    with open(ok_path) as f:
        oauth_key = f.readline().strip()

    ctx.obj['oauth_key'] = oauth_key

    dbx = dropbox.Dropbox(oauth_key)
    db_info_path = os.path.join(
        home,
        '.postgres_info'
    )
    db_info = None

    with open(db_info_path, 'r') as f:
        db_info = yaml.load(f)

    db_info.update({'db': 'music'})

    ctx.obj['dbx'] = dbx
    ctx.obj['db_info'] = db_info
    ctx.obj['get_session'] = get_session_maker(
        db_info['user'],
        db_info['password'],
        db_info['host'],
        db_info['db']
    )


# TODO: maybe add a warning for artists that might already exist
@syncing_cli.command()
@click.option('--source')
@click.option('--bandcamp', default=False, type=bool)
@click.pass_context
def update(ctx, source, bandcamp):

    target = None

    if bandcamp:
        target = unzip_and_save_bandcamp_album(
            source, 
            ctx.obj['media_dir']
        )
    else:
        formats = {
            'flac',
            'mp3',
            'mp4',
            'wav'
        }

        paths = [join(root, fn) 
                 for root, _, filenames in os.walk(source)
                 for fn in filenames
                 if splitext(fn)[1][1:] in formats]

        if len(paths) == 0:
            raise Exception('No valid file formats in source dir!')
                    
        metadata = get_metadata(paths[0])
        artist = metadata['artist']
        source_dir_name = basename(dirname(source))
        target = join(
            ctx.obj['media_dir'],
            artist,
            source_dir_name
        )

        os.makedirs(target)
        move(source, target)

    new_registry_path = join(
        ctx.obj['media_dir'],
        'registry.list.new'
    )

    with open(new_registry_path, 'a') as f:
        f.write(target + '\n')


@syncing_cli.command()
@click.pass_context
def upload(ctx):

    local_only_files = get_local_only_files(
        ctx.obj['dbx'],
        ctx.obj['media_dir'],
        DBX_MUSIC_DIR
    )

    LOGGER.info(
        'local_only_files',
        local_only_files=local_only_files
    )

    with ctx.obj['get_session']() as session:
         rows = session.query(IncompleteDropboxUpload).all()
         incomplete_dbx_paths = [r.path for r in rows]

    local_only_files.extend(incomplete_dbx_paths)

    oauth_key = ctx.obj['oauth_key']
    db_info = copy.deepcopy(
        ctx.obj['db_info']
    )
    media_dir = ctx.obj['media_dir']

    def dropbox_upload_closure(local_path):

        dbx = dropbox.Dropbox(oauth_key)
        get_session = get_session_maker(
            db_info['user'],
            db_info['password'],
            db_info['host'],
            db_info['db']
        )

        dropbox_upload_file(
            dbx,
            local_path,
            get_session,
            media_dir
        )

    do_parallel_with_pbar(
        dropbox_upload_closure,
        local_only_files
    )


@syncing_cli.command()
@click.pass_context
def download(ctx):

    remote_only_files = get_remote_only_files(
        ctx.obj['dbx'],
        ctx.obj['media_dir'],
        DBX_MUSIC_DIR
    )

    with ctx.obj['get_session']() as session:
        rows = session.query(IncompleteDropboxDownload).all()
        incomplete_dbx_paths = [r.path for r in rows]

        remote_only_files.extend(incomplete_dbx_paths)

    oauth_key = ctx.obj['oauth_key']
    db_info = copy.deepcopy(
        ctx.obj['db_info']
    )
    media_dir = ctx.obj['media_dir']

    def dropbox_download_closure(dbx_path):

        dbx = dropbox.Dropbox(oauth_key)
        get_session = get_session_maker(
            db_info['user'],
            db_info['password'],
            db_info['host'],
            db_info['db']
        )

        dropbox_download_file(
            dbx,
            dbx_path,
            get_session,
            media_dir
        )

    do_parallel_with_pbar(
        dropbox_download_closure,
        remote_only_files
    )


if __name__=='__main__':
    syncing_cli(obj={})
