import polars as pl
from polars import LazyFrame

import regkit.registries.columns as cols
from regkit.registries.fetchers.factory import FetcherType, RegistryFetcher, fetcher


@fetcher(registry_type=FetcherType.LPR2DIAG)
class Lpr2DiagRegistryFetcher(RegistryFetcher):
    cols = cols.Lpr2DiagCols

    def column_norm_mapping(self):
        record_number = "V_RECNUM"
        diag_type = "C_DIAGTYPE"
        diag = "C_DIAG"
        diag_additional = "C_TILDIAG"
        return {
            record_number: self.cols.record_number,
            diag_type: self.cols.diag_type,
            diag: self.cols.diag,
            diag_additional: self.cols.diag_additional,
        }


@fetcher(registry_type=FetcherType.LPR2ADM)
class Lpr2AdmRegistryFetcher(RegistryFetcher):
    cols = cols.Lpr2AdmCols

    def _post_rename(self, lf: LazyFrame):
        return lf.with_columns(
            pl.lit("LPR2").alias(self.cols.lpr_origin),
            pl.lit(None, dtype=pl.Utf8).alias(self.cols.contact_type),
        )

    def column_norm_mapping(self):
        cpr_enc = "cpr_enc"
        date_start = "D_INDDTO"
        date_end = "D_UDDTO"
        patient_type = "C_PATTYPE"
        record_number = "K_RECNUM"
        return {
            cpr_enc: self.cols.cpr_enc,
            date_start: self.cols.date_start,
            date_end: self.cols.date_end,
            record_number: self.cols.record_number,
            patient_type: self.cols.patient_type,
        }


@fetcher(registry_type=FetcherType.LPR3DIAG)
class Lpr3DiagRegistryFetcher(RegistryFetcher):
    cols = cols.Lpr3DiagCols

    def _post_rename(self, lf: LazyFrame):
        later_disproven = "senere_afkraeftet"
        return lf.with_columns(
            pl.lit(None, dtype=pl.Int64).alias(self.cols.diag_additional),
        ).filter(pl.col(later_disproven).str.to_lowercase().ne("ja"))

    def column_norm_mapping(self):
        record_number = "dw_ek_kontakt"
        diag_type = "diagnosetype"
        diag = "diagnosekode"
        lpr_origin = "lprindberetningssystem"

        return {
            record_number: self.cols.record_number,
            diag_type: self.cols.diag_type,
            diag: self.cols.diag,
            lpr_origin: self.cols.lpr_origin,
        }


@fetcher(registry_type=FetcherType.LPR3CONTACT)
class Lpr3ContactRegistryFetcher(RegistryFetcher):
    cols = cols.Lpr3ContactCols

    def _post_rename(self, lf: LazyFrame):
        return lf.with_columns(
            pl.lit(None, dtype=pl.Int64).alias(self.cols.patient_type),
        )

    def column_norm_mapping(self):
        cpr_enc = "cpr_enc"
        record_number = "dw_ek_kontakt"
        date_start = "dato_start"
        date_end = "dato_slut"
        contact_type = "kontakttype"
        return {
            cpr_enc: self.cols.cpr_enc,
            date_start: self.cols.date_start,
            date_end: self.cols.date_end,
            record_number: self.cols.record_number,
            contact_type: self.cols.contact_type,
        }
