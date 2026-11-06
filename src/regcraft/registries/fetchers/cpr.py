import regcraft.registries.columns as cols
from regcraft.registries.fetchers.factory import FetcherType, RegistryFetcher, fetcher


@fetcher(registry_type=FetcherType.CPR)
class CprRegistryFetcher(RegistryFetcher):
    cols = cols.CprCols

    def column_norm_mapping(self):
        cpr_enc = "cpr_enc"
        birthdate = "D_FODDATO"
        status_code = "C_STATUS"
        status_date = "D_STATUS_HEN_START"
        sex = "C_KON"
        return {
            cpr_enc: self.cols.cpr_enc.value,
            birthdate: self.cols.birthdate.value,
            status_code: self.cols.status_code.value,
            status_date: self.cols.status_date.value,
            sex: self.cols.sex.value,
        }
