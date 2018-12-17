import os

from os.path import join, isdir

from dropbox.files import (
    FileMetadata, 
    FolderMetadata
)


MAX_MEGABYTES = 150


def upload_files(dbx, media_dir, local_paths, dbx_dir):
    
    lmd = len(media_dir)

    for lp in local_paths:
        size = os.stat(lp).st_size
        megabytes = size / 10**6

        if megabytes > MAX_MEGABYTES:
            print(
                'FILE {} EXCEEDS MAX REQUEST SIZE WITH {}MB AND WILL NOT BE UPLOADED.' % 
                (lp, megabytes)
            )
        else:
            with open(lp, 'rb') as f:
                dbx.files_upload(
                    f,
                    lp[lmd:]
                )


def get_remote_only_files(dbx, media_dir, dbx_dir):

    search_path = join(
        media_dir,
        '**',
        '*'
    )
    local_paths = glog.glob(
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
    listdir = get_full_listdir(dbx, current, recursive=True)

    return [metadata for metadata in listdir
            if type(metadata) == FileMetadata]


def get_full_listdir(dbx, root, recursive=False):

    listdir = dbx.files_list_folder(root, recursive=recursive)
    entries = listdir.entries

    while listdir.has_more:
        listdir = dbx.files_list_folder_continue(listdir.cursor)

        entries.extend(listdir.entries)

    return entries
