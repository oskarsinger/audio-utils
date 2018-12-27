from sqlalchemy import (
    Column, 
    String, 
    DateTime, 
    Integer,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def create_tables(engine):

    Base.metadata.create_all(bind=engine)

    tables = Base.metadata.tables

    return {n: engine.has_table(n)
            for n in tables.keys()}


def get_snake2camel(snake):

    tokens = snake.split('_')
    capitalized = [t[0].upper() + t[1:]
                   for t in tokens]

    return ''.join(capitalized)


def get_incomplete(name):

    attrs = {
        'path': Column(String, primary_key=True),
        'insertion_time': Column(DateTime),
        '__tablename__': name
    }
    class_name = get_snake2camel(name)
        
    return type(class_name, (Base,), attrs)


def get_failed(name):

    attrs = {
        'path': Column(String, primary_key=True),
        'error_message': Column(String),
        'insertion_time': Column(DateTime),
        '__tablename__': name
    }
    class_name = get_snake2camel(name)
        
    return type(class_name, (Base,), attrs)


IncompleteDropboxUpload = get_incomplete(
    'incomplete_dropbox_upload'
)
IncompleteDropboxDownload = get_incomplete(
    'incomplete_dropbox_download'
)
IncompleteMP3Transfer = get_incomplete(
    'incomplete_mp3_transfer'
)


FailedDropboxDownload = get_failed(
    'failed_dropbox_download'
)
FailedDropboxUpload = get_failed(
    'failed_dropbox_upload'
)
FailedMP3Transfer = get_failed(
    'failed_mp3_transfer'
)


class TooLargeDropboxUpload(Base):

    __tablename__ = 'too_large_dropbox_upload'

    path = Column(String, primary_key=True)
    size = Column(Integer)
    insertion_time = Column(DateTime)


class SongRegistry(Base):

    __tablename__ = 'song_registry'

    path = Column(String, primary_key=True)
    artist = Column(String)
    album = Column(String)
    album_artist = Column(String)
    title = Column(String)
    track_number = Column(Integer)
    file_type = Column(String)
    insertion_time = Column(DateTime)


class AlbumArtRegistry(Base):

    __tablename__ = 'album_art_registry'

    path = Column(String, primary_key=True)
    artist = Column(String)
    album = Column(String)
    file_type = Column(String)
    insertion_time = Column(DateTime)


class AlbumRegistry(Base):
    
    __tablename__ = 'album_registry'

    album = Column(String, primary_key=True)
    artist = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class ArtistRegistry(Base):

    __tablename__ = 'artist_registry'

    artist = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class OtherRegistry(Base):

    __tablename__ = 'other_registry'

    path = Column(String, primary_key=True)
    file_type = Column(String)
    insertion_time = Column(DateTime)
