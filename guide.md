# Data Integration – Guide to `integrate.py`

This document describes how to configure and run the `integrate.py` script and what data cleansing and normalization steps it performs.

---

## Configuration via `config.ini`

All relevant settings are controlled via a `config.ini` file in the project directory.  
The script first defines default values:

```python
CONFIG = {
    'db_name'= 'dbs',
    'db_user'= 'postgres',
    'db_password'= '',
    'dir_datasets'= '',
    'debug_dropdb'= '',
    'debug_utd19_limit'= '',
    'debug_ist_limit'= '',
    'debug_select'=
}
```

## Executing the script

### Preparation

Requirements:
- PostgreSQL (the following tools must be accessible via your `PATH`: `psql`, `createdb`, `dropdb`)
- Python &ge; 3.14 (lower 3.x versions fail to parse some of our format strings)
- psycopg for Python

1. Create and customize ‘config.ini’ in the project directory.
2. Ensure that:
   - the user "db_user" exists in PostgreSQL,
   - the password "db_password" works,
   - "dir_datasets" points to the directory containing the CSV files.

### Start the script

In the project directory:

```bash
python3 integrate.py
```
