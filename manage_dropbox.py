import click
import dropbox
import os
import pathlib
import yaml

from os.path import basename, dirname, join, exists
from collections import defaultdict
from shutil import move
from tqdm import tqdm

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


DBX_MUSIC_DIR = '/Music'


@click.group()
@click.option('--media-dir')
@click.pass_context
def dropbox_cli(ctx, media_dir):

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

    dbx = dropbox.Dropbox(oauth_key)
    db_info_path = os.path.join(
        home,
        '.postgres_info'
    )
    db_info = None

    with open(db_info_path, 'r') as f:
        db_info = yaml.load(f)

    ctx.obj['dbx'] = dbx
    ctx.obj['get_session'] = get_session_maker(
        db_info['user'],
        db_info['password'],
        db_info['host'],
        'music'
    )


# TODO: maybe add a warning for artists that might already exist
@dropbox_cli.command()
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


@dropbox_cli.command()
@click.pass_context
def upload(ctx):

    rows = None

    with ctx.obj['get_session']() as session:
        rows = session.query(ToDropboxUpload).all()

    for r in tqdm(rows):
        dropbox_upload_file(
            ctx.job['dbx'],
            r.local_path,
            ctx.obj['get_session'],
            ctx.obj['media_dir']
        )


@dropbox_cli.command()
@click.pass_context
def download(ctx):

    remote_only_files = get_remote_only_files(
        ctx.obj['dbx'],
        ctx.obj['media_dir'],
        DBX_MUSIC_DIR
    )

    for dbx_path in tqdm(remote_only_files):
        save_path = join(
            ctx.obj['media_dir'], 
            dbx_path[1:]
        )

        os.makedirs(
            dirname(save_path), 
            exist_ok=True
        )

        dropbox_download_file(
            ctx.obj['dbx'],
            dbx_path,
            ctx.obj['get_session'],
            ctx.obj['media_dir']
        )
    

if __name__=='__main__':
    dropbox_cli(obj={})
