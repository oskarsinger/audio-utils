import click
import dropbox
import os
import pathlib

from os.path import basename, dirname, join, exists
from collections import defaultdict
from shutil import move

from audioutils.io import unzip_and_save_bandcamp_album
from audioutils.metadata import get_metadata
from audioutils.dropbox import (
    get_all_files,
    get_full_listdir,
    get_remote_only_files,
    upload_files
)


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

    ctx.obj['dbx'] = dbx

    registry_path = join(
        media_dir, 
        'registry.list'
    )
    registry = None

    open(registry_path, 'a').close()

    with open(registry_path) as f:
        registry = [line.strip() for line in f]

    ctx.obj['registry'] = registry


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

    registry_path = join(
        ctx.obj['media_dir'],
        'registry.list'
    )
    new_registry_path = registry_path + '.new'
    new_registry = None

    if not exists(new_registry_path):
        raise Exception('No new files to upload!')

    with open(new_registry_path) as f:
        new_registry = [line.strip() for line in f]

    upload_files(
        ctx.job['dbx'],
        ctx.obj['media_dir'],
        new_registry,
        DBX_MUSIC_DIR
    )

    with open(registry_path, 'a') as f:
        f.write('\n'.join(new_registry))

    os.remove(new_registry_path)
    

@dropbox_cli.command()
@click.pass_context
def download(ctx):

    remote_only_files = get_remote_only_files(
        ctx.obj['dbx'],
        ctx.obj['media_dir'],
        DBX_MUSIC_DIR
    )

    for dbx_path in remote_only_files:
        save_path = join(
            ctx.obj['media_dir'], 
            dbx_path[1:]
        )
        print('Downloading\n\t{}\n\tto\n\t{}'.format(dbx_path, save_path))

        os.makedirs(dirname(save_path), exist_ok=True)

        ctx.obj['dbx'].files_download_to_file(
            save_path, 
            dbx_path
        )

    
if __name__=='__main__':
    dropbox_cli(obj={})
