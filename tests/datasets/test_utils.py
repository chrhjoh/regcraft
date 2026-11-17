from datetime import date

import polars as pl
import pytest

from regcraft.datasets.utils import (
    Split,
    common_cpr_filters,
    common_diag_adm_filter,
    common_lsr_filter,
    filter_by_occurrence,
    filter_study_age,
    split_dataset,
)
from regcraft.registries.columns import CprCols, DiagAdmCols, LsrCols


def test_filter_by_occurrence():
    lf = pl.DataFrame({"token": ["A", "A", "B", "C", "C", "C"]}).lazy()

    result = filter_by_occurrence(lf, min_count=2).collect()

    assert result["token"].to_list() == ["A", "A", "C", "C", "C"]


def test_filter_by_occurrence_custom_column():
    lf = pl.DataFrame({"code": ["A", "A", "B"]}).lazy()

    result = filter_by_occurrence(lf, min_count=2, col="code").collect()

    assert result["code"].to_list() == ["A", "A"]


def test_split_dataset_reproducible():
    lf = pl.DataFrame({"id": range(1000)}).lazy()

    first = split_dataset(lf, val=0.1, test=0.2, seed=42)
    second = split_dataset(lf, val=0.1, test=0.2, seed=42)

    for split in first:
        assert (
            first[split].collect()["id"].to_list()
            == second[split].collect()["id"].to_list()
        )


def test_split_dataset_proportions_and_integrity():
    lf = pl.DataFrame({"id": range(1000)}).lazy()

    result = split_dataset(lf, val=0.1, test=0.2, seed=42)
    collected = {split: frame.collect() for split, frame in result.items()}

    assert set(result) == {Split.TRAIN, Split.VAL, Split.TEST}

    ids = [set(df["id"].to_list()) for df in collected.values()]

    assert len(ids[0] & ids[1]) == 0
    assert len(ids[0] & ids[2]) == 0
    assert len(ids[1] & ids[2]) == 0
    assert set.union(*ids) == set(range(1000))

    assert all("split" not in df.columns for df in collected.values())


@pytest.mark.parametrize(
    ("val", "test", "expected_splits"),
    [
        (0.0, 0.0, {Split.TRAIN}),
        (0.2, 0.0, {Split.TRAIN, Split.VAL}),
        (0.0, 0.2, {Split.TRAIN, Split.TEST}),
        (0.5, 0.5, {Split.VAL, Split.TEST}),
    ],
)
def test_split_dataset_omits_empty_splits(val, test, expected_splits):
    lf = pl.DataFrame({"id": range(10)}).lazy()

    result = split_dataset(lf, val=val, test=test, seed=42)

    assert set(result) == expected_splits


def test_split_dataset_rejects_invalid_proportions():
    lf = pl.DataFrame({"id": [1, 2, 3]}).lazy()

    with pytest.raises(ValueError):
        split_dataset(lf, val=0.5, test=0.6)


def test_common_cpr_filters():
    lf = pl.DataFrame(
        {
            CprCols.status_code: [1, 80, 90, 2, 1],
            CprCols.birthdate: [
                date(1990, 1, 1),
                date(1990, 1, 1),
                date(1990, 1, 1),
                date(1990, 1, 1),
                None,
            ],
        }
    ).lazy()

    result = common_cpr_filters(lf, None).collect()

    assert result[CprCols.status_code].to_list() == [1, 80, 90]


def test_common_cpr_filters_custom_status_codes():
    lf = pl.DataFrame(
        {
            CprCols.status_code: [1, 2, 3],
            CprCols.birthdate: [date(1990, 1, 1)] * 3,
        }
    ).lazy()

    result = common_cpr_filters(lf, [2]).collect()

    assert result[CprCols.status_code].to_list() == [2]


def test_filter_study_age():
    lf = pl.DataFrame(
        {
            CprCols.birthdate: [
                date(2002, 1, 1),  # Exactly 18
                date(2002, 1, 2),  # Under 18
                date(1955, 1, 1),  # Exactly 65
                date(1954, 12, 31),  # Over 65
            ],
        }
    ).lazy()

    result = filter_study_age(
        lf,
        year=2020,
        min_age=18,
        max_age=65,
    ).collect()

    assert result[CprCols.birthdate].to_list() == [
        date(2002, 1, 1),
        date(1955, 1, 1),
    ]


def test_common_lsr_filter():
    lf = pl.DataFrame(
        {LsrCols.atc: ["A10AB01", "A10AB0", "N06AB03", "A10AB010"]}
    ).lazy()

    result = common_lsr_filter(lf).collect()

    assert result[LsrCols.atc].to_list() == ["A10AB01", "N06AB03"]


def test_common_diag_adm_filter():
    lf = pl.DataFrame(
        {
            DiagAdmCols.diag: [
                "DE11",
                "DR10",
                "DS10",
                "DT10",
                "DA10",
                "AE11",
            ],
            DiagAdmCols.diag_type: ["A", "A", "A", "A", "C", "A"],
        }
    ).lazy()

    result = common_diag_adm_filter(lf).collect()

    assert result[DiagAdmCols.diag].to_list() == ["DE11"]


def test_common_diag_adm_filter_custom_options():
    lf = pl.DataFrame(
        {
            DiagAdmCols.diag: ["DE11", "DR10", "AE11"],
            DiagAdmCols.diag_type: ["A", "B", "A"],
        }
    ).lazy()

    result = common_diag_adm_filter(
        lf,
        included_diag_types=["A"],
        excluded_chapters=["R"],
        icd10_only=False,
    ).collect()

    assert result[DiagAdmCols.diag].to_list() == ["DE11", "AE11"]
