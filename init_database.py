<<<<<<< HEAD
import os
import click
import sqlalchemy
import pathlib
=======
import click
import sqlalchemy
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
import yaml

from sqlalchemy.exc import ProgrammingError

from audioutils.db.tables import create_tables

@click.command()
<<<<<<< HEAD
def run_things_all_day_bb():

    home = pathlib.Path.home()
    db_info_path = os.path.join(
        home,
        '.postgres_info'
    )
=======
@click.option('--db-info-path')
def run_things_all_day_bb(db_info_path):

>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
    db_info = None

    with open(db_info_path, 'r') as f:
        db_info = yaml.load(f)

    db_string = '''
        postgresql://{}:{}@{}:5432
    '''.format(
        db_info['user'],
        db_info['password'],
        db_info['host']
    ).strip()
    engine = sqlalchemy.create_engine(
        db_string,
        echo=True
    )

    try:
        connection = engine.connect()

        connection.execute('commit')
        connection.execute(
            'create database {}'.format(
<<<<<<< HEAD
                'music'
=======
                db_info['db_name']
>>>>>>> 295ee43f968e00deb35c03fa31d2d6a0767110dc
            )
        )
        connection.close()
    except ProgrammingError as e:
        print(e)

    table_exists = create_tables(engine)

    for k_and_v in table_exists.items():
        print(
            'CREATE TABLE {} SUCCESSFUL: {}'.format(
                *k_and_v
            )
        )
    
if __name__=='__main__':
    run_things_all_day_bb()
