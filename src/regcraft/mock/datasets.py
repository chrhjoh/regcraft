import regcraft.mock.registries as mock
from regcraft.datasets.delfi import build_delfi_dataset
from regcraft.registries.columns import CprCols
from regcraft.registries.combine import create_diag_adm, create_lsr


def mock_delfi(patients: int, events_per_modality: int, seed: int = 42):
    cpr = mock.mock_cpr(patients)
    unique_patients = cpr.collect().get_column(CprCols.cpr_enc).unique().to_list()

    lpr2_diag = mock.mock_lpr2diag(events_per_modality // 2)
    lpr2_adm = mock.mock_lpr2adm(
        nrows=events_per_modality // 2, patients=unique_patients
    )

    lpr3_diag = mock.mock_lpr3diag(events_per_modality // 2)
    lpr3_contact = mock.mock_lpr3contact(
        events_per_modality // 2, patients=unique_patients
    )
    diag_adm = create_diag_adm(
        lpr2_diag=lpr2_diag,
        lpr2_adm=lpr2_adm,
        lpr3_diag=lpr3_diag,
        lpr3_adm=lpr3_contact,
    )
    lsr = create_lsr(
        mock.mock_epikur(events_per_modality, patients=unique_patients),
        mock.mock_laegemiddel(),
    )

    return build_delfi_dataset(cpr, lsr, diag_adm, seed=seed)
