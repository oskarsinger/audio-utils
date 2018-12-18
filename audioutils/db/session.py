from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from audioutils.db.tables import Base


def get_session_maker(user, password, host, db):

    engine_string = ''.join([
        'postgresql://',
        user,
        ':',
        password,
        '@',
        host,
        ':5432',
        '/',
        db
    ])
    engine = create_engine(
        engine_string,
        poolclass=QueuePool,
        pool_timeout=300,
        pool_size=100,
        max_overflow=100,
        echo_pool=True
    )

    # TODO: figure out a better way to do this
    Base.metadata.create_all(bind=engine)

    get_session_no_cm = sessionmaker(bind=engine)

    @contextmanager
    def get_session():
        
        session = get_session_no_cm()
        
        try:
            yield session
        finally:
            session.commit()
            session.close()

    return get_session
