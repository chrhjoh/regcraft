import os
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from typing import Any

import polars as pl

from regcraft.code_schemes import CodeQuery, atc_chapter, icd10_chapter
from regcraft.code_schemes.parse import format_atc, format_icd10
from regcraft.datasets.utils import (
    LongEhrCols,
    Split,
    common_cpr_filters,
    common_diag_adm_filter,
    common_lsr_filter,
    filter_by_occurrence,
    filter_study_age,
    split_dataset,
)
from regcraft.io import write_parquet, write_sharded_parquet, write_txt
from regcraft.registries.columns import CprCols
from regcraft.registries.combine import DiagAdmCols, LsrCols, coallese_diag_adm_dates


class DelfiCategory(Enum):
    ICD10 = 0
    LAB = 1
    ATC = 2
    DEATH = 3
    NOEVENT = 4
    EXTRA = 5


class TokenAttrCols(StrEnum):
    token = auto()
    category_id = auto()
    modality_id = auto()
    class_id = auto()


class SequencesCols(StrEnum):
    patient_id = auto()
    event_texts = auto()
    times_days = auto()


class CovariatesCols(StrEnum):
    patient_id = auto()
    time_days = auto()  # TODO: is this correct?
    feature_id = auto()
    value_ = auto()


class FeatureMapCols(StrEnum):
    name = auto()
    feature_id = auto()
    kind = auto()
    num_classes = auto()


@dataclass
class DelfiToken:
    token: str
    category_id: DelfiCategory
    modality_id: int | None = None
    class_id: int = 0


@dataclass
class DelfiDataset:
    sequences: dict[Split, pl.LazyFrame]
    covariates: dict[Split, pl.LazyFrame]
    candidate_texts: Iterable[str]
    token_attributes: pl.LazyFrame
    feature_map: pl.LazyFrame

    def save(
        self,
        output_dir: str,
        sequences_dir: str = "sequences",
        covariates_dir: str = "covariates",
        candidate_texts: str = "candidate_texts.txt",
        token_attributes: str = "token_attributes.parquet",
        feature_map: str = "feature_map.parquet",
    ):
        def _output(*subpaths: str):
            return os.path.join(output_dir, *subpaths)

        os.makedirs(output_dir, exist_ok=True)
        for split, lf in self.sequences.items():
            write_sharded_parquet(lf, _output(sequences_dir, split))
        for split, lf in self.covariates.items():
            write_sharded_parquet(lf, _output(covariates_dir, split))
        write_parquet(self.token_attributes, _output(token_attributes))
        write_parquet(self.feature_map, _output(feature_map))
        write_txt(self.candidate_texts, _output(candidate_texts))


def extract_delfi_tokens(
    lf: pl.LazyFrame,
    category: DelfiCategory,
    metadata_fn: CodeQuery,
    strip_prefix: str = "",
) -> list[DelfiToken]:
    token = LongEhrCols.token
    codes = lf.select(pl.col(token).unique()).collect().get_column(token).to_list()

    return [
        DelfiToken(
            token=c,
            category_id=category,
            modality_id=metadata_fn(c.lstrip(strip_prefix)).category,
        )
        for c in codes
    ]


def preprocess_cpr(
    cpr: pl.LazyFrame,
    study_start_year: int | None = None,
    status_codes: list[int] | None = None,
):
    cpr = common_cpr_filters(cpr, status_codes)
    if study_start_year:
        cpr = filter_study_age(cpr, study_start_year)
    return cpr.rename({CprCols.cpr_enc: LongEhrCols.patient_id})


def preprocess_lsr(lsr: pl.LazyFrame, atc_level: int):
    token = LongEhrCols.token
    lsr = common_lsr_filter(lsr).with_columns(
        format_atc(atc_level).alias(token),
    )

    return lsr.select(
        pl.col(LsrCols.cpr_enc).alias(LongEhrCols.patient_id), token, LongEhrCols.date
    )


