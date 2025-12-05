import os
import sys
import psycopg
from pathlib import Path

DEBUG_DROPDB = True
DEBUG_UTD19_LIMIT = 1_000
DEBUG_IST_LIMIT = 10

DBNAME = 'dbs'

if sys.platform == 'win32':
    USER = 'postgres'
    DB_PASSWORD = os.environ['DBPASSWORD']

    os.environ['PGUSER'] = USER
    os.environ['PGPASSWORD'] = DB_PASSWORD
    
    if DEBUG_DROPDB:
        os.system(f'dropdb {DBNAME}')

    os.system(f'createdb -U {USER} {DBNAME}')

    conn = psycopg.connect(
        dbname=DBNAME,
        user=USER,
        password=DB_PASSWORD,
        host='localhost',
    )
else:
    USER = os.environ.get('USER')
    
    if DEBUG_DROPDB:
        os.system(f'dropdb {DBNAME}')

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
    print('\n'.join(['\t'.join([str(a) for a in t]) for t in cur.fetchall()]))

def skip_header(f):
    f.seek(0)
    next(f)

cur = conn.cursor()

print()

cur.execute(''.join(open('tables.sql').readlines()))

with open(os.path.join(DIR_DATASETS, 'utd19', 'utd19_u.csv'), 'r', encoding='utf-8') as f:
    skip_header(f)
    count = 0
    with cur.copy("COPY TrafficMeasurement FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)
            if DEBUG_UTD19_LIMIT is not None and (count := count + 1) >= DEBUG_UTD19_LIMIT:
                break

with open(os.path.join(DIR_DATASETS, 'utd19', 'detectors_public.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY DetectorLocation FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

with open(os.path.join(DIR_DATASETS, 'utd19', 'links.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY DetectorLink FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

dir_dataset_ist = os.path.join(DIR_DATASETS, 'ist-filtered')
count = 0
for name in Path(dir_dataset_ist).glob('*.csv'):
    path = os.path.join(dir_dataset_ist, name)
    assert os.path.isfile(path)
    with open(path, 'r', encoding = 'utf-8') as f:
        # ist-filtered has no headers.
        with cur.copy("COPY Zugfahrt FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
            for line in f:
                copy.write(line)
    if DEBUG_IST_LIMIT is not None and (count := count + 1) >= DEBUG_IST_LIMIT:
        break

for citycode in ['BAS', 'LUZ', 'SMA']:
    with open(os.path.join(DIR_DATASETS, 'weather', 'data', f'nbcn-daily_{citycode}_previous.csv'), 'r', encoding = 'utf-8') as f:
        skip_header(f)
        with cur.copy("COPY Weather FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
            for line in f:
                copy.write(line)

with open(os.path.join(DIR_DATASETS, 'anzahl-sbb-bahnhofbenutzer-tagesverlauf.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY Bahnhofbelastung FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
        for line in f:
            copy.write(line)

with open(os.path.join(DIR_DATASETS, 'schulferien.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY Holidays FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

# _select('* FROM DetectorLocation LIMIT 10')

conn.commit()
cur.close()
conn.close()

_ = '\\' if sys.platform == 'win32' else '\\\\'
os.system(f'psql -U {USER} -d {DBNAME} -c {_}dt')
