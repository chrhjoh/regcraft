from enum import StrEnum, auto

import polars as pl


class BaseCols(StrEnum):
    @classmethod
    def schema(cls) -> pl.Schema:
        raise NotImplementedError()


class CprCols(BaseCols):
    cpr_enc = auto()
    birthdate = auto()
    status_code = auto()
    status_date = auto()
    sex = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.birthdate.value: pl.Date,
                cls.status_code.value: pl.Int16,
                cls.status_date.value: pl.Date,
                cls.sex.value: pl.Utf8,
            }
        )


class Lpr2DiagCols(BaseCols):
    record_number = auto()
    diag_type = auto()
    diag = auto()
    diag_additional = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.record_number.value: pl.Int32,
                cls.diag_type.value: pl.Utf8,
                cls.diag.value: pl.Utf8,
                cls.diag_additional.value: pl.Utf8,
            }
        )


class Lpr2AdmCols(BaseCols):
    cpr_enc = auto()
    date_start = auto()
    date_end = auto()
    record_number = auto()
    patient_type = auto()
    lpr_origin = auto()
    contact_type = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.date_start.value: pl.Date,
                cls.date_end.value: pl.Date,
                cls.record_number.value: pl.Int32,
                cls.patient_type.value: pl.Utf8,
                cls.lpr_origin.value: pl.Utf8,
                cls.contact_type.value: pl.Utf8,
            }
        )


class Lpr3DiagCols(BaseCols):
    record_number = auto()
    diag_type = auto()
    diag = auto()
    lpr_origin = auto()
    diag_additional = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.record_number.value: pl.Int32,
                cls.diag_type.value: pl.Utf8,
                cls.diag.value: pl.Utf8,
                cls.lpr_origin.value: pl.Utf8,
                cls.diag_additional.value: pl.Utf8,
            }
        )


class Lpr3ContactCols(BaseCols):
    cpr_enc = auto()
    date_start = auto()
    date_end = auto()
    record_number = auto()
    patient_type = auto()
    contact_type = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.date_start.value: pl.Date,
                cls.date_end.value: pl.Date,
                cls.record_number.value: pl.Int32,
                cls.patient_type.value: pl.Utf8,
                cls.contact_type.value: pl.Utf8,
            }
        )


class LaegemiddelCols(BaseCols):
    atc = auto()
    item_id = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.atc.value: pl.Utf8,
                cls.item_id.value: pl.Int32,
            }
        )


class EpikurCols(BaseCols):
    cpr_enc = auto()
    item_id = auto()
    date = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.date.value: pl.Date,
                cls.item_id.value: pl.Int32,
            }
        )


class LsrCols(BaseCols):
    cpr_enc = auto()
    atc = auto()
    date = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.atc.value: pl.Utf8,
                cls.date.value: pl.Date,
            }
        )


class DiagAdmCols(BaseCols):
    cpr_enc = auto()
    diag = auto()
    diag_type = auto()
    date_start = auto()
    date_end = auto()

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                cls.cpr_enc.value: pl.Utf8,
                cls.diag.value: pl.Utf8,
                cls.diag_type.value: pl.Utf8,
                cls.date_start.value: pl.Date,
                cls.date_end.value: pl.Date,
            }
        )