def preprocess_diag_adms(
    diag_adms: pl.LazyFrame,
    icd_level: int,
    included_diag_types: list[str] | None = None,
    excluded_chapters: list[str] | None = None,
    reccuring_codes: bool = False,
    default_date: str = DiagAdmCols.date_start,
    fallback_date: str = DiagAdmCols.date_end,
):
    cpr_enc = DiagAdmCols.cpr_enc
    token = LongEhrCols.token
    date = LongEhrCols.date

    diag_adms = diag_adms.with_columns(
        coallese_diag_adm_dates(default_date, fallback_date).alias(date)
    )

    diag_adms = common_diag_adm_filter(
        diag_adms,
        included_diag_types=included_diag_types,
        excluded_chapters=excluded_chapters,
    )

    diag_adms.with_columns(format_icd10(icd_level).alias(token))

    if not reccuring_codes:
        diag_adms = diag_adms.group_by([cpr_enc, token]).agg(pl.col(date).min())

    return diag_adms.select(pl.col(cpr_enc).alias(LongEhrCols.patient_id), token, date)


def _get_largest_modality_groups(tokens: Iterable[DelfiToken]):
    max_modality_ids = defaultdict(int)
    for t in tokens:
        id_ = t.modality_id or -1
        max_modality_ids[t.category_id.value] = max(
            max_modality_ids.get(t.category_id.value, id_), id_
        )
    return max_modality_ids


def build_token_attributes(
    tokens: Iterable[DelfiToken],
    use_modality_id: bool = False,
) -> pl.DataFrame:

    if use_modality_id:
        modality_max = _get_largest_modality_groups(tokens)
    else:
        modality_max = None

    token_attributes = []
    for t in tokens:
        # use category_id as default if not using modality_id
        modality_id = t.category_id.value
        if use_modality_id and modality_max is not None:
            modality_id = t.modality_id or modality_max[t.category_id.value] + 1

        token_attributes.append(
            {
                TokenAttrCols.token.value: t.token,
                TokenAttrCols.category_id.value: t.category_id,
                TokenAttrCols.modality_id.value: modality_id,
                TokenAttrCols.class_id.value: t.class_id,
            }
        )

    return pl.DataFrame(token_attributes)


def build_candidate_texts(
    tokens: Iterable[DelfiToken],
    include_extra_token: bool = False,
    exclude_tokens: Iterable[str] | None = None,
) -> list[str]:
    if exclude_tokens:
        tokens = [t for t in tokens if t.token not in exclude_tokens]
    if not include_extra_token:
        tokens = [t for t in tokens if t.category_id != DelfiCategory.EXTRA]

    return [t.token for t in tokens]


def build_covariates(cpr: pl.LazyFrame, male: Any = "M"):
    patient_id = LongEhrCols.patient_id
    covariates = cpr.select(
        pl.col(patient_id),
        pl.lit(0).cast(pl.Float32).alias(CovariatesCols.time_days),
        pl.lit(0).alias(CovariatesCols.feature_id),
        pl.when(pl.col(CprCols.sex).eq(male))
        .then(0)
        .otherwise(1)
        .cast(pl.Float32)
        .alias(CovariatesCols.value_),
    ).sort([pl.col(patient_id), pl.col(CovariatesCols.feature_id)])
    feature_map = pl.DataFrame(
        {
            FeatureMapCols.feature_id: [0],
            FeatureMapCols.name: ["sex_id"],
            FeatureMapCols.kind: ["categorical"],
            FeatureMapCols.num_classes: [2],
        }
    )
    return covariates, feature_map


def preprocess_death_data(cpr: pl.LazyFrame):
    status_date = CprCols.status_code
    return cpr.filter(
        pl.col(CprCols.status_code).eq(90) & pl.col(status_date).is_not_null()
    ).select(
        LongEhrCols.patient_id,
        pl.lit("Death").alias(LongEhrCols.token),
        pl.col(status_date).alias(LongEhrCols.date),
    )


def _calculate_age_days(dataset: pl.LazyFrame):
    return dataset.with_columns(
        pl.col(LongEhrCols.date)
        .sub(pl.col(CprCols.birthdate))
        .dt.total_days()
        .alias(LongEhrCols.age_days)
        .cast(pl.Float32),
    )


