from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class IncompleteDropboxDownload(Base):

    __tablename__ = 'incomplete_dropbox_download'

    dbx_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class IncompleteDropboxUpload(Base):

    __tablename__ = 'incomplete_dropbox_upload'

    local_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class FailedDropboxUpload(Base):

    __tablename__ = 'failed_dropbox_upload'

    local_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class IncompleteMP3Transfer(Base):

    __tablename__ = 'incomplete_mp3_transfer'

    local_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class TooLargeDropboxUpload(Base):

    __tablename__ = 'too_large_dropbox_upload'

    dbx_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class Registry(Base):

    __table__ = 'registry'

    local_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)


class ToDropboxUpload(Base):

    __table__ = 'to_dropbox_upload'

    dbx_path = Column(String, primary_key=True)
    insertion_time = Column(DateTime)
