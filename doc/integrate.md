# Data Integration Guide

## 1. Collecting the Datasets

Combine the following directories and files in a folder (you can name it however you want; we'll use the generic name `dir_datasets` to refer to it in this guide):

  - **ist-filtered**  
    This directory contains the 2024 [Ist-Daten dataset](https://archive.opentransportdata.swiss/actual_data_archive.htm) after preprocessing using our [filter.sh script](https://git.scicore.unibas.ch/dbis/lecture-groups/database-systems/2025hs/group-10/-/blob/main/filter.sh) to only include entries for Basel, Zürich, and Luzern:
    - 2024-01-01_istdaten.csv (... and similar)
  - **utd19**  
    This directory contains [the UTD19 dataset](https://utd19.ethz.ch/):
    - detectors_public.csv
    - links.csv
    - utd19_u.csv
  - **weather**  
    This directory contains the [Weather dataset](https://opendata.swiss/de/dataset/klimamessnetz-tageswerte). To obtain the weather data, see 1_how-to-download-nbcn-d.txt, which will point you to a CSV file containing links to the actual weather data per city. We're only interested in *BAS* (Basel), *LUZ* (Luzern), and *SMA* (Zürich). Download these three CSV files, then move them to a new **data** directory inside **weather**:
    - **data**
      - nbcn-daily_BAS_previous.csv (... and similar)
  - [anzahl-sbb-bahnhofbenutzer-tagesverlauf.csv](https://opendata.swiss/de/dataset/anzahl-sbb-bahnhofbenutzer-tagesverlauf) (just place here)
  - [schulferien.csv](https://data.stadt-zuerich.ch/dataset/ssd_schulferien/resource/aad477f6-db39-4d1b-92d8-0885f2d363d1) (just place here)

## 2. Preparing the Environment

We'll need the following tools:
- PostgreSQL (the following command line tools must be included in your `PATH`: `psql`, `createdb`, `dropdb`)
- Python &ge; 3.14 (lower 3.x versions may fail to parse some of our f-strings)
- psycopg for Python

Once you've verified that you meet these requirements, clone this repository and create a new text file called config.ini in its root.

### Datasets

First, the script needs to know where on your system you keep our datasets. For this, add the following line to your config.ini and replace `<dir_datasets>` with the path to your `dir_datasets` directory from step 1:

```
dir_datasets=<dir_datasets>
```

### Credentials

Next, database credentials: config.ini allows you to set the username via `db_user` (defaults to `postgres`) and the password via `db_password` (defaults to the empty string). For example, if you've installed PostgreSQL on macOS via Homebrew, this likely suffices:

```
db_user=<your_username>
```

If you're using Windows, it might be easiest to use the superuser `postgres`, in which case you just need to provide your password:

```
db_password=<your_postgres_superuser_password>
```

### Database

By default, we'll create (**and drop!**) a database called `dbs_hs25_g10`. If this interferes with existing databases on your system, change the name like this:

```
db_name=<your_database_name>
```

### Behavior

Since the full integration takes a while (about 11 minutes on an M4 MacBook Air), we also allow you to limit the number of entries to integrate for the largest datasets. For example, to only read the first 1'500'000 (of the total ~134'000'000) UTD19 entries, add the following to your config.ini:

```
debug_utd19_limit=1500000
```

The config.ini file supports a few more options, mainly for debugging. You likely won't need them, but if you do, they're documented in `integrate.py`.

## 3. Running the Integration Script

To run the integration script, use `python3 integrate.py`. By default, **this first drops any existing databases with the name defined by the configuration (see step 2)**, then creates a fresh database, creates the tables (per `sql/tables.sql`), reads the datasets into the database (while normalizing dates, times, and city names), creates the indexes (per `sql/indexes.sql`), and finally creates the views (per `sql/views.sql`).
