from sqlalchemy import Column, String, DateTime, Integer
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
    insertion_time = Column(DateTime)


class Failed(Base):

    __tablename__ 'failed'

    path = Column(String, primary_key=True)
    error_message = Column(String)
    insertion_time = Column(DateTime)


class IncompleteDropboxUpload(Incomplete):

    __tablename__ = 'incomplete_dropbox_upload'


class IncompleteDropboxDownload(Incomplete):

    __table__ = 'incomplete_dropbox_download'


class IncompleteMP3Transfer(Incomplete):

    __table__ = 'incomplete_mp3_transfer'


class FailedDropboxDownload(Failed):

    __tablename__ = 'failed_dropbox_download'


class FailedDropboxUpload(Failed):

    __tablename__ = 'failed_dropbox_upload'


class FailedMP3Transfer(Failed):

    __tablename__ = 'failed_mp3_transfer'


class TooLargeDropboxUpload(Base):

    __tablename__ = 'too_large_dropbox_upload'

    path = Column(String, primary_key=True)
    size = Column(Integer)
    insertion_time = Column(DateTime)


class SongRegistry(Base):

    __table__ = 'song_registry'

    path = Column(String, primary_key=True)
    artist = Column(String)
    album = Column(String)
    album_artist = Column(String)
    song = Column(String)
    track_number = Column(Integer)
    file_type = Column(String)
    insertion_time = Column(DateTime)


class AlbumArtRegistry(Base):

    __table__ = 'album_art_registry'

    path = Column(String, primary_key=True)
    artist = Column(String)
    album = Column(String)
    file_type = Column(String)
    insertion_time = Column(DateTime)


class AlbumRegistry(Base):
    
    __table__ = 'album_registry'

    album = Column(String, primary_key=True)
    artist = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class ArtistRegistry(Base):

    __table__ = 'artist_registry'

    artist = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class OtherRegistry(Base):

    __table__ = 'other_registry'

    path = Column(String, primary_key=True)
    file_type = Column(String)
    insertion_time = Column(DateTime)
