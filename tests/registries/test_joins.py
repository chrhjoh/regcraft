from datetime import date
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_schema_equal

from regcraft.registries import joins
from regcraft.registries.columns import DiagAdmCols, LsrCols


def test_create_diag_adm_no_complete_pair():
    with pytest.raises(RuntimeError, match="At least either both lpr2 or both lpr3"):
        joins.create_diag_adm(
            lpr2_diag=None,
            lpr2_adm=None,
            lpr3_diag=None,
            lpr3_adm=None,
        )


@pytest.fixture
def epikur() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "cpr_enc": ["A", "B", "C"],
            "item_id": [1, 2, 3],
            "date": [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1)],
        }
    ).lazy()


@pytest.fixture
def laegemiddel() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "item_id": [1, 2, 4],
            "atc": ["A01", "B02", "C03"],
        }
    ).lazy()


@pytest.fixture
def lpr2_diag() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "record_number": [1, 2, 3],
            "diag_type": ["A", "B", "C"],
            "diag": ["D1", "D2", "D3"],
            "diag_additional": [None, None, None],
        }
    ).lazy()


@pytest.fixture
def lpr2_adm() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "cpr_enc": ["A", "B", "C"],
            "date_start": [
                date(2020, 1, 1),
                date(2020, 2, 1),
                date(2020, 3, 1),
            ],
            "date_end": [
                date(2020, 1, 2),
                date(2020, 2, 2),
                date(2020, 3, 2),
            ],
            "record_number": [1, 2, 4],
            "patient_type": ["P", "P", "P"],
            "lpr_origin": ["LPR2", "LPR2", "LPR2"],
            "contact_type": ["X", "X", "X"],
        }
    ).lazy()


@pytest.fixture
def lpr3_diag() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "record_number": [10, 20],
            "diag_type": ["A", "B"],
            "diag": ["D10", "D20"],
            "lpr_origin": ["LPR3", "LPR3"],
            "diag_additional": [None, None],
        }
    ).lazy()


@pytest.fixture
def lpr3_adm() -> pl.LazyFrame:
    return pl.DataFrame(
        {
            "cpr_enc": ["D", "E"],
            "date_start": [date(2021, 1, 1), date(2021, 2, 1)],
            "date_end": [date(2021, 1, 2), date(2021, 2, 2)],
            "record_number": [10, 20],
            "patient_type": ["P", "P"],
            "contact_type": ["X", "X"],
        }
    ).lazy()


def test_join_lsr(
    epikur: pl.LazyFrame,
    laegemiddel: pl.LazyFrame,
):
    result = joins.join_lsr(epikur, laegemiddel).collect()

    expected = pl.DataFrame(
        {
            "cpr_enc": ["A", "B"],
            "atc": ["A01", "B02"],
            "date": [date(2020, 1, 1), date(2020, 2, 1)],
        }
    )

    assert_schema_equal(result.schema, LsrCols.schema())
    assert_frame_equal(result.sort("cpr_enc"), expected)


def test_join_diag_adm(
    lpr2_diag: pl.LazyFrame,
    lpr2_adm: pl.LazyFrame,
):
    result = joins.join_diag_adm(
        lpr2_diag,
        lpr2_adm,
        on="record_number",
    ).collect()

    expected = pl.DataFrame(
        {
            "cpr_enc": ["A", "B"],
            "diag": ["D1", "D2"],
            "diag_type": ["A", "B"],
            "date_start": [date(2020, 1, 1), date(2020, 2, 1)],
            "date_end": [date(2020, 1, 2), date(2020, 2, 2)],
        }
    )

    assert_schema_equal(result.schema, DiagAdmCols.schema())
    assert_frame_equal(result.sort("cpr_enc"), expected)


@pytest.mark.parametrize("collect", [False, True])
def test_create_lsr(
    epikur: pl.LazyFrame,
    laegemiddel: pl.LazyFrame,
    tmp_path: Path,
    collect: bool,
):
    epikur_path = tmp_path / "epikur.parquet"
    laegemiddel_path = tmp_path / "laegemiddel.parquet"

    epikur.collect().write_parquet(epikur_path)
    laegemiddel.collect().write_parquet(laegemiddel_path)

    if collect:
        result = joins.create_lsr(str(epikur_path), str(laegemiddel_path))
    else:
        result = joins.create_lsr(epikur, laegemiddel)

    expected = joins.join_lsr(epikur, laegemiddel).collect()

    assert_frame_equal(
        result.collect().sort("cpr_enc"),
        expected.sort("cpr_enc"),
    )


def test_create_diag_adm_lpr2_only(
    lpr2_diag: pl.LazyFrame,
    lpr2_adm: pl.LazyFrame,
):
    result = joins.create_diag_adm(lpr2_diag, lpr2_adm, None, None).collect()

    expected = joins.join_diag_adm(lpr2_diag, lpr2_adm, on="record_number").collect()

    assert_frame_equal(result, expected, check_row_order=False)


def test_create_diag_adm_lpr3_only(
    lpr3_diag: pl.LazyFrame,
    lpr3_adm: pl.LazyFrame,
):
    result = joins.create_diag_adm(None, None, lpr3_diag, lpr3_adm).collect()

    expected = joins.join_diag_adm(lpr3_diag, lpr3_adm, on="record_number").collect()

    assert_frame_equal(result, expected, check_row_order=False)


def test_create_diag_adm_both(
    lpr2_diag: pl.LazyFrame,
    lpr2_adm: pl.LazyFrame,
    lpr3_diag: pl.LazyFrame,
    lpr3_adm: pl.LazyFrame,
):
    result = joins.create_diag_adm(lpr2_diag, lpr2_adm, lpr3_diag, lpr3_adm).collect()

    expected = pl.concat(
        [
            joins.join_diag_adm(lpr2_diag, lpr2_adm, on="record_number").collect(),
            joins.join_diag_adm(lpr3_diag, lpr3_adm, on="record_number").collect(),
        ]
    )

    assert result.height == 4
    assert_schema_equal(result.schema, DiagAdmCols.schema())
    assert_frame_equal(result, expected, check_row_order=False)


@pytest.mark.parametrize(
    ("lpr2_diag_missing", "lpr2_adm_missing", "lpr3_diag_missing", "lpr3_adm_missing"),
    [
        (None, None, None, None),
        (None, None, None, "provided"),
        (None, None, "provided", None),
        (None, "provided", None, None),
        ("provided", None, None, None),
    ],
)
def test_create_diag_adm_incomplete_inputs(
    lpr2_diag_missing,
    lpr2_adm_missing,
    lpr3_diag_missing,
    lpr3_adm_missing,
):
    with pytest.raises(RuntimeError, match="At least either both lpr2 or both lpr3"):
        joins.create_diag_adm(
            lpr2_diag_missing,
            lpr2_adm_missing,
            lpr3_diag_missing,
            lpr3_adm_missing,
        )
