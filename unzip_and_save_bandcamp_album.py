import click

from audioutils.bandcamp import unzip_and_save_album

@click.command()
@click.option('--source')
@click.option('--target')
def run_tings_all_day_bb(
    source,
    target):

    unzip_and_save_album(source, target)

if __name__=='__main__':
    run_tings_all_day_bb()
