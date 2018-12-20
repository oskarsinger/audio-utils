from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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


class Registry(Base):

    __table__ = 'registry'

    local_path = Column(String, primary_key=True)
    artist = Column(String)
    album = Column(String)
    album_artist = Column(String)
    song = Column(String)
    track_number = Column(Integer)
    insertion_time = Column(DateTime)
