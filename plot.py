import math
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from init import *

PATH_OUT = 'out'
DO_CLEAR_OUT = True
DO_SAVE_FIG = True

conn = connect()
cur = conn.cursor()


def plots(title, drawers):
    width = math.ceil(len(drawers) ** 0.5)
    height = math.ceil(len(drawers) / width)

    fig, axes = plt.subplots(width, height, figsize=(
        max(5, width * 4), max(4, height * 3)), sharex=False, squeeze=False)

    fig.suptitle(title)

    for i, drawer in enumerate(drawers):
        drawer(axes.flatten()[i])

    plt.tight_layout()
    if DO_SAVE_FIG:
        plt.savefig(f'{PATH_OUT}/{title}.png')
    else:
        plt.show()


def _date_vs_a_and_b(ax1, a_table, a_metric, b_table, b_metric, date_begin, date_end, region, **kwargs):
    params = locals()
    del params['ax1'], params['kwargs']

    # Build and execute query.
    query = open('queries/date_vs_a_and_b.sql').read()
    for key, value in params.items():
        query = query.replace('$' + key, str(value))
    assert '$' not in query
    cur.execute(query)

    # Extract results.
    rows = cur.fetchall()
    x = [datetime.strptime(str(row[0]), '%Y%m%d') for row in rows]
    y_holiday = [row[1] for row in rows]
    ya = [row[2] for row in rows]
    yb = [row[3] for row in rows]

    # Get options.
    a_plot = kwargs.get('a_plot', 'bar')
    b_plot = kwargs.get('a_plot', 'plot')
    holiday_color = kwargs.get('holiday_color', 'gainsboro')
    a_color = kwargs.get('a_color', 'cadetblue')
    b_color = kwargs.get('b_color', 'black')
    a_linewidth = kwargs.get('a_linewidth', 2)
    b_linewidth = kwargs.get('b_linewidth', 2)

    for i, is_holiday in enumerate(y_holiday):
        if is_holiday:
            pos = mdates.date2num(x[i])
            ax1.axvspan(pos - 0.5, pos + 0.5, color=holiday_color)

    ax1.set_xlabel('date')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    ax1.set_ylabel(a_metric)
    getattr(ax1, a_plot)(x, ya, linewidth=a_linewidth, color=a_color)

    ax2 = ax1.twinx()
    ax2.set_ylabel(b_metric)
    getattr(ax2, b_plot)(x, yb, linewidth=b_linewidth, color=b_color)


def plot_month(month, region, a_table, a_metric, b_table, b_metric, **kwargs):
    date_begin = month * 100
    plots(f'{a_table} & {b_table} ({region}, {month})', [lambda ax1, b=date_begin, e=date_begin + 99, r=region: _date_vs_a_and_b(
        ax1, a_table, a_metric, b_table, b_metric, b, e, r, **kwargs)])


def plot_year(year, region, a_table, a_metric, b_table, b_metric, **kwargs):
    drawers = []
    for i in range(1, 13):
        date_begin = year * 10000 + i * 100
        date_end = date_begin + 99
        drawers.append(lambda ax1, b=date_begin, e=date_end, r=region: _date_vs_a_and_b(
            ax1, a_table, a_metric, b_table, b_metric, b, e, r, **kwargs))
    plots(f'{a_table} & {b_table} ({region}, {year})', drawers)


if DO_CLEAR_OUT:
    for file in Path(PATH_OUT).iterdir():
        file.unlink()

for a_table, a_metric, year, regions in [
    ('Traffic_augmented', 'road_use', 2015, [
        7,
    ]),
    ('Delays', 'total_delay_s', 2024, [
        3,
        7,
        21,
    ]),
]:
    for region in regions:
        for b_table, b_metric in [
            ('Snow', 'snow_cm'),
            ('Precipitation', 'precipitation_mm'),
            ('Temperature', 'temp_avg'),
            ('Temperature', 'temp_min'),
            ('Temperature', 'temp_max'),
        ]:
            print(year, region, a_table, a_metric, b_table, b_metric)
            plot_year(year, region, a_table, a_metric, b_table, b_metric)