def filter_dataset_timeperiods(
    dataset: pl.LazyFrame,
    min_age: int = 0,
    max_age: int = 120,
    min_year: int = 1995,
    max_year: int = 2026,
    filter_post_death: bool = True,
):
    date = LongEhrCols.date

    if filter_post_death:
        dataset = dataset.filter(
            # NOTE: status date can be null for alive
            pl.col(date).le(
                pl.col(CprCols.status_date).fill_null(
                    pl.date(year=9999, month=12, day=31)
                )
            )
        )

    return dataset.filter(
        pl.col(LongEhrCols.age_days).is_between(min_age * 365.25, max_age * 365.25)
        & pl.col(date).dt.year().is_between(min_year, max_year)
    )


def dataset_to_sequences(dataset: pl.LazyFrame):
    return (
        dataset.sort(LongEhrCols.age_days)
        .group_by(SequencesCols.patient_id)
        .agg(
            pl.col.token.alias(SequencesCols.event_texts),
            pl.col.age_days.alias(SequencesCols.times_days),
        )
    )


def _split_covariates_by_dataset(
    dataset_splits: Mapping[Split, pl.LazyFrame],
    covariates: pl.LazyFrame,
):
    patient_id = SequencesCols.patient_id
    splits = {}
    for split, dataset in dataset_splits.items():
        ids = dataset.select(patient_id).collect().get_column(patient_id)
        splits[split] = covariates.filter(pl.col(patient_id).is_in(ids))

    return splits


def build_delfi_dataset(
    cpr: pl.LazyFrame,
    lsr: pl.LazyFrame | None = None,
    diag_adms: pl.LazyFrame | None = None,
    atc_token_level: int = 4,
    icd10_token_level: int = 3,
    min_atc_tokens: int = 1,
    min_icd10_tokens: int = 1,
    val_percent: float = 0.1,
    test_percent: float = 0.2,
    seed: int = 42,
) -> DelfiDataset:
    if lsr is None and diag_adms is None:
        raise RuntimeError("lsr or diag_adms must be specified")
    pl.set_random_seed(seed)
    data_sources = []
    tokens = [
        DelfiToken("<bos>", category_id=DelfiCategory.EXTRA),
        DelfiToken("<eos>", category_id=DelfiCategory.EXTRA),
        DelfiToken("<pad>", category_id=DelfiCategory.EXTRA),
        DelfiToken("<noevent>", category_id=DelfiCategory.NOEVENT),
        DelfiToken("Death", category_id=DelfiCategory.DEATH),
    ]

    cpr = preprocess_cpr(cpr)
    data_sources.append(preprocess_death_data(cpr))

    if lsr:
        lsr = preprocess_lsr(lsr, atc_level=atc_token_level)
        lsr = filter_by_occurrence(lsr, min_atc_tokens)
        lsr_tokens = extract_delfi_tokens(
            lsr,
            category=DelfiCategory.ATC,
            metadata_fn=atc_chapter,
            strip_prefix="ATC ",
        )
        data_sources.append(lsr)
        tokens.extend(lsr_tokens)
    if diag_adms:
        diag_adms = preprocess_diag_adms(diag_adms, icd_level=icd10_token_level)
        diag_adms = filter_by_occurrence(diag_adms, min_icd10_tokens)
        diag_tokens = extract_delfi_tokens(
            diag_adms,
            category=DelfiCategory.ICD10,
            metadata_fn=icd10_chapter,
            strip_prefix="ICD10 ",
        )
        data_sources.append(diag_adms)
        tokens.extend(diag_tokens)

    dataset = _calculate_age_days(
        pl.concat(data_sources).join(cpr, on=LongEhrCols.patient_id)
    )
    dataset = filter_dataset_timeperiods(dataset)
    sequences = dataset_to_sequences(dataset)
    splits = split_dataset(sequences, test=test_percent, val=val_percent)

    covariates, feature_map = build_covariates(cpr)

    return DelfiDataset(
        sequences=splits,
        covariates=_split_covariates_by_dataset(splits, covariates),
        candidate_texts=build_candidate_texts(
            tokens, include_extra_token=False, exclude_tokens=None
        ),
        token_attributes=build_token_attributes(tokens, use_modality_id=False).lazy(),
        feature_map=feature_map.lazy(),
    )
