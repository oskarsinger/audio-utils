import os
import glob

from os.path import join, isdir

from dropbox.files import (
    FileMetadata, 
    FolderMetadata
)
from dropbox.exceptions import DropboxException
from structlog import get_logger

from audioutils.db.tables import (
    IncompleteDropboxUpload,
    FailedDropboxUpload,
    IncompleteDropboxDownload,
    FailedDropboxDownload,
    TooLargeDropboxUpload,
    SongRegistry,
    AlbumArtRegistry
)
from audioutils.db.utils import (
    get_safe_load,
    insert_if_not_exists
)
from audioutils.metadata import (
    get_metadata,
    MUSIC_FILETYPES
)


LOGGER = get_logger()
MAX_MEGABYTES = 150


def unsafe_dropbox_upload_file(dbx, row, get_session, media_dir):

    lmd = len(media_dir) 
    file_size = os.stat(row['path']).st_size
    megabytes = size / 10**6

    LOGGER.msg(
        'Uploading file',
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

        LOGGER.msg(
            'File size exceeds Dropbox limit', 
            megabytes=megabytes,
            path=row['path']
        )
    else:
        with open(row['path'], 'rb') as f:
            metadata = dbx.files_upload(
                f,
                row['path'][lmd:]
            )

        LOGGER.msg(
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

    LOGGER.msg(
        'Downloading file', 
        path=row['path']
    )

    local_path = os.path.join(media_dir, row['path'][1:])
    dbx_metadata = dbx.files_download_to_file(
        local_path,
        row['path']
    )


    if not get_hash_check(local_path, dbx_metadata):
        raise DropboxException('Local and Dropbob content hashes not equal.')

    LOGGER.msg(
        'File successfully downloaded from Dropbox',
        path=row['path']
    )

    (head, ext) = os.path.splitext(row['path'])
    row['file_type'] = ext[1:]
    registry = None

    if ext[1:] in MUSIC_FILETYPES:
        metadata = get_metadata(row['path'])
        registry = SongRegistry

        row['artist'] = metadata['artist']
        row['album'] = metadata['album']
        row['album_artist'] = metadata['album_artist']
        row['song'] = metadata['song']
        row['track_number'] = metadata['track_number']
    elif ext[1:] in {'jpeg', 'png'} and head.endswith('cover'):
        registry = AlbumArtRegistry

        # TODO: how to get artist and album for this?
        # TODO: might have to search path for music file and pull out metadata
        row['artist'] = None
        row['album'] = None
    else:
        registry = OtherRegistry

    with get_session() as session:
        session.query(registry).insert(**row)


dropbox_download_file = get_safe_load(
    unsafe_dropbox_download_file,
    IncompleteDropboxDownload,
    FailedDropboxDownload,
    DropboxException
)


def get_hash_check(local_path, dbx_metadata):

    dbx_hash = dbx_metadata.content_hash
    local_hash = None

    return dbx_hash == local_hash


def get_remote_only_files(dbx, media_dir, dbx_dir):

    search_path = join(
        media_dir,
        '**',
        '*'
    )
    local_paths = glob.glob(
        search_path,
        recursive=True
    )
    local_paths_lower = [p.lower()[len(media_dir):] 
                         for p in local_paths]
    dbx_files = get_all_files(dbx, dbx_dir)
    dbx_paths = [f.path_lower for f in dbx_files]

    return set(dbx_paths).difference(local_paths_lower)


def get_all_files(dbx, root):

    path2files = {}
    listdir = get_full_listdir(
        dbx, 
        root, 
        recursive=True
    )

    return [metadata for metadata in listdir
            if type(metadata) == FileMetadata]


def get_full_listdir(dbx, root, recursive=False):

    listdir = dbx.files_list_folder(root, recursive=recursive)
    entries = listdir.entries

    while listdir.has_more:
        listdir = dbx.files_list_folder_continue(listdir.cursor)

        entries.extend(listdir.entries)

    return entries
