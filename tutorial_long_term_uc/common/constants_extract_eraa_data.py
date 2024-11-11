from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from utils.basic_utils import is_str_bool
from utils.eraa_utils import set_interco_to_tuples


INTERCO_STR_SEP = "2"
USAGE_PARAMS_SHORT_NAMES = {"allow_adding_interco_capas": "adding_interco_capas", 
                            "allow_overwriting_eraa_interco_capa_vals": "overwriting_eraa_interco_capa_vals", 
                            "allow_manually_adding_demand": "manually_adding_demand",
                            "allow_manually_adding_generators": "manually_adding_generators"
                            }

    
@dataclass
class UsageParameters:
    adding_interco_capas: bool = False
    overwriting_eraa_interco_capa_vals: bool = False 
    manually_adding_demand: bool = False
    manually_adding_generators: bool = False


@dataclass
class ERAADatasetDescr:
    # {datatype: {aggreg. prod. type: list of ERAA prod types}}
    aggreg_prod_types_def: Dict[str, Dict[str, List[str]]]
    agg_prod_types_with_cf_data: List[str]  # list of aggreg. prod types with CF (to be read)
    available_climatic_years: List[int]
    available_countries: List[str]
    available_aggreg_prod_types: List[str]
    available_intercos: Union[List[str], List[Tuple[str, str]]]
    available_target_years: List[int]  # N.B. "target year" is a "year" in ERAA terminology
    eraa_edition: str
    # per (meta-)country GPS coordinates - only for network plot
    gps_coordinates: Union[Dict[str, List[float]], Dict[str, Tuple[float, float]]]
    per_zone_color: Dict[str, str]
    per_agg_prod_type_color: Dict[str, str]
    pypsa_unit_params_per_agg_pt: Dict[str, dict]  # dict of per aggreg. prod type main Pypsa params
    # for each aggreg. prod type, a dict. {complem. param name: source - "from_json_tb_modif"/"from_eraa_data"}
    units_complem_params_per_agg_pt: Dict[str, Dict[str, str]]

    def process(self):
        for agg_pt, pypsa_params in self.pypsa_unit_params_per_agg_pt.items():
            for param_name, param_val in pypsa_params.items():
                if is_str_bool(bool_str=param_val) is True:
                    self.pypsa_unit_params_per_agg_pt[agg_pt][param_name] = bool(param_val)
        for country in self.gps_coordinates:
            self.gps_coordinates[country] = tuple(self.gps_coordinates[country])
        # from "{zone_origin}{INTERCO_STR_SEP}{zone_dest}" format of interco names to tuples (zone_origin, zone_dest)
        self.available_intercos = set_interco_to_tuples(interco_names=self.available_intercos)


ALL_UNITS_KEY = "all_units"


@dataclass
class PypsaStaticParams:
    # per aggreg. prod. unit list of minimal parameters for PyPSA generators to be built
    min_unit_params_per_agg_pt: Dict[str, List[str]]

    def process(self):
        # add common static params to all agg. prod type
        if ALL_UNITS_KEY in self.min_unit_params_per_agg_pt:
            common_min_params = self.min_unit_params_per_agg_pt[ALL_UNITS_KEY]
            self.min_unit_params_per_agg_pt.pop(ALL_UNITS_KEY)
            for agg_pt in self.min_unit_params_per_agg_pt:
                self.min_unit_params_per_agg_pt[agg_pt].extend(common_min_params)
                