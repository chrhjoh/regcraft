from datetime import date

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from regcraft.code_schemes import icd10_chapter
from regcraft.datasets.delfi import (
    DelfiCategory,
    DelfiToken,
    build_candidate_texts,
    build_covariates,
    build_delfi_dataset,
    build_token_attributes,
    dataset_to_sequences,
    extract_delfi_tokens,
    filter_dataset_timeperiods,
    preprocess_cpr,
    preprocess_death_data,
    preprocess_diag_adms,
    preprocess_lsr,
)
from regcraft.datasets.utils import LongEhrCols
from regcraft.registries.columns import CprCols, DiagAdmCols, LsrCols


def test_extract_delfi_tokens():
    lf = pl.DataFrame({"token": ["ICD10 E11", "ICD10 E11", "ICD10 I10"]}).lazy()

    result = extract_delfi_tokens(
        lf,
        category=DelfiCategory.ICD10,
        metadata_fn=icd10_chapter,
        strip_prefix="ICD10 ",
    )

    assert all(
        r
        in [
            DelfiToken("ICD10 E11", DelfiCategory.ICD10, modality_id=4),
            DelfiToken("ICD10 I10", DelfiCategory.ICD10, modality_id=9),
        ]
        for r in result
    )


def test_build_token_attributes():
    tokens = [
        DelfiToken("E11", DelfiCategory.ICD10, class_id=1),
        DelfiToken("A10", DelfiCategory.ATC, class_id=2),
    ]

    result = build_token_attributes(tokens)

    expected = pl.DataFrame(
        {
            "token": ["A10", "E11"],
            "category_id": [2, 0],
            "modality_id": [2, 0],
            "class_id": [2, 1],
        }
    )

    assert_frame_equal(result, expected)


def test_build_candidate_texts():
    tokens = [
        DelfiToken("E11", DelfiCategory.ICD10),
        DelfiToken("A10", DelfiCategory.ATC),
        DelfiToken("<pad>", DelfiCategory.EXTRA),
    ]

    assert build_candidate_texts(tokens) == ["A10", "E11"]
    assert build_candidate_texts(tokens, include_extra_token=True) == [
        "<pad>",
        "A10",
        "E11",
    ]
    assert build_candidate_texts(tokens, exclude_tokens=["E11"]) == ["A10"]


def test_preprocess_cpr():
    lf = pl.DataFrame(
        {
            CprCols.cpr_enc: ["1", "2", "3"],
            CprCols.birthdate: [
                date(1990, 1, 1),
                date(1990, 1, 1),
                None,
            ],
            CprCols.status_code: [1, 2, 1],
        }
    ).lazy()

    result = preprocess_cpr(lf).collect()

    assert result[LongEhrCols.patient_id].to_list() == ["1"]
    assert LongEhrCols.patient_id in result.columns
    assert CprCols.cpr_enc not in result.columns


def test_preprocess_lsr():
    lf = pl.DataFrame(
        {
            LsrCols.cpr_enc: ["1", "2"],
            LsrCols.atc: ["A10AB01", "N06AB03"],
            LsrCols.date: [date(2020, 1, 1), date(2020, 2, 1)],
        }
    ).lazy()

    result = preprocess_lsr(lf, atc_level=4).collect()

    assert result[LongEhrCols.patient_id].to_list() == ["1", "2"]
    assert result[LongEhrCols.token].to_list() == ["ATC A10AB", "ATC N06AB"]
    assert result[LongEhrCols.date].to_list() == [
        date(2020, 1, 1),
        date(2020, 2, 1),
    ]


