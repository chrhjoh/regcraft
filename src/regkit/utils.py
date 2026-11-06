from collections.abc import Mapping


def _merge_mappings(
    defaults: Mapping[str, str] | None, overrides: Mapping[str, str] | None
) -> Mapping[str, str]:
    mapping = {}
    for mapper in [defaults, overrides]:
        if mapper is not None:
            for k, v in mapper:
                mapping[k] = v
    return mapping
