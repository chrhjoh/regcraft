from datetime import date
from random import Random

import pytest

from regcraft.mock.generators import (
    mock_choice,
    mock_cpr_enc,
    mock_date,
    mock_int_sequence,
    mock_sequence,
)


def test_mock_cpr_enc():
    assert mock_cpr_enc(3) == ["Patient0", "Patient1", "Patient2"]


def test_mock_sequence():
    assert mock_sequence(3) == ["0", "1", "2"]
    assert mock_sequence(2, prefix="ID-") == ["ID-0", "ID-1"]


def test_mock_int_sequence():
    assert mock_int_sequence(3) == [0, 1, 2]


def test_mock_date_within_range():
    start = date(2020, 1, 1)
    end = date(2020, 1, 10)

    dates = mock_date(100, Random(42), start, end)

    assert len(dates) == 100
    assert all(start <= d <= end for d in dates)


def test_mock_date_reproducible():
    start = date(2020, 1, 1)
    end = date(2020, 12, 31)

    assert mock_date(10, Random(42), start, end) == mock_date(
        10, Random(42), start, end
    )


def test_mock_date_includes_endpoints():
    start = date(2020, 1, 1)

    dates = mock_date(100, Random(42), start, start)

    assert dates == [start] * 100


def test_mock_choice():
    choices = ["A", "B", "C"]

    result = mock_choice(100, Random(42), choices)

    assert len(result) == 100
    assert set(result) <= set(choices)


def test_mock_choice_with_weights():
    result = mock_choice(
        10,
        Random(42),
        choices=["A", "B"],
        weights=[1, 0],
    )

    assert result == ["A"] * 10


def test_mock_choice_with_none():
    result = mock_choice(10, Random(42), choices=[None])

    assert result == [None] * 10


def test_mock_choice_invalid_weights():
    with pytest.raises(ValueError):
        mock_choice(10, Random(42), choices=["A", "B"], weights=[1])
