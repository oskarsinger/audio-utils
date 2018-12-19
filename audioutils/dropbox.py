import os
import glob

from os.path import join, isdir

from dropbox.files import (
    FileMetadata, 
    FolderMetadata
)


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
