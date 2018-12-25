import os
import glob

from os.path import join, isdir

from dropbox.files import (
    FileMetadata, 
    FolderMetadata
)
from audioutils.db.tables import (
<<<<<<< HEAD
    IncompleteDropboxUpload,
    FailedDropboxUpload,
=======
    IncompleteDropboxDownload,
    FailedDropboxUpload
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
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


MAX_MEGABYTES = 150


<<<<<<< HEAD
=======
dropbox_upload_file = get_safe_load(
    unsafe_dropbox_upload_file,
    IncompleteDropboxUpload,
    FailedDropboxUpload
)


>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
def unsafe_dropbox_upload_file(dbx, row, get_session, media_dir):

    lmd = len(media_dir) 
    file_size = os.stat(row['path']).st_size
    megabytes = size / 10**6

    if megabytes > MAX_MEGABYTES:
        error_message = 'FILE {} EXCEEDS MAX REQUEST SIZE WITH {}MB.'.format(
            row['path'], 
            megabytes
        )
        row['size'] = file_size

        with get_session() as session:
            insert_if_not_exists(
                session,
                TooLargeDropboxUpload,
                **row
            )

        raise Exception(error_message)
    else:
<<<<<<< HEAD
        with open(row['path'], 'rb') as f:
=======
        with open(row['path'], as 'rb') as f:
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
            dbx.files_upload(
                f,
                row['path'][lmd:]
            )


<<<<<<< HEAD
dropbox_upload_file = get_safe_load(
    unsafe_dropbox_upload_file,
    IncompleteDropboxUpload,
    FailedDropboxUpload
=======
dropbox_download_file = get_safe_load(
    unsafe_dropbox_download_file,
    IncompleteDropboxDownload,
    FailedDropboxDownload
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
)


def unsafe_dropbox_download_file(dbx, row, get_session, media_dir):

<<<<<<< HEAD
    print('DOWNLOADING FILE:', row['path'])

    dbx_metadata = dbx.files_download_to_file(
        os.path.join(media_dir, row['path'][1:]),
        row['path']
    )
    # TODO: implement hash stuff here
=======
    print('DOWNLOADING FILE:', dbx_path)

    (_, response) = dbx.files_download_to_file(
        os.path.join(media_dir, row['path'][1:]),
        row['path']
    )
    # TODO: probably raise exception if this goes wrong; need to learn about these status codes
    print('RESPONSE STATUS CODE:', response.status_code)
    print('RESPONSE TEXT:', response.text)

>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
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


<<<<<<< HEAD
dropbox_download_file = get_safe_load(
    unsafe_dropbox_download_file,
    IncompleteDropboxDownload,
    FailedDropboxDownload
)


=======
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
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
