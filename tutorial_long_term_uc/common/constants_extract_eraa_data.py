from dataclasses import dataclass
from typing import Dict, List, Tuple, Union


@dataclass
class ERAADatasetDescr:
    # {datatype: {aggreg. prod. type: list of ERAA prod types}}
    aggreg_prod_types_def: Dict[str, Dict[str, List[str]]]
    agg_prod_types_with_cf_data: List[str]  # list of aggreg. prod types with CF (to be read)
    available_climatic_years: List[int]
    available_countries: List[str]
    available_aggreg_prod_types: List[str]
    available_target_years: List[int]  # N.B. "target year" is a "year" in ERAA terminology
    eraa_edition: str
    # per (meta-)country GPS coordinates - only for network plot
    gps_coordinates: Union[Dict[str, List[float]], Dict[str, Tuple[float, float]]]
    per_zone_color: Dict[str, str]
    per_agg_prod_type_color: Dict[str, str]
    