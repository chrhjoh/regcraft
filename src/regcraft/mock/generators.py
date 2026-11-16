from collections.abc import Sequence
from datetime import date, timedelta
from random import Random


def mock_cpr_enc(nrows: int) -> list[str]:
    return mock_sequence(nrows, prefix="Patient")


def mock_sequence(nrows: int, prefix: str = "") -> list[str]:
    return [f"{prefix}{i}" for i in range(nrows)]


def mock_int_sequence(nrows: int) -> list[int]:
    return [i for i in range(nrows)]


def mock_date(
    nrows: int,
    rng: Random,
    start: date,
    end: date,
) -> list[date]:
    max_days = (end - start).days

    return [start + timedelta(days=rng.randint(0, max_days)) for _ in range(nrows)]


def mock_choice[T](
    n: int,
    rng: Random,
    choices: Sequence[T | None],
    weights: Sequence[float] | None = None,
) -> list[T | None]:
    return rng.choices(choices, weights=weights, k=n)
