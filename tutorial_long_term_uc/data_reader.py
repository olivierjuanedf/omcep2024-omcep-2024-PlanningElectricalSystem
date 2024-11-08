import os
from typing import Dict, List
import pandas as pd
import numpy as np

from long_term_uc_io import INPUT_ERAA_FOLDER, DT_SUBFOLDERS, DT_FILE_PREFIX, COLUMN_NAMES, FILES_FORMAT
from utils.basic_utils import get_key_of_val
from utils.df_utils import concatenate_dfs, selec_in_df_based_on_list


def aggreg_cf_prod_types_data(df_cf_list: List[pd.DataFrame], pt_agg_col: str, val_col: str, 
                              agg_prod_types: Dict[str, List[str]]) -> pd.DataFrame:
    # concatenate, aggreg. over prod type of same aggreg. type and avg
    df_cf_agg = concatenate_dfs(dfs=df_cf_list)
    df_cf_agg[pt_agg_col] = df_cf_agg.apply(get_key_of_val, args=(agg_prod_types,)) 
    df_cf_agg = df_cf_agg.groupby(pt_agg_col).agg({val_col: np.mean}).reset_index(drop=True)
    return df_cf_agg


def get_countries_data(countries: List[str], year: int, climatic_year: int, 
                       selec_prod_types: Dict[str, List[str]], agg_prod_types_with_cf_data: List[str],
                       aggreg_prod_types: Dict[str, List[str]]) -> (Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]):
    # get - per datatype - folder names
    demand_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.demand)
    res_cf_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.res_capa_factors)
    gen_capas_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.generation_capas)
    # file prefix
    demand_prefix = DT_FILE_PREFIX.demand
    res_cf_prefix = DT_FILE_PREFIX.res_capa_factors
    gen_capas_prefix = DT_FILE_PREFIX.generation_capas
    # column names
    climatic_year_col = COLUMN_NAMES.climatic_year
    prod_type_col = COLUMN_NAMES.production_type
    prod_type_agg_col = f"{prod_type_col}_agg"
    value_col = COLUMN_NAMES.value
    # separators for csv reader
    column_sep = FILES_FORMAT.column_sep
    decimal_sep = FILES_FORMAT.decimal_sep

    # [Coding trick] A bit "technical" operation directly done after reading
    # -> groubpy, to get all data with same climatic_year values together
    # [Coding trick] f"{year}" directly fullfill string with value of year variable
    full_demand = {}
    full_cf_data = {}
    demand = {}
    cf_data = {}
    agg_cf_data = {}

    for country in countries:
        # read csv files
        current_suffix = f"{year}_{country}"  # common suffix to all ERAA data files
        # get demand
        full_demand[country] = pd.read_csv(f"{demand_folder}/{demand_prefix}_{current_suffix}.csv", sep=";", index_col=1, parse_dates=True)
        # then keep only selected climatic year
        demand[country] = selec_in_df_based_on_list(df=full_demand[country], 
                                                    selec_col=climatic_year_col, 
                                                    selec_vals=[climatic_year], rm_selec_col=True)

        # get RES capacity factor data
        full_cf_data[country] = {}
        cf_data[country] = {}
        for agg_prod_type in selec_prod_types[country]:
            # if prod type with CF data
            if agg_prod_type in agg_prod_types_with_cf_data:
                current_df_cf_list = []
                for prod_type in aggreg_prod_types[agg_prod_type]:
                    cf_data_file = f"{res_cf_folder}/{res_cf_prefix}_{prod_type}_{current_suffix}.csv"
                    full_cf_data[country][prod_type] = pd.read_csv(cf_data_file, parse_dates=True, sep=";") 
                    cf_data[country][prod_type] = \
                    selec_in_df_based_on_list(df=[country][prod_type],
                                              selec_col=climatic_year_col,
                                              selec_vals=[climatic_year], rm_selec_col=True)
                    current_df_cf_list.append(cf_data[country][prod_type])
                # concatenate, aggreg. over prod type of same aggreg. type and avg
                agg_cf_data[country] = aggreg_cf_prod_types_data(df_cf_list=current_df_cf_list, 
                                                                 pt_agg_col=prod_type_agg_col, 
                                                                 val_col=value_col, 
                                                                 agg_prod_types=aggreg_prod_types)
    return demand, agg_cf_data
    