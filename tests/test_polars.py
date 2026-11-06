from datetime import date

import polars as pl
import pytest

from regcraft.polars import convert_dates


def test_convert_dates():
    lf = pl.LazyFrame(
        {
            "start_date": ["2024-01-15", "2024-02-20"],
            "end_date": ["2024-03-10", "2024-04-25"],
            "name": ["Alice", "Bob"],
        }
    )

    result = convert_dates(lf).collect()

    assert result.schema["start_date"] == pl.Date
    assert result.schema["end_date"] == pl.Date
    assert result["start_date"].to_list() == [
        date(2024, 1, 15),
        date(2024, 2, 20),
    ]
    assert result["name"].to_list() == ["Alice", "Bob"]


def test_convert_dates_custom_format():
    lf = pl.LazyFrame({"birth_date": ["15/01/2024", "20/02/2024"]})

    result = convert_dates(lf, format="%d/%m/%Y").collect()

    assert result["birth_date"].to_list() == [
        date(2024, 1, 15),
        date(2024, 2, 20),
    ]


def test_convert_dates_custom_expression():
    lf = pl.LazyFrame(
        {
            "date_of_birth": ["2024-01-15"],
            "created": ["2024-02-20"],
        }
    )

    result = convert_dates(lf, expr="^date_of_birth$").collect()

    assert result.schema["date_of_birth"] == pl.Date
    assert result.schema["created"] == pl.String


def test_convert_dates_non_strict():
    lf = pl.LazyFrame({"event_date": ["2024-01-15", "invalid", None]})

    result = convert_dates(lf, strict=False).collect()

    assert result["event_date"].to_list() == [
        date(2024, 1, 15),
        None,
        None,
    ]


def test_convert_dates_strict():
    lf = pl.LazyFrame({"event_date": ["2024-01-15", "invalid"]})

    with pytest.raises(pl.exceptions.InvalidOperationError):
        convert_dates(lf, strict=True).collect()
