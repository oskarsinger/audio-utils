import click
import sqlalchemy
import yaml

from audioutils.db.tables import create_tables

@click.command()
@click.option('--db-dir')
@click.option('--db-info-path')
def run_things_all_day_bb(db_dir, db_info_path):

    db_info = None

    with open(db_info_path, 'r') as f:
        db_info = yaml.load(f)

    db_string = '''
        postgresq://{}@{}:5432
    '''.format(
        db_info['user'],
        db_info['host']
    )
    engine = sqlalchemy.create_engine(
        db_string,
        echo=True
    )
    connection = engine.connect()

    connection.execute('commit')
    connection.execute(
        'create database {}'.format(
            db_info['db_name']
        )
    )
    connection.close()

    table_exists = create_tables(engine)

    for k_and_v in table_exists.items():
        print(
            'CREATE TABLE {} SUCCESSFUL: {}'.format(
                *k_and_v
            )
        )
    
if __name__=='__main__':
    run_things_all_day_bb()
