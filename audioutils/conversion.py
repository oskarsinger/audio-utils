import shutil

from pydub import AudioSegment
from pathos.multiprocessing import ProcessPool as PP

from os import listdir
from os.path import join, isfile

from .metadata import (
    get_name_and_format,
    set_metadata,
    get_metadata
)

def convert_album(
    album_dir,
    target_format,
    source,
    bitrate,
    copy_non_sound,
    num_processes):

    filenames = [fn for fn in listdir(source)
                 if isfile(join(source, fn))]
    caf = lambda fn: convert_album_file(
        fn,
        album_dir,
        target_format,
        source,
        bitrate,
        copy_non_sound)

    if num_processes > 1:
        PP(nodes=num_processes).map(
            caf,
            filenames)
    else:
        for fn in filenames:
            caf(fn)

def convert_album_file(
    filename,
    album_dir,
    target_format,
    source,
    bitrate,
    copy_non_sound):

    source_format = get_name_and_format(filename)[1]

    if source_format in {'mp3', 'flac', 'wav', 'mp4'}:
        convert_and_write_song(
            filename,
            album_dir,
            target_format,
            source,
            bitrate)
    elif copy_non_sound:
        target_file_path = join(album_dir, filename)
        source_file_path = join(source, filename)
        
        shutil.copyfile(
            source_file_path,
            target_file_path)

def convert_and_write_song(
    song_filename,
    album_dir,
    target_format,
    source,
    bitrate):

    (name, source_format) = get_name_and_format(song_filename)
    source_song_path = join(source, song_filename)
    target_fn = name + '.' + target_format
    target_song_path = join(album_dir, target_fn)

    print('Importing file:', source_song_path)

    song = AudioSegment.from_file(
        source_song_path, 
        format=source_format)
    metadata = get_metadata(source_song_path)

    print('Exporting file:', target_song_path)
    
    song.export(
        target_song_path,
        format=target_format,
        bitrate=bitrate)
    set_metadata(
        target_song_path, 
        metadata, 
        source_format)

    print()
