#!/usr/bin/env python3

import datetime
import enum

class UnitMode(enum.Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

def round_to(
    dt: datetime.datetime,
    unit_mode: UnitMode,
) -> datetime.datetime:
    if unit_mode == UnitMode.DAY:
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit_mode == UnitMode.WEEK:
        dt = round_to(dt, UnitMode.DAY)
        while dt.weekday() != 0:
            dt -= datetime.timedelta(days=1)
    elif unit_mode == UnitMode.MONTH:
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError

    return dt

def format_to(
    dt: datetime.datetime,
    unit_mode: UnitMode,
) -> str:
    if unit_mode == UnitMode.DAY:
        fmt = "%a, %d %b %Y"
    elif unit_mode == unit_mode.WEEK:
        fmt = "Week %U, %Y"
    elif unit_mode == unit_mode.MONTH:
        fmt = "%B %Y"
    else:
        raise ValueError

    return dt.strftime(fmt)

def increment_to(
    dt: datetime.datetime,
    unit_mode: UnitMode,
    decrease: bool = False
) -> datetime.datetime:
    sgn = 1
    if decrease:
        sgn = -1

    if unit_mode == UnitMode.DAY:
        dt += sgn * datetime.timedelta(days=1)
    elif unit_mode == UnitMode.WEEK:
        dt += sgn * datetime.timedelta(days=7)
    elif unit_mode == UnitMode.MONTH:
        dt += sgn * datetime.timedelta(days=31)
        dt = dt.replace(day=1)
    else:
        raise ValueError

    return dt

def decrement_to(
    dt: datetime.datetime,
    unit_mode: UnitMode,
) -> datetime.datetime:
    return increment_to(dt, unit_mode, decrease=True)

