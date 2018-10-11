import click
import shutil

from pydub import AudioSegment
from os import listdir, mkdir
from os.path import isfile, join, splitext, exists

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
    bitrate):

    (artist, album) = source.split('/')[-2:]
    artist_dir = join(target, artist)
    album_dir = join(artist_dir, album)

    if not exists(artist_dir):
        mkdir(artist_dir)

    if not exists(album_dir):
        mkdir(album_dir)

    song_filenames = [fn for fn in listdir(source)
                      if isfile(join(source, fn))]

    for sfn in song_filenames:

        source_song_path = join(source, sfn)
        (name, source_format) = splitext(sfn)
        source_format = source_format[1:]

        if source_format in {'mp3', 'flac', 'wav', 'ogg'}:
            target_fn = name + '.' + target_format
            target_song_path = join(album_dir, target_fn)

            print('Importing file:', source_song_path)

            song = AudioSegment.from_file(
                source_song_path, 
                format=source_format)

            print('Exporting file:', target_song_path)
            
            song.export(
                target_song_path, 
                format=target_format,
                bitrate=bitrate)

            print()
        elif copy_non_sound:
            target_file_path = join(album_dir, sfn)
            source_file_path = join(source, sfn)
            
            shutil.copyfile(
                source_file_path,
                target_file_path)


if __name__=='__main__':
    run_tings_all_day_bb()
