import os
import sys

import psycopg

# Don't change the configuration values here! Use config.ini instead (see integrate.md).
CONFIG = {
    # The database name.
    'db_name': 'dbs_hs25_g10',
    # The database user.
    'db_user': 'postgres',
    # The database user's password (leave empty if no password is required).
    'db_password': '',
    # The path to the directory on your system containing the datasets.
    'dir_datasets': '',
    # Unless '', drops the <db_name> database on start.
    'debug_dropdb': '1',
    # Unless '', uses utd19_u-filtered.csv over utd19_u.csv.
    'debug_use_filtered_utd19': '',
    # Unless '', limits the number of entries read from UTD19 to the given number.
    'debug_utd19_limit': '',
    # Unless '', limits the number of entries read from Ist to the given number.
    'debug_ist_limit': '',
    # Unless '', skips indexes.sql.
    'debug_no_index': '',
    # Unless '', runs the given query (exclude the leading SELECT!) after integration.
    'debug_select': '',
    # Unless '', dumps the database after creation.
    'debug_dump': '',
}


def warn(*args, **kwargs):
    print('\033[93m[warn]', *args, **kwargs)


def connect():
    return psycopg.connect(
        dbname=CONFIG['db_name'],
        user=CONFIG['db_user'],
        host='localhost',
        password=CONFIG['db_password']
    )


# Apply configuration.

with open('config.ini', 'r') as config_ini:
    for entry in config_ini:
        if entry.startswith(';') or not entry.rstrip('\n'):
            continue
        key, value = entry.rstrip('\n').split('=')
        CONFIG[key] = value.replace(
            '~', os.environ['USERPROFILE' if sys.platform == 'win32' else 'HOME'])

# Prepare environment variables.

os.environ['PGUSER'] = CONFIG['db_user']
os.environ['PGPASSWORD'] = CONFIG['db_password']
os.environ['PGPASSWORD'] = CONFIG['db_password']
os.environ['PGPASSWORD'] = CONFIG['db_password']
