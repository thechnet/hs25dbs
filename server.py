#  https://fastapi.tiangolo.com/#create-it

import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from init import *


@asynccontextmanager
async def main(app: FastAPI):
    app.state.conn = connect()
    app.state.cur = app.state.conn.cursor()

    yield

    app.state.cur.close()
    app.state.conn.close()


app = FastAPI(lifespan=main)


# from pydantic import BaseModel
# class Entry(BaseModel):
#     start_date: str
#     start_time: str
#     end_date: str
#     end_time: str
#     summary: str
#     created_date: str


DEFAULT_FILTER_OPERATORS = {
    'start_date': 'equ',
    'end_date': 'equ',
    'summary': 'like',
}

SIMPLE_FILTER_OPERATORS = {
    'equ': '=',
    'neq': '<>',
    'gtr': '>',
    'geq': '>=',
    'lss': '<',
    'leq': '<=',
}


def assemble_filter_and_args(params: dict):
    conditions = ["TRUE"]
    args = []

    for key, value in params.items():
        match = re.match(r'([a-z_]+)(?:\[([a-z]+)\])?', key)
        if match is None:
            warn('bad key:', key)
            continue
        field = match.group(1)
        if field not in DEFAULT_FILTER_OPERATORS:
            warn('bad field:', field)
            continue
        operator = match.group(2) or DEFAULT_FILTER_OPERATORS[field]

        if operator in SIMPLE_FILTER_OPERATORS:
            conditions.append(
                f"{field} {SIMPLE_FILTER_OPERATORS[operator]} %s")
        elif operator == 'like':
            value = value.replace('_', '=_').replace(
                '%', '=%').replace('*', '%')
            conditions.append(f"{field} LIKE %s ESCAPE '='")
        else:
            warn('bad operator:', operator)
            continue

        args.append(value)

    return " AND ".join(conditions), args


@app.get("/")
def read_root(request: Request):
    filter, args = assemble_filter_and_args(dict(request.query_params))

    app.state.cur.execute(f"SELECT * FROM Holidays WHERE {filter}", args)
    rows = app.state.cur.fetchall()

    return {"rows": rows}
