import os

from structlog import get_logger
from dropbox.exceptions import DropboxException

from audioutils.db.tables import (
    IncompleteDropboxUpload,
    FailedDropboxUpload,
    IncompleteDropboxDownload,
    FailedDropboxDownload,
    TooLargeDropboxUpload,
    SongRegistry,
    AlbumArtRegistry,
    OtherRegistry
)
from audioutils.db.utils import (
    get_safe_load,
    insert_if_not_exists
)
from audioutils.metadata import (
    get_metadata,
    MUSIC_FILETYPES
)
from audioutils.dropbox.hashing import get_dropbox_hash_check


LOGGER = get_logger()
MAX_MEGABYTES = 150


def unsafe_dropbox_upload_file(dbx, row, get_session, media_dir):

    lmd = len(media_dir) 
    file_size = os.stat(row['path']).st_size
    megabytes = size / 10**6

    LOGGER.info(
        'Uploading file to Dropbox',
        path=row['path']
    )

    if megabytes > MAX_MEGABYTES:
        row['size'] = file_size

        with get_session() as session:
            insert_if_not_exists(
                session,
                TooLargeDropboxUpload,
                **row
            )

        LOGGER.error(
            'File size exceeds Dropbox limit', 
            megabytes=megabytes,
            path=row['path']
        )
    else:
        dbx_metadata = None

        with open(row['path'], 'rb') as f:
            dbx_metadata = dbx.files_upload(
                f,
                row['path'][lmd:]
            )

        if not get_dropbox_hash_check(row['path'], dbx_metadata):
            raise DropboxException('Local and Dropbob content hashes not equal.')

        LOGGER.info(
            'File successfully uploaded to Dropbox',
            path=row['path']
        )


dropbox_upload_file = get_safe_load(
    unsafe_dropbox_upload_file,
    IncompleteDropboxUpload,
    FailedDropboxUpload,
    DropboxException
)


def unsafe_dropbox_download_file(dbx, row, get_session, media_dir):

    LOGGER.info(
        'Downloading file from Dropbox', 
        path=row['path']
    )

    local_path = os.path.join(media_dir, row['path'][1:])
    dbx_metadata = dbx.files_download_to_file(
        local_path,
        row['path']
    )

    if not get_dropbox_hash_check(local_path, dbx_metadata):
        raise DropboxException('Local and Dropbob content hashes not equal.')

    LOGGER.info(
        'File successfully downloaded from Dropbox',
        path=row['path'],
        local_path=local_path
    )

    (head, ext) = os.path.splitext(row['path'])
    row['file_type'] = ext[1:]
    registry = None

    if ext[1:] in MUSIC_FILETYPES:
        metadata = get_metadata(local_path)
        registry = SongRegistry

        print('METADATA ITEMS:', list(metadata.items()))

        row['artist'] = metadata['artist']
        row['album'] = metadata['album']
        row['album_artist'] = metadata['albumartist']
        row['song'] = metadata['song']
        row['track_number'] = metadata['tracknumber']
    elif ext[1:] in {'jpeg', 'png'} and head.endswith('cover'):
        registry = AlbumArtRegistry

        # TODO: how to get artist and album for this?
        # TODO: might have to search path for music file and pull out metadata
        row['artist'] = None
        row['album'] = None
    else:
        registry = OtherRegistry

    registry_obj = registry(**row)

    with get_session() as session:
        session.add(registry_obj)


dropbox_download_file = get_safe_load(
    unsafe_dropbox_download_file,
    IncompleteDropboxDownload,
    FailedDropboxDownload,
    DropboxException
)
