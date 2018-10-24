from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wavpack import WavPack
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
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
        #tags=metadata,
        bitrate=bitrate)
    set_metadata(
        target_song_path, 
        metadata, 
        source_format)

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

def set_metadata(song_path, metadata, source_format):

    f = get_name_and_format(song_path)[1]
    source_mp3 = source_format == 'mp3'
    target_mp3 = f == 'mp3'
    tags = None

    if source_mp3 and target_mp3:
        tags = ID3(song_path)
        
        for t in metadata.values():
            tags.add(t)

    elif not source_mp3 and target_mp3:
        tags = EasyID3(song_path)
        metadata = {k : v for k, v in metadata.items()
                    if k in EasyID3.valid_keys.keys()}

        for k, v in metadata.items():
            tags[k] = v

    elif source_mp3 and not target_mp3:
        tags = ext2class[f](song_path)

        for k, v in metadata.items():
            tags[k] = v.text 

    else:
        tags = ext2class[f](song_path)

        for k, v in metadata.items():
            tags[k] = v

    tags.save()

def get_metadata(song_path):

    f = get_name_and_format(song_path)[1]
    tags = dict(ext2class[f](song_path).tags)

    if not f == 'mp3':
        tags = {k : v[0] for (k,v) in tags.items()}
    
    return tags
