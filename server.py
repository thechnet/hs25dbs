import re
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from init import *
from pydantic import BaseModel


@asynccontextmanager
async def main(app: FastAPI):
    app.state.conn = connect()
    app.state.cur = app.state.conn.cursor()

    yield

    app.state.cur.close()
    app.state.conn.close()


app = FastAPI(lifespan=main)

DEFAULT_TIME = '00:00:00'


class UpdatableEntry(BaseModel):
    start_date: Optional[int] = None
    start_time: Optional[str] = DEFAULT_TIME
    end_date: Optional[int] = None
    end_time: Optional[str] = DEFAULT_TIME
    summary: Optional[str] = None
    created_date: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                'start_date': 20260101,
                'end_date': 20260102,
                'summary': '...'
            }
        }
    }


class CreatableEntry(UpdatableEntry):
    start_date: int
    end_date: int
    summary: str

    model_config = {
        'json_schema_extra': {
            'example': {
                'start_date': 20260101,
                'start_time': DEFAULT_TIME,
                'end_date': 20260102,
                'end_time': DEFAULT_TIME,
                'summary': 'Summary'
            }
        }
    }


DEFAULT_FILTER_OPERATORS = {
    'id': 'equ',
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


@app.get("/entries")
def get_entries(request: Request):
    filter, args = assemble_filter_and_args(dict(request.query_params))
    print(filter)

    app.state.cur.execute(f"""
        SELECT * FROM Holidays
        WHERE {filter}
    """, args)

    return {"matches": app.state.cur.fetchall()}


@app.post("/entry")
def create_entry(entry: CreatableEntry):
    app.state.cur.execute("""
        INSERT INTO Holidays (start_date, start_time, end_date, end_time, summary, created_date)
        VALUES (%s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE))
        RETURNING *
    """, (entry.start_date, entry.start_time, entry.end_date, entry.end_time, entry.summary, entry.created_date))
    result = app.state.cur.fetchone()
    app.state.conn.commit()

    return {"message": "entry created", "entry": result}


@app.put("/entry/{id}")
def update_entry(id: int, entry: UpdatableEntry):
    updates = entry.model_dump(exclude_unset=True)

    if not updates:
        return {"message": "no updates given"}

    app.state.cur.execute(f"""
        UPDATE Holidays
        SET {', '.join([f"{key}=%s" for key in updates.keys()])}
        WHERE id = %s
        RETURNING *
    """, (*updates.values(), id))
    result = app.state.cur.fetchone()
    app.state.conn.commit()

    return {"message": "entry updated", "entry": result}


@app.delete("/entry/{id}")
def delete_entry(id: int):
    app.state.cur.execute(f"""
        DELETE
        FROM Holidays
        WHERE id = %s
    """, (id,))
    app.state.conn.commit()

    return {"message": "entry deleted"}
