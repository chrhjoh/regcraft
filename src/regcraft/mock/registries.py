from collections.abc import Sequence
from datetime import date
from random import Random

import polars as pl

import regcraft.mock.generators as gen
import regcraft.registries.columns as c


def mock_cpr(
    nrows: int,
    seed: int = 42,
    start_birthdate: date = date(1940, 1, 1),
    end_birthdate: date = date(2012, 1, 1),
    end_status_date: date = date(2024, 12, 31),
) -> pl.LazyFrame:
    rng = Random(seed)
    status_codes = gen.mock_choice(
        nrows, rng, choices=[1, 90, 80, 30], weights=[10, 5, 1, 1]
    )
    return pl.LazyFrame(
        {
            c.CprCols.cpr_enc.value: gen.mock_cpr_enc(nrows),
            c.CprCols.birthdate.value: gen.mock_date(
                nrows, rng=rng, start=start_birthdate, end=end_birthdate
            ),
            c.CprCols.status_code.value: status_codes,
            c.CprCols.status_date.value: [
                d if s != 1 else None
                for d, s in zip(
                    gen.mock_date(
                        nrows, rng=rng, start=end_birthdate, end=end_status_date
                    ),
                    status_codes,
                )
            ],
            c.CprCols.sex.value: gen.mock_choice(nrows, rng=rng, choices=["M", "F"]),
        },
        schema=c.CprCols.schema(),
    )


def _mock_common_diag(
    nrows: int,
    rng: Random,
    codes: Sequence[str] | None = None,
    weights: Sequence[float] | None = None,
) -> dict[str, Sequence[str | int | None]]:
    if weights is not None and codes is None:
        raise ValueError("If weights are specified then codes must also be specified")
    elif weights is not None and codes is not None and len(weights) != len(codes):
        raise ValueError("codes and weights must have the same length")

    if not codes:
        codes = ["DE10", "DC15", "Y213", "12345", "DA100"]
        weights = [10, 10, 0.5, 0.5, 2]
    return {
        c.Lpr2DiagCols.diag: gen.mock_choice(
            nrows,
            rng=rng,
            choices=codes,
            weights=weights,
        ),
        c.Lpr2DiagCols.diag_additional: gen.mock_choice(
            nrows,
            rng=rng,
            choices=list(codes) + [None],
            weights=list(weights) + [50] if weights is not None else None,
        ),
        c.Lpr2DiagCols.diag_type: gen.mock_choice(
            nrows, rng=rng, choices=["A", "B", "C", "M"], weights=[10, 5, 2, 0.5]
        ),
        c.Lpr2DiagCols.record_number: gen.mock_int_sequence(nrows),
    }


def _mock_common_adm(
    nrows: int,
    patients: Sequence[str] | int,
    start_date: date,
    end_date: date,
    rng: Random,
) -> dict[str, Sequence[str | int | None | date]]:
    return {
        c.Lpr2AdmCols.cpr_enc: _resolve_long_cpr_enc(nrows, patients),
        c.Lpr2AdmCols.date_start: gen.mock_date(
            nrows, rng, start=start_date, end=end_date
        ),
        c.Lpr2AdmCols.date_end: gen.mock_date(
            nrows, rng, start=start_date, end=end_date
        ),
        c.Lpr2AdmCols.record_number: gen.mock_int_sequence(nrows),
        c.Lpr2AdmCols.patient_type: gen.mock_choice(
            nrows, rng=rng, choices=["In", "Out"]
        ),
        c.Lpr2AdmCols.contact_type: gen.mock_choice(
            nrows, rng=rng, choices=["Physical", "Virtual"]
        ),
    }


def mock_lpr2diag(
    nrows: int,
    seed: int = 42,
) -> pl.LazyFrame:
    return pl.LazyFrame(
        _mock_common_diag(nrows, rng=Random(seed)),
        schema=c.Lpr2DiagCols.schema(),
    )


def _resolve_long_cpr_enc(
    nrows: int,
    patients: Sequence[str] | int,
) -> list[str]:
    if isinstance(patients, int):
        patients = gen.mock_cpr_enc(patients)

    if not patients:
        raise ValueError("patients cannot be empty")

    return [patients[i % len(patients)] for i in range(nrows)]


def mock_lpr2adm(
    nrows: int,
    patients: Sequence[str] | int,
    seed=42,
) -> pl.LazyFrame:
    rng = Random(seed)
    data = _mock_common_adm(
        nrows, patients, date(2000, 1, 1), date(2024, 12, 31), rng=rng
    )
    data[c.Lpr2AdmCols.lpr_origin] = ["LPR2" for _ in range(nrows)]
    return pl.LazyFrame(data, schema=c.Lpr2AdmCols.schema())


def mock_lpr3diag(
    nrows: int,
    seed=42,
) -> pl.LazyFrame:
    rng = Random(seed)
    data = _mock_common_diag(nrows, rng=rng)
    data[c.Lpr3DiagCols.lpr_origin] = gen.mock_choice(
        nrows, rng=rng, choices=["LPR3", "Other"], weights=[10, 0.5]
    )
    return pl.LazyFrame(data, schema=c.Lpr3DiagCols.schema())


def mock_lpr3contact(
    nrows: int,
    patients: Sequence[str] | int,
    seed=42,
) -> pl.LazyFrame:
    rng = Random(seed)
    data = _mock_common_adm(
        nrows, patients, date(2000, 1, 1), date(2024, 12, 31), rng=rng
    )
    return pl.LazyFrame(data, schema=c.Lpr3ContactCols.schema())


ATCS = ["A10AB01", "C10AB29", "AB", "A10AE01"]
ITEM_IDS = list(range(len(ATCS)))


def mock_epikur(
    nrows: int,
    patients: Sequence[str] | int,
    seed=42,
) -> pl.LazyFrame:
    rng = Random(seed)
    return pl.LazyFrame(
        {
            c.EpikurCols.cpr_enc: _resolve_long_cpr_enc(nrows, patients),
            c.EpikurCols.item_id: gen.mock_choice(nrows, rng=rng, choices=ITEM_IDS),
            c.EpikurCols.date: gen.mock_date(
                nrows, rng=rng, start=date(2000, 1, 1), end=date(2024, 12, 31)
            ),
        }
    )


def mock_laegemiddel() -> pl.LazyFrame:
    return pl.LazyFrame(
        {c.LaegemiddelCols.item_id: ITEM_IDS, c.LaegemiddelCols.atc: ATCS}
    )
