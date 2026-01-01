import csv
from datetime import datetime
from pathlib import Path

from init import *

HALTESTELLEN = [
    'Basel Bad Bf',
    'Basel Dreispitz',
    'Basel Grenze',
    'Basel SBB',
    'Basel SBB RB Gr A',
    'Basel St. Jakob',
    'Basel St. Johann',
    'Luzern',
    'Luzern Allmend/Messe',
    'Luzern Littau',
    'Luzern Verkehrshaus',
    'Zürich Affoltern',
    'Zürich Altstetten',
    'Zürich Altstetten Farbhof',
    'Zürich Binz',
    'Zürich Brunau',
    'Zürich Enge',
    'Zürich Flughafen',
    'Zürich Friesenberg',
    'Zürich Giesshübel',
    'Zürich Hardbrücke',
    'Zürich HB',
    'Zürich HB SZU',
    'Zürich Langstrasse',
    'Zürich Leimbach',
    'Zürich Manegg',
    'Zürich Oerlikon',
    'Zürich Saalsporthalle',
    'Zürich Schweighof',
    'Zürich Seebach',
    'Zürich Selnau',
    'Zürich Stadelhofen',
    'Zürich Stadelhofen Bahnhof',
    'Zürich Tiefenbrunnen',
    'Zürich Triemli',
    'Zürich Wiedikon',
    'Zürich Wipkingen',
    'Zürich Wollishofen',
    'Zürich Balgrist',
    'Zürich Hegibachplatz',
    'Zürich Kreuzplatz',
    'Zürich Rehalp',
    'Zürich Wetlistrasse',
]

UTD19_CITY_TO_REGION = {
    'basel': HALTESTELLEN.index('Basel SBB'),
    'luzern': HALTESTELLEN.index('Luzern'),
    'zurich': HALTESTELLEN.index('Zürich HB')
}


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
    # day
    year, month, day = record[0].split('-')
    record[0] = f'{year}{month}{day}'

    record[6] = UTD19_CITY_TO_REGION.get(record[6], -1)

    # interval
    # seconds = int(record[1])
    # hours = seconds // 3600
    # seconds -= hours * 3600
    # minutes = seconds // 60
    # seconds -= minutes * 60
    # record[1] = f'{hours:02}:{minutes:02}:{seconds:02}'

    return record


def normalize_ist(record):
    # haltestellen_name
    record[13] = HALTESTELLEN.index(record[13].replace(', ', ' '))

    # add seconds to ankunftszeit and abfahrtszeit
    for i in [14, 17]:
        if not record[i]:  # use betriebstag
            record[i] = f'{record[0]} 12:00'
        record[i] += ':00'
    # if prognose is missing, assume no delay
    if not record[15]:
        record[15] = record[14]
    if not record[18]:
        record[18] = record[17]
    # convert to timestamps
    for i in [14, 15, 17, 18]:
        record[i] = int(datetime.strptime(
            record[i], '%d.%m.%Y %H:%M:%S').timestamp())

    # betriebstag
    day, month, year = record[0].split('.')
    record[0] = f'{year}{month}{day}'

    return record


def normalize_weather(record):
    match record[0]:
        case 'BAS':
            record[0] = HALTESTELLEN.index('Basel SBB')
        case 'LUZ':
            record[0] = HALTESTELLEN.index('Luzern')
        case 'SMA':
            record[0] = HALTESTELLEN.index('Zürich HB')
    for i in range(2, len(record)):
        if record[i] == '-':
            record[i] = ''
    return record


def normalize_bahnhofbelastung(record):
    if len(record) <= 3 or not record[3].strip():
        return record
    hour = int(float(record[3]))
    record[3] = f"{hour:02}:00:00"
    return record


def normalize_holidays(record):
    start_date, end_date, summary, created_date = record
    start_date, start_time = start_date.split('T')
    end_date, end_time = end_date.split('T')

    start_year, start_month, start_day = start_date.split('-')
    start_date = f'{start_year}{start_month}{start_day}'

    end_year, end_month, end_day = end_date.split('-')
    end_date = f'{end_year}{end_month}{end_day}'

    return [start_date, start_time.rstrip('Z'), end_date, end_time.rstrip('Z'), summary, created_date]


if __name__ == '__main__':

    # Print indices.

    city = '*'
    firstidx = 0
    lastidx = 0
    for i, stop in enumerate(HALTESTELLEN):
        if not stop.startswith(city) or i + 1 == len(HALTESTELLEN):
            if city != '*':
                print(city, firstidx, '-', lastidx -
                      (0 if i + 1 == len(HALTESTELLEN) else 1))
                firstidx = lastidx
            city = stop.split(' ')[0]
        lastidx += 1
    print()

    # Prepare database, connection, and cursor.

    if CONFIG['debug_dropdb'] == '1':
        os.system(f'dropdb {CONFIG['db_name']}')
    os.system(f'createdb -U {CONFIG['db_user']} {CONFIG['db_name']}')

    conn = connect()

    cur = conn.cursor()

    # Create tables.

    execute('sql/tables.sql')

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
        execute('sql/indexes.sql')

    # Create views.

    execute('sql/views.sql')

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
