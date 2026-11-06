from enum import StrEnum, auto
from pathlib import Path

import polars as pl

from regkit.registries.fetchers.factory import (
    FetcherType,
    RegistryFetcher,
    RegistryVersion,
    default_scanner,
    fetcher,
)


class LaegemiddelCols(StrEnum):
    atc = auto()
    item_id = auto()


@fetcher(registry_type=FetcherType.LAEGEMIDDEL)
class LaegemiddelRegistryFetcher(RegistryFetcher):
    cols = LaegemiddelCols

    def column_norm_mapping(self):
        atc = "atc"
        item_id = "vnr"
        return {atc: self.cols.atc, item_id: self.cols.item_id}

    def _scan_file(self, path: str):

        if self.version == RegistryVersion.V2026 and Path(path).suffix == ".asc":
            raise ValueError(
                "Laegemiddeloplysninger separator is not unique. Rerun with the .uniqDelim file"
            )

        if self.version != RegistryVersion.V2026:
            return default_scanner(path)

        separator = "¤"
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.readlines()
        header = lines.pop(0).split(separator)
        indexes = [i for i, c in enumerate(header) if c in self.column_norm_mapping()]
        data = [{header[i]: l.split(separator)[i] for i in indexes} for l in lines]

        df = pl.from_dicts(data, schema={"vnr": pl.Int64, "atc": pl.Utf8})
        return df.lazy()


class EpikurCols(StrEnum):
    cpr_enc = auto()
    item_id = auto()
    date = auto()


@fetcher(registry_type=FetcherType.EPIKUR)
class EpikurRegistryFetcher(RegistryFetcher):
    cols = EpikurCols

    def column_norm_mapping(self):
        item_id = "vnr"
        date = "eksd"
        cpr_enc = "cpr_enc"
        return {
            cpr_enc: self.cols.cpr_enc.value,
            date: self.cols.date.value,
            item_id: self.cols.item_id.value,
        }
