from regkit.registries.fetchers import cpr as cpr
from regkit.registries.fetchers import lpr as lpr
from regkit.registries.fetchers import lsr as lsr

from .factory import get_registryfetcher

__all__ = ["get_registryfetcher"]
