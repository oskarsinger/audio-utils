import datetime

from sqlalchemy.dialects.postgresql import insert
<<<<<<< HEAD
from dropbox.exceptions import DropboxException
=======
from dropbox.exceptions import ApiError
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc


def get_safe_load(do_load, incomplete_table_class, failed_table_class):

    def safe_load(dbx, path, get_session, media_dir):

        row = {
            'path': path,
<<<<<<< HEAD
            'insertion_time': datetime.datetime.now()
        }
=======
            'insertion_time'
        }
        row['insertion_time'] = datetime.datetime.now()
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc

        with get_session() as session:
            insert_if_not_exists(
                session,
                incomplete_table_class,
                **row
            )

        try:
            do_load(dbx, row, get_session, media_dir)
<<<<<<< HEAD
        except DropboxException as e:
=======
        except Exception as e:
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
            print(
                'FAILED TO LOAD {} due to {}'.format(
                    path,
                    str(e)
                )
            )
            
            row['error_message'] = str(e)

            with get_session() as session:
                insert_if_not_exists(
                    session,
                    failed_table_class,
                    **row
                )

        with get_session() as session:
            session.query(incomplete_table_class).filter(
                incomplete_table_class.path == row['path']
            ).delete()
        
    return safe_load


def insert_if_not_exists(session, mapped, **kwargs):

    table = mapped.__table__
    insert_vals = insert(table).values(**kwargs)
    query = insert_vals.on_conflict_do_nothing()
        
    session.execute(query)
