from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from enum import StrEnum, auto
from pathlib import Path

import polars as pl
from polars import LazyFrame

from regcraft.polars import convert_dates


class RegistryVersion(StrEnum):
    V2026 = auto()

    @classmethod
    def from_path(cls, path: str):
        if "/2026-04-07/" in path:
            return RegistryVersion.V2026

        raise ValueError(f"Could not determine registries version of {path}")


class FetcherType(StrEnum):
    LAEGEMIDDEL = auto()
    EPIKUR = auto()
    CPR = auto()
    LPR2DIAG = auto()
    LPR2ADM = auto()
    LPR3DIAG = auto()
    LPR3CONTACT = auto()

    @classmethod
    def from_path(cls, path: str):
        match Path(path).stem:
            case "epikur":
                return FetcherType.EPIKUR
            case "laegemiddeloplysninger":
                return FetcherType.LAEGEMIDDEL
            case "t_person":
                return FetcherType.CPR
            case "LPR2DIAG":
                return FetcherType.LPR2DIAG
            case "LPR2ADM":
                return FetcherType.LPR2ADM
            case "LPR3CONTACT":
                return FetcherType.LPR3CONTACT
            case "LPR3DIAG":
                return FetcherType.LPR3DIAG

        raise ValueError(f"Could not determine registries version of {path}")


type Scanner = Callable[[str], pl.LazyFrame]


def default_scanner(path: str, **kwargs):
    return pl.scan_csv(path, separator=";", **kwargs)


class RegistryFetcher[E: StrEnum](ABC):
    cols: type[E]

    def __init__(
        self,
        version: RegistryVersion,
    ):
        self.version = version
        if not self.validate_version():
            raise RuntimeError(f"Registry {self} is not valid with version:", version)

    def _scan_file(self, path: str) -> LazyFrame:
        return default_scanner(path)

    def _post_rename(self, lf: LazyFrame) -> LazyFrame:
        return lf

    def _select_cols(self, lf: LazyFrame) -> LazyFrame:
        return lf.select(*self.cols)

    def _convert_dates(self, lf: LazyFrame) -> LazyFrame:
        return convert_dates(lf, strict=False)

    def parse(self, path: str) -> LazyFrame:
        lf = self._scan_file(path)
        lf = lf.rename(self.column_norm_mapping())
        lf = self._select_cols(self._post_rename(lf))
        lf = self._convert_dates(lf)

        return lf

    @abstractmethod
    def column_norm_mapping(self) -> Mapping[str, str]:
        """Returns a column mapping for normalizing column names"""

    def validate_version(self) -> bool:
        """Returns a column mapping for normalizing column names"""
        return self.version in (RegistryVersion.V2026,)


Fetchers: dict[FetcherType, type[RegistryFetcher]] = {}


def fetcher(
    registry_type: FetcherType,
):
    def decorator(registry: type[RegistryFetcher]):
        if registry_type in Fetchers:
            raise ValueError(f"Already registered registry {registry_type}")
        Fetchers[registry_type] = registry

    return decorator


def get_registryfetcher(registry_type: FetcherType) -> type[RegistryFetcher]:
    return Fetchers[registry_type]
