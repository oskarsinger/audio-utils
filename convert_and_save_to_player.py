import click
import shutil

from os import listdir
from os.path import isfile, join
from audioutils import *

@click.command()
@click.option('--source')
@click.option('--target')
@click.option('--target-format', default='mp3')
@click.option('--bitrate', default='128k')
@click.option('--copy-non-sound', default=False)
def run_tings_all_day_bb(
    source,
    target,
    target_format,
    bitrate,
    copy_non_sound):

    (artist_dir, album_dir) = get_and_make_artist_and_album_dirs(
        source,
        target)
    c_and_w_song = lambda sfn: convert_and_write_song(
        sfn,
        album_dir,
        target_format,
        source,
        bitrate)
    song_filenames = [fn for fn in listdir(source)
                      if isfile(join(source, fn))]

    for sfn in song_filenames:
        source_format = get_name_and_format(sfn)[1]
        if source_format in {'mp3', 'flac', 'wav', 'mp4'}:
            c_and_w_song(sfn)
        elif copy_non_sound:
            target_file_path = join(album_dir, sfn)
            source_file_path = join(source, sfn)
            
            shutil.copyfile(
                source_file_path,
                target_file_path)

if __name__=='__main__':
    run_tings_all_day_bb()
