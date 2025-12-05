import os
import sys
import psycopg

DEBUG_DROPDB = True
DEBUG_UTD19_LIMIT = 1000

DBNAME = 'dbs'

if sys.platform == 'win32':
    USER = 'postgres'
    DB_PASSWORD = os.environ['DBPASSWORD']

    os.environ['PGUSER'] = USER
    os.environ['PGPASSWORD'] = DB_PASSWORD

    os.system(f'createdb -U {USER} {DBNAME}')

    conn = psycopg.connect(
        dbname=DBNAME,
        user=USER,
        password=DB_PASSWORD,
        host='localhost',
    )

else:
    USER = os.environ.get('USER')

    os.system(f'createdb {DBNAME}')

    conn = psycopg.connect(
        dbname=DBNAME,
        user=USER,
        host='localhost',
    )

try:
    DIR_DATASETS = os.environ['DIR_DATASETS']
except KeyError:
    DIR_DATASETS = ''
if not os.path.isdir(DIR_DATASETS):
    print(f'Please ensure the "DIR_DATASETS" environment variable points to the directory containing the data sets.')
    quit()

def _select(query):
    cur.execute('SELECT ' + query + ';')
    print('\n'.join([', '.join([str(a) for a in t]) for t in cur.fetchall()]))

os.system(f'createdb {DBNAME}')

cur = conn.cursor()

print()

cur.execute(''.join(open('tables.sql').readlines()))

with open(os.path.join(DIR_DATASETS, 'utd19', 'utd19_u.csv'), 'r') as f:
    f.seek(0)
    next(f)
    count = 0
    with cur.copy("COPY TrafficMeasurement FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)
            if (count := count + 1) >= DEBUG_UTD19_LIMIT:
                break

with open(os.path.join(DIR_DATASETS, 'utd19', 'detectors_public.csv'), 'r') as f:
    f.seek(0)
    next(f)
    with cur.copy("COPY DetectorLocation FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

with open(os.path.join(DIR_DATASETS, 'utd19', 'links.csv'), 'r') as f:
    f.seek(0)
    next(f)
    with cur.copy("COPY DetectorLink FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

# _select('* FROM DetectorLocation LIMIT 10')

conn.commit()
cur.close()
conn.close()

_ = '\\' if sys.platform == 'win32' else '\\\\'
os.system(f'psql -U {USER} -d {DBNAME} -c {_}dt')

if DEBUG_DROPDB:
    os.system(f'dropdb {DBNAME}')
