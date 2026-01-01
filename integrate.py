import csv
from pathlib import Path

from init import *


def _select(query):
    try:
        cur.execute('SELECT ' + query + ';')
        print('\n'.join(['\t'.join(
            [f'\033[42m{a}\033[0m' for a in t]) for t in cur.fetchall()]))
    except Exception as e:
        print(e)


def execute(path):
    print(f'Executing {path}')
    cur.execute(''.join(open(path).readlines()))


def read(table, source, has_header, delimiter=',', limit=None, normalizer=None):
    if not isinstance(source, list):
        source = [source]
    for path in source:
        with open(
            os.path.join(CONFIG['dir_datasets'], path),
            mode='r',
            # Disable newline translation (preferred by csv library)
            newline='',
            encoding='utf-8'
        ) as file:
            reader = csv.reader(file, delimiter=delimiter)
            if has_header:
                next(reader)  # Skip header.
            with cur.copy(f"COPY {table} FROM STDIN WITH (FORMAT csv, DELIMITER '{delimiter}')") as copy:
                count = 0
                for record in reader:
                    normalized = normalizer(record) if normalizer else record
                    for i in range(len(normalized)):
                        normalized[i] = str(normalized[i])
                        if delimiter in normalized[i]:
                            normalized[i] = f'"{normalized[i]}"'
                    copy.write(delimiter.join(normalized) + '\n')
                    if limit is not None and (count := count + 1) >= limit:
                        break


def normalize_trafficmeasurement(record):
    seconds = int(record[1])
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    record[1] = f'{hours:02}:{minutes:02}:{seconds:02}'
    return record


def normalize_weather(record):
    match record[0]:
        case 'BAS':
            record[0] = 'Basel'
        case 'LUZ':
            record[0] = 'Luzern'
        case 'SMA':
            record[0] = 'Zürich'
    for i in range(2, len(record)):
        if record[i] == '-':
            record[i] = ''
    return record
    return record


def normalize_holidays(record):
    start_date, end_date, summary, created_date = record
    start_date, start_time = start_date.split('T')
    end_date, end_time = end_date.split('T')
    return [start_date, start_time.rstrip('Z'), end_date, end_time.rstrip('Z'), summary, created_date]


def normalize_ist(record):
    for i in [14, 17]:  # 14: ankunftszeit
        if record[i]:
            record[i] = record[i].split(' ')[1] + ':00'
    for i in [15, 18]:
        if record[i]:
            record[i] = record[i].split(' ')[1]
    return record


def normalize_bahnhofbelastung(record):
    if len(record) <= 3 or not record[3].strip():
        return record
    hour = int(float(record[3]))
    record[3] = f"{hour:02}:00:00"
    return record


if __name__ == '__main__':

    # Prepare database, connection, and cursor.

    if CONFIG['debug_dropdb'] == '1':
        os.system(f'dropdb {CONFIG['db_name']}')
    os.system(f'createdb -U {CONFIG['db_user']} {CONFIG['db_name']}')

    conn = connect()

    cur = conn.cursor()

    # Create tables.

    execute('tables.sql')

    # Read data.

    print('Reading data')

    # UTD19.
    utd19_u = f'utd19_u{'-filtered' if CONFIG['debug_use_filtered_utd19'] else ''}.csv'
    read('TrafficMeasurement', os.path.join('utd19', utd19_u), True, limit=int(
        CONFIG['debug_utd19_limit']) if CONFIG['debug_utd19_limit'] else None, normalizer=normalize_trafficmeasurement)
    read('DetectorLocation', os.path.join(
        'utd19', 'detectors_public.csv'), True)
    read('DetectorLink', os.path.join('utd19', 'links.csv'), True)

    # Holidays.
    read('Holidays(start_date, start_time, end_date, end_time, summary, created_date)',
         'schulferien.csv', True, normalizer=normalize_holidays)

    # Ist.
    dir_dataset_ist = os.path.join(CONFIG['dir_datasets'], 'ist-filtered')
    read('Zugfahrt', [p for p in Path(dir_dataset_ist).glob('*.csv')], False,
         delimiter=';', limit=int(CONFIG['debug_ist_limit']) if CONFIG['debug_ist_limit'] else None, normalizer=normalize_ist)

    # Weather.
    read('Weather', [Path('weather') / 'data' / f'nbcn-daily_{city}_previous.csv' for city in [
         'BAS', 'LUZ', 'SMA']], True, delimiter=';', normalizer=normalize_weather)

    # Bahnhofbelastung.
    read('Bahnhofbelastung', 'anzahl-sbb-bahnhofbenutzer-tagesverlauf.csv',
         True, delimiter=';', normalizer=normalize_bahnhofbelastung)

    # Create indexes.

    if not CONFIG['debug_no_index']:
        execute('indexes.sql')

    # Finalize.

    conn.commit()

    if CONFIG['debug_select']:
        _select(CONFIG['debug_select'])

    cur.close()
    conn.close()

    _ = '\\' if sys.platform == 'win32' else '\\\\'
    os.system(f'psql -U {CONFIG['db_user']} -d {CONFIG['db_name']} -c {_}dt')

    if CONFIG['debug_dump']:
        print('Dumping')
        os.system(
            f'pg_dump -U {CONFIG['db_user']} {CONFIG['db_name']} > dbs_hs25_g10.sql')
