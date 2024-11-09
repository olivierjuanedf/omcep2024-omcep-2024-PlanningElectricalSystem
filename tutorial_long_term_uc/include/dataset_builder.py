import pandas as pd
import numpy as np
from typing import Dict, List, Union
from dataclasses import dataclass

from common.error_msgs import print_errors_list, print_out_msg
from common.long_term_uc_io import COMPLEM_DATA_SOURCES, COLUMN_NAMES


@dataclass
class GenUnitsPypsaParams:
    capa_factors: str = "p_max_pu" 
    power_capa: str = "p_nom"
    energy_capa: str = None


GEN_UNITS_PYPSA_PARAMS = GenUnitsPypsaParams()


@dataclass
class GenerationUnitData:
    name: str
    type: str
    carrier: str = None
    p_nom: float = None
    p_min_pu: float = None
    p_max_pu: float = None
    efficiency: float = None
    marginal_cost: float = None
    committable: bool = False

    def get_non_none_attr_names(self):
        return [key for key, val in self.__dict__.items() if val is not None]


def get_val_of_agg_pt_in_df(df_data: pd.DataFrame, prod_type_agg_col: str, 
                            agg_prod_type: str, value_col: str, static_val: bool) \
                                -> Union[np.ndarray, float]:
    if static_val is True:
        return df_data[df_data[prod_type_agg_col] == agg_prod_type][value_col].iloc[0]
    else:
        return np.array(df_data[df_data[prod_type_agg_col] == agg_prod_type][value_col])


def set_gen_unit_name(country: str, agg_prod_type: str) -> str:
    return f"{country[:3].lower()}_{agg_prod_type}"


def get_generation_units_data(pypsa_unit_params_per_agg_pt: Dict[str, dict], 
                              units_complem_params_per_agg_pt: Dict[str, Dict[str, str]], 
                              agg_res_cf_data: Dict[str, pd.DataFrame], 
                              agg_gen_capa_data: Dict[str, pd.DataFrame]) -> Dict[str, List[GenerationUnitData]]:
    """
    Get generation units data to create them hereafter
    :param pypsa_unit_params_per_agg_pt: dict of per aggreg. prod type main Pypsa params
    :param units_complem_params_per_agg_pt: # for each aggreg. prod type, a dict. {complem. param name: source - "from_json_tb_modif"/"from_eraa_data"}
    :param agg_res_cf_data: {country: df with per aggreg. prod type RES capa factor data}
    :param agg_gen_capa_data: {country: df with per aggreg. prod type (installed) generation capa. data}
    """
    countries = list(agg_gen_capa_data)
    prod_type_col = COLUMN_NAMES.production_type
    prod_type_agg_col = f"{prod_type_col}_agg"
    value_col = COLUMN_NAMES.value
    # TODO: set as global constants/unify...
    power_capa_key = "power_capa"
    capa_factor_key = "capa_factors"

    n_spaces_msg = 2

    generation_units_data = {}
    for country in countries:
        print_out_msg(msg_level="info", msg=f"- for country {country}")
        generation_units_data[country] = []
        current_capa_data = agg_gen_capa_data[country]
        current_res_cf_data = agg_res_cf_data[country]
        # get list of assets to be treated from capa. data
        agg_prod_types = list(set(current_capa_data[prod_type_agg_col]))
        # initialize set of params for each unit by using pypsa default values
        current_assets_data = {agg_pt: pypsa_unit_params_per_agg_pt[agg_pt] for agg_pt in agg_prod_types}
        # and loop over pt to add complementary params
        for agg_pt in agg_prod_types:
            print_out_msg(msg_level="info", msg=n_spaces_msg * " " + f"* for aggreg. prod. type {agg_pt}")
            # set and add asset name
            gen_unit_name = set_gen_unit_name(country=country, agg_prod_type=agg_pt)
            current_assets_data[agg_pt]["name"] = gen_unit_name
            # and "type" (the aggreg. prod types used here, with a direct corresp. to PyPSA generators; 
            # made explicit in JSON fixed params files)
            current_assets_data[agg_pt]["type"] = agg_pt
            if agg_pt in units_complem_params_per_agg_pt and len(units_complem_params_per_agg_pt[agg_pt]) > 0:
                # add pnom attribute if needed
                if power_capa_key in units_complem_params_per_agg_pt[agg_pt]:
                    print_out_msg(msg_level="info", msg=2*n_spaces_msg * " " + f"-> add {power_capa_key}")
                    current_power_capa = \
                        get_val_of_agg_pt_in_df(df_data=current_capa_data, prod_type_agg_col=prod_type_agg_col,
                                                agg_prod_type=agg_pt, value_col="power_capacity",
                                                static_val=True)
                    current_assets_data[agg_pt][GEN_UNITS_PYPSA_PARAMS.power_capa] = int(current_power_capa)
                        
                # add pmax_pu when variable for RES/fatal units
                if capa_factor_key in units_complem_params_per_agg_pt[agg_pt]:
                    print_out_msg(msg_level="info", msg=2*n_spaces_msg * " " + f"-> add {capa_factor_key}")
                    current_assets_data[agg_pt][GEN_UNITS_PYPSA_PARAMS.capa_factors] = \
                        get_val_of_agg_pt_in_df(df_data=current_res_cf_data, prod_type_agg_col=prod_type_agg_col,
                                                agg_prod_type=agg_pt, value_col=value_col, static_val=False)
                # max hours for storage-like assets (energy capa/power capa)

                # marginal costs/efficiency, from FuelSources
            generation_units_data[country].append(GenerationUnitData(**current_assets_data[agg_pt]))
    return generation_units_data


def control_min_pypsa_params_per_gen_units(generation_units_data: Dict[str, List[GenerationUnitData]],
                                           pypsa_min_unit_params_per_agg_pt: Dict[str, List[str]]):
    """
    Control that minimal PyPSA parameter infos has been provided before creating generation units
    """
    pypsa_params_errors_list = []
    # loop over countries
    for country, gen_units_data in generation_units_data.items():
        # and unit in them
        for elt_unit_data in gen_units_data:
            current_unit_type = elt_unit_data.type
            pypsa_min_unit_params_set = set(pypsa_min_unit_params_per_agg_pt[current_unit_type])
            params_with_init_val_set = set(elt_unit_data.get_non_none_attr_names())
            missing_pypsa_params = list(pypsa_min_unit_params_set - params_with_init_val_set)
            if len(missing_pypsa_params) > 0:
                current_unit_name = elt_unit_data.name
                current_msg = f"country {country}, unit name {current_unit_name} and type {current_unit_type} -> {missing_pypsa_params}"
                pypsa_params_errors_list.append(current_msg)
    if len(pypsa_params_errors_list) > 0:
        print_errors_list(error_name="on 'minimal' PyPSA gen. units parameters; missing ones for", 
                        errors_list=pypsa_params_errors_list)     
    else:
        print_out_msg(msg_level="info", msg="PyPSA NEEDED PARAMETERS FOR GENERATION UNITS CREATION HAVE BEEN LOADED!")
