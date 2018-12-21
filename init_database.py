import click
import sqlalchemy
import yaml

@click.command()
@click.option('--db-dir')
@click.option('--db-info-path')
def run_things_all_day_bb(db_dir, db_info_path):

    db_info = None

    with open(db_info_path, 'r') as f:
        db_info = yaml.load(f)

    db_string = '''
        postgresq://{}:{}@{}:5432
    '''.format(
        db_info['user'],
        db_info['password'],
        db_info['host']
    )
    engine = sqlalchemy.create_engine(db_string)
    connection = engine.connect()

    connection.execute('commit')
    connection.execute('create database music')
    connection.close()

    
if __name__=='__main__':
    run_things_all_day_bb()
