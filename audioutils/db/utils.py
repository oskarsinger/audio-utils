import datetime

from sqlalchemy.dialects.postgresql import insert

from audioutils.db.tables import (
    IncompleteDownload,
    Registry
)


def download_dropbox_file(dbx, dbx_path, get_session, media_dir):

    row = {
        'dbx_path': dbx_path,
        'insertion_time': datetime.datetime.now()
    }

    # TODO: check if doc is in 
    with get_session() as session:
        insert_if_not_exists(
            session,
            IncompleteDownload,
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
        session.query(IncompleteDownload).filter(
            IncompleteDownload.dbx_path == dbx_path
        ).delete()

        row['insertion_time'] = datetime.datetime.now()

        session.query(Registry).insert(**row)


def insert_if_not_exists(session, mapped, **kwargs):

    table = mapped.__table__
    insert_vals = insert(table).values(**kwargs)
    query = insert_vals.on_conflict_do_nothing()
        
    session.execute(query)
