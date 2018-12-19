import datetime

from sqlalchemy.dialects.postgresql import insert
from dropbox.exceptions import ApiError

from audioutils.db.tables import (
    IncompleteDropboxDownload,
    Registry,
    TooLargeDropboxUpload
)


MAX_MEGABYTES = 150


def upload_dropbox_file(dbx, local_path, get_session, media_dir):

    lmd = len(media_dir) 
    file_size = os.stat(local_path).st_size
    megabytes = size / 10**6

    row = {
        'local_path': local_path,
        'insertion_time': datetime.datetime.now()
    }

    if megabytes > MAX_MEGABYTES:
        print(
            'FILE {} EXCEEDS MAX REQUEST SIZE WITH {}MB AND WILL NOT BE UPLOADED.' % 
            (lp, megabytes)
        )

        with get_session() as session:
            insert_if_not_exists(
                session,
                TooLargeDropboxUpload,
                **row
            )
    else:
        with get_session() as session:
            insert_if_not_exists(
                session,
                IncompleteDropboxUpload,
                **row
            )

        print('UPLOADING FILE:', local_path)

        try:
            with open(local_path, as 'rb') as f:
                dbx.files_upload(
                    f,
                    local_path[lmd:]
                )

            with get_session() as session:
                session.query(IncompleteDropboxDownload).filter(
                    IncompleteDropboxDownload.dbx_path == dbx_path
                ).delete()
        except ApiError as apie:
            print(
                'FAILED TO UPLOAD FILE {} because of {}'.format(
                    local_path, 
                    apie.user_message_text
                )
            )

            with get_session() as session:
                insert_if_not_exists(
                    session,
                    FailedDropboxUpload,
                    **row
                )


def download_dropbox_file(dbx, dbx_path, get_session, media_dir):

    row = {
        'dbx_path': dbx_path,
        'insertion_time': datetime.datetime.now()
    }

    with get_session() as session:
        insert_if_not_exists(
            session,
            IncompleteDropboxDownload,
            **row
        )

    print('DOWNLOADING FILE:', dbx_path)

    (_, response) = dbx.files_download_to_file(
        os.path.join(media_dir, dbx_path[1:]),
        dbx_path
    )
    print('RESPONSE STATUS CODE:', response.status_code)
    print('RESPONSE TEXT:', response.text)

    with get_session() as session:
        session.query(IncompleteDropboxDownload).filter(
            IncompleteDropboxDownload.dbx_path == dbx_path
        ).delete()

        row['insertion_time'] = datetime.datetime.now()

        session.query(Registry).insert(**row)


def insert_if_not_exists(session, mapped, **kwargs):

    table = mapped.__table__
    insert_vals = insert(table).values(**kwargs)
    query = insert_vals.on_conflict_do_nothing()
        
    session.execute(query)
