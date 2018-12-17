import os

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
    result_paths = glog.glob(
        search_path,
        recursive=True
    )
    local_dirs = {p for p in result_paths
                  if isdir(p)}
    dbx_dirs = get_all_dirs(dbx, dbx_dir)
    remote_only_dirs = set(dbx_dirs).difference(local_dirs)

    remote_only_files = {}

    for d in remote_only_dirs:
        all_files_d = get_all_files(dbx, d)

        remote_only_files.update(all_files_d)

    return remote_only_files


def get_all_dirs(dbx, root):

    queue = [root]
    paths = []

    while len(queue) > 0:
        current = queue[0]
        listdir = get_full_listdir(dbx, current)
        dirs = [metadata for metadata in listdir
                if type(metadata) == FolderMetadata]
        current_paths = [join(current, d.name) for d in dirs]

        paths.extend(current_paths)
        queue.extend(current_paths)

        queue = queue[1:]

    return paths


def get_all_files(dbx, root):

    queue = [root]
    path2files = {}

    while len(queue) > 0:
        current = queue[0]
        listdir = get_full_listdir(dbx, current)
        files = [metadata for metadata in listdir
                 if type(metadata) == FileMetadata]
        dirs = [metadata for metadata in listdir
                if type(metadata) == FolderMetadata]

        path2files[current] = files
        queue.extend([
            os.path.join(current, d.name) for d in dirs
        ])

        queue = queue[1:]

    return path2files


def get_full_listdir(dbx, root):

    listdir = dbx.file_list_folder(root) 
    entries = listdir.entries

    while listdir.has_more:
        listdir = dbx.files_list_folder_continue(listdir.cursor)

        entries.extend(listdir.entries)

    return entries
