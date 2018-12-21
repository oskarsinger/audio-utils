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


class Incomplete(Base):

    __tablename__ = 'incomplete'

    path = Column(String, primary_key=True)
    interaction = Column(String)
    insertion_time = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'incomplete',
        'polymorphic_on': interaction
    }


class Failed(Base):

    __tablename__ = 'failed'

    path = Column(String, primary_key=True)
    error_message = Column(String)
    interaction = Column(String)
    insertion_time = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'incomplete',
        'polymorphic_on': interaction
    }


def get_incomplete(name):

    class IncompleteChild(Incomplete):

        __mapper_args__ = {
            'polymorphic_identity': name
        }
        
    return IncompleteChild


def get_failed(name):

    class FailedChild(Failed):

        __mapper_args__ = {
            'polymorphic_identity': name
        }
        
    return FailedChild


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
    song = Column(String)
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
