import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

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
    carrier: str = None
    p_nom: float = None
    p_min_pu: float = None
    p_max_pu: float = None
    efficiency: float = None
    marginal_cost: float = None
    committable: bool = False


def get_val_of_agg_pt_in_df(df_data: pd.DataFrame, prod_type_agg_col: str, 
                            agg_prod_type: str, value_col: str) -> float:
    return df_data[df_data[prod_type_agg_col] == agg_prod_type][value_col].iloc[0]


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

    generation_units_data = {}
    for country in countries:
        generation_units_data[country] = []
        current_capa_data = agg_gen_capa_data[country]
        current_res_cf_data = agg_res_cf_data[country]
        # get list of assets to be treated from capa. data
        agg_prod_types = list(set(current_capa_data[prod_type_agg_col]))
        # initialize set of params for each unit by using pypsa default values
        current_assets_data = {agg_pt: pypsa_unit_params_per_agg_pt[agg_pt] for agg_pt in agg_prod_types}
        # and loop over pt to add complementary params
        for agg_pt in agg_prod_types:
            # set and add asset name
            gen_unit_name = set_gen_unit_name(country=country, agg_prod_type=agg_pt)
            current_assets_data[agg_pt]["name"] = gen_unit_name
            if agg_pt in units_complem_params_per_agg_pt and len(units_complem_params_per_agg_pt[agg_pt]) > 0:
                # add pnom attribute if needed
                if "power_capa" in units_complem_params_per_agg_pt[agg_pt]:
                    current_assets_data[agg_pt][GEN_UNITS_PYPSA_PARAMS.power_capa] = \
                        get_val_of_agg_pt_in_df(df_data=current_capa_data, prod_type_agg_col=prod_type_agg_col,
                                                agg_prod_type=agg_pt, value_col=value_col)
                # add pmax_pu when variable for RES/fatal units
                if "capa_factor" in units_complem_params_per_agg_pt[agg_pt]:
                    current_assets_data[agg_pt][GEN_UNITS_PYPSA_PARAMS.capa_factors] = \
                        get_val_of_agg_pt_in_df(df_data=current_res_cf_data, prod_type_agg_col=prod_type_agg_col,
                                                agg_prod_type=agg_pt, value_col=value_col)
                # max hours for storage-like assets (energy capa/power capa)

                # marginal costs/efficiency, from FuelSources
            generation_units_data[country].append(GenerationUnitData(**current_assets_data[agg_pt]))
    return generation_units_data
