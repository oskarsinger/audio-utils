import click
import dropbox
import os
import pathlib

from collection import defaultdict

@click.group()
@click.option('--media-dir')
@click.pass_context
def dropbox_cli(ctx, media_dir):

    ctx.obj['media_dir'] = media_dir 
    
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    oauth_key = None
    home = pathlib.Path.home()
    ok_path = os.path.join(
        home, 
        '.dropbox_access_key'
    )

    with open(ok_path) as f:
        oauth_key = f.readline().strip()

    dbx = dropbox.Dropbox(oauth_key)

    ctx.obj['dbx'] = dbx

    registry_path = os.path.join(
        media_dir, 
        'registry.list'
    )
    registry = defaultdict(lambda: [])

    os.open(registry_path, 'a').close()

    with open(registry_path) as f:

        artist = None
        
        for line in f:
            stripped = line.strip()

            if stripped.startswith('-'):
                registry[artist].append(stripped[2:])
            else:
                artist = stripped[:-1]

    ctx.obj['registry'] = registry


@dropbox_cli.command()
@click.pass_context
def upload(ctx):

    # TODO: find everything that is in folder but not in registry
    # TODO: upload these things to dropbox
    

@dropbox_cli.command()
@click.pass_context
def download(ctx):

    
if __name__=='__main__':
    dropbox_cli(obj={})
