import math
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from init import *

conn = connect()
cur = conn.cursor()


def plots(drawers):
    width = math.ceil(len(drawers) ** 0.5)
    height = math.ceil(len(drawers) / width)

    _, axes = plt.subplots(width, height, figsize=(
        max(10, width * 4), max(8, height * 3)), sharex=False, squeeze=False)

    for i, drawer in enumerate(drawers):
        drawer(axes.flatten()[i])

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
    holiday_color = kwargs.get('holiday_color', 'silver')
    a_color = kwargs.get('a_color', 'blue')
    b_color = kwargs.get('b_color', 'red')
    a_linewidth = kwargs.get('a_linewidth', 2)
    b_linewidth = kwargs.get('b_linewidth', 2)

    for i, is_holiday in enumerate(y_holiday):
        if is_holiday:
            pos = mdates.date2num(x[i])
            ax1.axvspan(pos - 0.5, pos + 0.5, color=holiday_color)

    ax1.set_xlabel('date')
    ax1.set_ylabel(a_metric)
    getattr(ax1, a_plot)(x, ya, linewidth=a_linewidth, color=a_color)

    ax2 = ax1.twinx()
    ax2.set_ylabel(b_metric)
    getattr(ax2, b_plot)(x, yb, linewidth=b_linewidth, color=b_color)


def month(month, region, a_table, a_metric, b_table, b_metric, **kwargs):
    date_begin = month * 100
    plots([lambda ax1, b=date_begin, e=date_begin + 99, r=region: _date_vs_a_and_b(
        ax1, a_table, a_metric, b_table, b_metric, b, e, r, **kwargs)])


def year(year, region, a_table, a_metric, b_table, b_metric, **kwargs):
    drawers = []
    for i in range(1, 13):
        date_begin = year * 10000 + i * 100
        date_end = date_begin + 99
        drawers.append(lambda ax1, b=date_begin, e=date_end, r=region: _date_vs_a_and_b(
            ax1, a_table, a_metric, b_table, b_metric, b, e, r, **kwargs))
    plots(drawers)


b_table = 'Precipitation'
b_metric = 'precipitation_mm'

year(2024, 3, 'Delays', 'total_delay_s', b_table, b_metric)
# year(2015, 7, 'Traffic_augmented', 'use', b_table, b_metric)
# month(202401, 3, 'Delays', 'total_delay_s', b_table, b_metric, b_linewidth=5)
