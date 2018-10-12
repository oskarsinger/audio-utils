from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wavpack import WavPack
from pydub import AudioSegment

from os import mkdir
from os.path import join, splitext, exists

ext2class = {
    'flac': FLAC,
    'mp3': MP3,
    'mp4': MP4,
    'wav': WavPack
}

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
        tags=metadata,
        bitrate=bitrate)

    print()

def get_and_make_artist_and_album_dirs(source, target):

    (artist, album) = source.split('/')[-2:]
    artist_dir = join(target, artist)
    album_dir = join(artist_dir, album)

    if not exists(artist_dir):
        mkdir(artist_dir)

    if not exists(album_dir):
        mkdir(album_dir)

    return (artist_dir, album_dir)

def get_name_and_format(song_path):

    (name, ext) = splitext(song_path)
    song_format = ext[1:]

    return (name, song_format)

def get_metadata(song_path):

    f = get_name_and_format(song_path)[1]
    tag_dict = dict(ext2class[f](song_path).tags)
    unlisted = {k : v[0] for (k,v) in tag_dict.items()}
    
    return unlisted
