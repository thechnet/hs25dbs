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

1. Create and customize ‘config.ini’ in the project directory.
2. Ensure that:
   - the user "db_user" exists in PostgreSQL,
   - the password "db_password" works,
   - "dir_datasets" points to the directory containing the CSV files.

### Start the script

In the project directory:

```bash
python integrate.py
```