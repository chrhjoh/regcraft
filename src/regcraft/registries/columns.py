from enum import StrEnum, auto


class CprCols(StrEnum):
    cpr_enc = auto()
    birthdate = auto()
    status_code = auto()
    status_date = auto()
    sex = auto()


class Lpr2DiagCols(StrEnum):
    record_number = auto()
    diag_type = auto()
    diag = auto()
    diag_additional = auto()


class Lpr2AdmCols(StrEnum):
    cpr_enc = auto()
    date_start = auto()
    date_end = auto()
    record_number = auto()
    patient_type = auto()
    lpr_origin = auto()
    contact_type = auto()


class Lpr3DiagCols(StrEnum):
    record_number = auto()
    diag_type = auto()
    diag = auto()
    lpr_origin = auto()
    diag_additional = auto()


class Lpr3ContactCols(StrEnum):
    cpr_enc = auto()
    date_start = auto()
    date_end = auto()
    record_number = auto()
    patient_type = auto()
    contact_type = auto()
