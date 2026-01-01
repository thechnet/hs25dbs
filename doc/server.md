# REST API Guide

## 1. Preparing the Environment

First, run through `integrate.md` to get the database ready.

Next, install [`fastapi[standard]`](https://fastapi.tiangolo.com/#installation) for Python.

## 2. Running the Server

To start the server, use `fastapi dev server.py`, then navigate to `http://localhost:8000/docs` in your browser.

## 3. Using the API

### GET (via `/entries`)

The search filter is specified via query parameters. For queries of the form `attr=value`, the default comparison (specified in `DEFAULT_FILTER_OPERATORS` in `server.py`) is performed. Additionally, we suppport the form `attr[op]=value`, where `op` is either `like` (see note below) or one of the operations specified in `SIMPLE_FILTER_OPERATORS`. Multiple query parameters can be given to check for multiple conditions.

For example, to get all entries with IDs in \(1,10\] but excluding 5, use

```
http://localhost:8000/entries?id[gtr]=1&id[leq]=10&id[neq]=5
```

**Note that `like` uses `*` instead of `%` and doesn't support `_`.**

### POST (via `/entry`)

Used to create the entry specified as JSON in the request body. The API hides the `id` attribute (because it is auto-incremented), and all attributes not listed under the `CreatableEntry` class are optional (if omitted, a fallback value is used).

An example (via `curl`) might look like this:

```sh
curl -X 'POST' \
  'http://localhost:8000/entry' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "end_date": 20251226,
  "end_time": "00:00:00",
  "start_date": 20251225,
  "start_time": "00:00:00",
  "summary": "Christmas"
}'
```

### PUT (via `/entry/{id}`)

Used to update the entry with ID `id`. The updates are specified as JSON in the response body. Any selection of the attributes listed under the `UpdatableEntry` class may be specified.

An example (via `curl`) might look like this:

```sh
curl -X 'PUT' \
  'http://localhost:8000/entry/297' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "summary": "Christmas 2025"
}'
```

### DELETE (via `/entry/{id}`)

Used to delete the entry with ID `id`.

An example (via `curl`) might look like this:

```sh
curl -X 'DELETE' \
  'http://localhost:8000/entry/297' \
  -H 'accept: application/json'
```
