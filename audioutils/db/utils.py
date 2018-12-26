import datetime

from sqlalchemy.dialects.postgresql import insert
from structlog import get_logger


LOGGER = get_logger()


def get_safe_load(do_load, incomplete_table_class, failed_table_class, exception_class):

    def safe_load(dbx, path, get_session, media_dir):

        row = {
            'path': path,
            'insertion_time': datetime.datetime.now()
        }

        with get_session() as session:
            insert_if_not_exists(
                session,
                incomplete_table_class,
                **row
            )

        try:
            do_load(dbx, row, get_session, media_dir)
        except exception_class as e:
            row['error_message'] = str(e)

            LOGGER.error(
                'Failed to load',
                **row
            )
            
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
