import pandas as pd
from typing import Dict


def get_generation_units_data(agg_res_cf_data: Dict[str, pd.DataFrame], agg_gen_capa_data: Dict[str, pd.DataFrame]):
    """
    :param agg_res_cf_data: {country: df with per aggreg. prod type RES capa factor data}
    :param agg_gen_capa_data: {country: df with per aggreg. prod type (installed) generation capa. data}
    """
    # add pnom attribute for all units
     
    # add pmax_pu static, or variable for RES/fatal ones

    # max hours for storage-like assets (energy capa/power capa)

    # marginal costs/efficiency, from FuelSources