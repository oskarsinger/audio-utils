import click

from audioutils.io import unzip_and_save_bandcamp_album

@click.command()
@click.option('--source')
@click.option('--target')
def run_tings_all_day_bb(
    source,
    target):

    unzip_and_save_bandcamp_album(source, target)

if __name__=='__main__':
    run_tings_all_day_bb()
