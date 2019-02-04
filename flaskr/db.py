import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext


def dict_factory(cursor, row):
   d = {}
   for idx, col in enumerate(cursor.description):
     d[col[0]] = row[idx]
   return d

def get_db():
    # if 'db' not in g:
    #     g.db = psycopg2.connect(
    #         current_app.config['DATABASE'],
    #         detect_types=psycopg2.PARSE_DECLTYPES
    #     )
    #     g.db.row_factory = psycopg2.Row

    # return g.db

    if 'db' not in g:
         g.db = postgres_connect()
         # g.db.row_factory = dict_factory

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


    
from configparser import ConfigParser
 
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db

def postgres_connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    finally:
        return conn
