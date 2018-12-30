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
from pathos.multiprocessing import ProcessPool

from audioutils.io import unzip_and_save_bandcamp_album
from audioutils.metadata import get_metadata
from audioutils.dropbox.utils import (
    get_all_files,
    get_full_listdir,
    get_remote_only_files
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

logfile_name = 'log_{}.txt'.format(
    datetime.datetime.now()
)
logging.basicConfig(
    filename=logfile_name,
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

    local_paths = None

    with ctx.obj['get_session']() as session:
         rows = session.query(IncompleteDropboxUpload).all()
         local_paths = [r.path for r in rows]

    for lp in tqdm(local_paths):
        dropbox_upload_file(
            ctx.job['dbx'],
            lp,
            ctx.obj['get_session'],
            ctx.obj['media_dir']
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

    pool = ProcessPool(nodes=6)
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

    print('STARTING TASKS')
    results = [pool.amap(dropbox_download_closure, [rof_path])
               for rof_path in tqdm(remote_only_files)]

    print('COMPLETING TASKS')
    total = len(results)

    with tqdm(total=total) as pbar:

        num_ready = 0

        while num_ready < total:
            
            ready = [r for r in results
                     if r.ready()]
            new_num_ready = len(ready)

            if new_num_ready > num_ready:
                pbar.update(new_num_ready - num_ready)

            num_ready = new_num_ready

if __name__=='__main__':
    syncing_cli(obj={})
