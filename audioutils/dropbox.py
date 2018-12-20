import os
import glob

from os.path import join, isdir

from dropbox.files import (
    FileMetadata, 
    FolderMetadata
)
from audioutils.db.tables import (
    IncompleteDropboxDownload,
    FailedDropboxUpload
    IncompleteDropboxDownload,
    FailedDropboxDownload,
    Registry,
    TooLargeDropboxUpload
)
from audioutils.db.utils import (
    get_safe_load,
    insert_if_not_exists
)


MAX_MEGABYTES = 150


dropbox_upload_file = get_safe_load(
    IncompleteDropboxUpload,
    FailedDropboxUpload
)


def unsafe_dropbox_upload_file(dbx, local_path, get_session, media_dir):

    lmd = len(media_dir) 
    file_size = os.stat(local_path).st_size
    megabytes = size / 10**6

    row = {
        'local_path': local_path,
        'insertion_time': datetime.datetime.now()
    }

    if megabytes > MAX_MEGABYTES:
        error_message = 'FILE {} EXCEEDS MAX REQUEST SIZE WITH {}MB.'.format(
            lp, 
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
        with open(local_path, as 'rb') as f:
            dbx.files_upload(
                f,
                local_path[lmd:]
            )


dropbox_download_file = 


def unsafe_dropbox_download_file(dbx, dbx_path, get_session, media_dir):

    row = {
        'dbx_path': dbx_path,
        'insertion_time': datetime.datetime.now()
    }

    print('DOWNLOADING FILE:', dbx_path)

    (_, response) = dbx.files_download_to_file(
        os.path.join(media_dir, dbx_path[1:]),
        dbx_path
    )
    # TODO: probably raise exception if this goes wrong; need to learn about these status codes
    print('RESPONSE STATUS CODE:', response.status_code)
    print('RESPONSE TEXT:', response.text)

    # TODO: this needs to pull out music file metadata and accordingly populate db row
    if is_music_file:

        with get_session() as session:
            session.query(Registry).insert(**row)


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
