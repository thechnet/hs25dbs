import os
import sys
import psycopg
from pathlib import Path

CONFIG = {
    'db_name': 'dbs',
    'db_user': 'postgres',
    'db_password': '',
    'dir_datasets': '',
    'debug_dropdb': '1',
    'debug_utd19_limit': '',
    'debug_ist_limit': '',
}
with open('config.ini', 'r') as config_ini:
    for entry in config_ini:
        if entry.startswith(';') or not entry.removesuffix('\n'): continue
        key, value = entry.removesuffix('\n').split('=')
        CONFIG[key] = value.replace('~', os.environ['USERPROFILE' if sys.platform == 'win32' else 'HOME'])
assert CONFIG['dir_datasets']

os.environ['PGUSER'] = CONFIG['db_user']
os.environ['PGPASSWORD'] = CONFIG['db_password']

if CONFIG['debug_dropdb'] == '1':
    os.system(f'dropdb {CONFIG['db_name']}')

os.system(f'createdb -U {CONFIG['db_user']} {CONFIG['db_name']}')

conn = psycopg.connect(
    dbname = CONFIG['db_name'],
    user = CONFIG['db_user'],
    host = 'localhost',
    password = CONFIG['db_password']
)

def _select(query):
    cur.execute('SELECT ' + query + ';')
    print('\n'.join(['|'.join([str(a) for a in t]) for t in cur.fetchall()]))

def skip_header(f):
    f.seek(0)
    next(f)

cur = conn.cursor()

print()

cur.execute(''.join(open('tables.sql').readlines()))

with open(os.path.join(CONFIG['dir_datasets'], 'utd19', 'utd19_u.csv'), 'r', encoding='utf-8') as f:
    skip_header(f)
    count = 0
    with cur.copy("COPY TrafficMeasurement FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:

            # Normalize time.
            record = line.split(',')
            seconds = int(record[1])
            hours = seconds // 3600
            seconds -= hours * 3600
            minutes = seconds // 60
            seconds -= minutes * 60
            record[1] = f'{hours:02}:{minutes:02}:{seconds:02}'
            
            copy.write(','.join(record))
            if CONFIG['debug_utd19_limit'] and (count := count + 1) >= int(CONFIG['debug_utd19_limit']):
                break

with open(os.path.join(CONFIG['dir_datasets'], 'utd19', 'detectors_public.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY DetectorLocation FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

with open(os.path.join(CONFIG['dir_datasets'], 'utd19', 'links.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY DetectorLink FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

dir_dataset_ist = os.path.join(CONFIG['dir_datasets'], 'ist-filtered')
count = 0
for name in Path(dir_dataset_ist).glob('*.csv'):
    path = os.path.join(dir_dataset_ist, name)
    assert os.path.isfile(path)
    with open(path, 'r', encoding = 'utf-8') as f:
        # ist-filtered has no headers.
        with cur.copy("COPY Zugfahrt FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
            for line in f:

                # Normalize times.
                record = line.split(';')
                for i in [14, 17]: # 14: ankunftszeit
                    if record[i]:
                        record[i] = record[i].split(' ')[1] + ':00'
                for i in [15, 18]:
                    if record[i]:
                        record[i] = record[i].split(' ')[1]

                copy.write(';'.join(record))
    if CONFIG['debug_ist_limit'] and (count := count + 1) >= int(CONFIG['debug_ist_limit']):
        break

for citycode in ['BAS', 'LUZ', 'SMA']:
    with open(os.path.join(CONFIG['dir_datasets'], 'weather', 'data', f'nbcn-daily_{citycode}_previous.csv'), 'r', encoding = 'utf-8') as f:
        skip_header(f)
        with cur.copy("COPY Weather FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
            for line in f:
                copy.write(line)

with open(os.path.join(CONFIG['dir_datasets'], 'anzahl-sbb-bahnhofbenutzer-tagesverlauf.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY Bahnhofbelastung FROM STDIN WITH (FORMAT csv, DELIMITER ';')") as copy:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue

            record = line.split(';')

            if len(record) <= 3 or not record[3].strip():
                copy.write(';'.join(record) + '\n')
                continue

            hour = int(float(record[3]))
            record[3] = f"{hour:02}:00:00"
            copy.write(';'.join(record) + '\n')

with open(os.path.join(CONFIG['dir_datasets'], 'schulferien.csv'), 'r', encoding = 'utf-8') as f:
    skip_header(f)
    with cur.copy("COPY Holidays FROM STDIN WITH (FORMAT csv)") as copy:
        for line in f:
            copy.write(line)

conn.commit()
cur.close()
conn.close()

_ = '\\' if sys.platform == 'win32' else '\\\\'
os.system(f'psql -U {CONFIG['db_user']} -d {CONFIG['db_name']} -c {_}dt')
