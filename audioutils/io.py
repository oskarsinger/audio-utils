import os

def get_and_make_artist_and_album_dirs(artist, album, target):

    target_path = os.path.join(
        target,
        artist,
        album)
    target_path_str = '\\ '.join(
        target_path.split())

    os.system('mkdir -p ' + target_path_str)

    album_dir = target_path
    artist_dir_items = target_path.split('/')[:-1]
    artist_dir = os.path.join(*artist_dir_items)

    return (artist_dir, album_dir)

