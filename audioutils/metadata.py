#!/usr/bin/env python

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wavpack import WavPack
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

from os import mkdir, system
from os.path import join, splitext

ext2class = {
    'flac': FLAC,
    'mp3': MP3,
    'mp4': MP4,
    'wav': WavPack
}

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