def test_preprocess_diag_adms():
    lf = pl.DataFrame(
        {
            DiagAdmCols.cpr_enc: ["1", "1", "1"],
            DiagAdmCols.diag: ["DE11", "DE11", "DI10"],
            DiagAdmCols.diag_type: ["A", "A", "A"],
            DiagAdmCols.date_start: [
                date(2020, 1, 1),
                date(2021, 1, 1),
                date(2020, 2, 1),
            ],
            DiagAdmCols.date_end: [
                None,
                None,
                None,
            ],
        }
    ).lazy()

    result = preprocess_diag_adms(lf, icd_level=3).collect()

    assert result[LongEhrCols.patient_id].to_list() == ["1", "1"]
    assert result[LongEhrCols.token].to_list() == ["ICD10 E11", "ICD10 I10"]
    assert result[LongEhrCols.date].to_list() == [
        date(2020, 1, 1),
        date(2020, 2, 1),
    ]


def test_preprocess_diag_adms_keeps_recurring_codes():
    lf = pl.DataFrame(
        {
            DiagAdmCols.cpr_enc: ["1", "1"],
            DiagAdmCols.diag: ["DE11", "DE11"],
            DiagAdmCols.diag_type: ["A", "A"],
            DiagAdmCols.date_start: [
                date(2020, 1, 1),
                date(2021, 1, 1),
            ],
            DiagAdmCols.date_end: [None, None],
        }
    ).lazy()

    result = preprocess_diag_adms(lf, icd_level=3, reccuring_codes=True).collect()

    assert result.height == 2


def test_build_covariates():
    lf = pl.DataFrame(
        {
            LongEhrCols.patient_id: ["1", "2"],
            CprCols.sex: ["M", "F"],
        }
    ).lazy()

    covariates, feature_map = build_covariates(lf)

    assert covariates.collect()["value_"].to_list() == [0.0, 1.0]
    assert covariates.collect()["feature_id"].to_list() == [0, 0]
    assert feature_map["name"].to_list() == ["sex_id"]


def test_preprocess_death_data():
    lf = pl.DataFrame(
        {
            LongEhrCols.patient_id: ["1", "2", "3"],
            CprCols.status_code: [90, 1, 90],
            CprCols.status_date: [
                date(2020, 1, 1),
                date(2020, 1, 1),
                None,
            ],
        }
    ).lazy()

    result = preprocess_death_data(lf).collect()

    assert result[LongEhrCols.patient_id].to_list() == ["1"]
    assert result[LongEhrCols.token].to_list() == ["Death"]


def test_filter_dataset_timeperiods():
    lf = pl.DataFrame(
        {
            LongEhrCols.patient_id: ["1", "2", "3"],
            LongEhrCols.date: [
                date(2020, 1, 1),
                date(2021, 1, 1),
                date(2020, 1, 1),
            ],
            LongEhrCols.age_days: [365.25 * 30] * 3,
            CprCols.status_date: [
                date(2020, 6, 1),
                date(2020, 6, 1),
                None,
            ],
        }
    ).lazy()

    result = filter_dataset_timeperiods(lf, min_year=2020, max_year=2021).collect()

    assert result[LongEhrCols.patient_id].to_list() == ["1", "3"]


def test_dataset_to_sequences():
    lf = pl.DataFrame(
        {
            LongEhrCols.patient_id: ["1", "1", "2"],
            LongEhrCols.token: ["B", "A", "C"],
            LongEhrCols.age_days: [20.0, 10.0, 30.0],
        }
    ).lazy()

    result = dataset_to_sequences(lf).collect()

    patient_1 = result.filter(pl.col("patient_id") == "1")

    assert patient_1["event_texts"].item().to_list() == ["A", "B"]
    assert patient_1["times_days"].item().to_list() == [10.0, 20.0]


def test_build_delfi_dataset_requires_data_source():
    cpr = pl.DataFrame(
        {
            CprCols.cpr_enc: ["1"],
            CprCols.birthdate: [date(1990, 1, 1)],
            CprCols.status_code: [1],
            CprCols.status_date: [None],
            CprCols.sex: ["M"],
        }
    ).lazy()

    with pytest.raises(RuntimeError, match="lsr or diag_adms"):
        build_delfi_dataset(cpr)
