import os
import sys
import psycopg

DEBUG_DROPDB = True
DEBUG_UTD19_LIMIT = 1000

DBNAME = 'dbs'
USER = os.environ['USERNAME' if sys.platform == 'win32' else 'USER']

try:
    UTD19 = os.environ['UTD19']
except KeyError:
    UTD19 = ''
if not os.path.isdir(UTD19):
    print(f'Please ensure the "UTD19" environment variable points to a directory containing the complete UTD19 dataset before running this script.')
    quit()

def _select(query):
    cur.execute('SELECT ' + query + ';')
    print('\n'.join([', '.join([str(a) for a in t]) for t in cur.fetchall()]))

os.system(f'createdb {DBNAME}')

conn = psycopg.connect(f'dbname={DBNAME} user={USER} host=localhost')
cur = conn.cursor()

print()

cur.execute(''.join(open('tables.sql').readlines()))

with open(os.path.join(UTD19, 'utd19_u.csv'), 'r') as f:
    f.seek(0)
    next(f)
    count = 0
    with cur.copy("COPY TrafficMeasurement FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)
            if (count := count + 1) >= DEBUG_UTD19_LIMIT:
                break

with open(os.path.join(UTD19, 'detectors_public.csv'), 'r') as f:
    f.seek(0)
    next(f)
    with cur.copy("COPY DetectorLocation FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

with open(os.path.join(UTD19, 'links.csv'), 'r') as f:
    f.seek(0)
    next(f)
    with cur.copy("COPY DetectorLink FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

# _select('* FROM DetectorLocation LIMIT 10')

conn.commit()
cur.close()
conn.close()

os.system(f'psql -U {USER} -d {DBNAME} -c \\\\dt')

if DEBUG_DROPDB:
    os.system(f'dropdb {DBNAME}')
