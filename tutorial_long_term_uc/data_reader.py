import os
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

from common.constants_datatypes import DATATYPE_NAMES
from common.constants_temporal import DAY_OF_WEEK
from long_term_uc_io import INPUT_ERAA_FOLDER, DT_SUBFOLDERS, DT_FILE_PREFIX, COLUMN_NAMES, \
    FILES_FORMAT, DATE_FORMAT, DATE_FORMAT_PRINT
from utils.df_utils import cast_df_col_as_date, concatenate_dfs, selec_in_df_based_on_list, \
    set_aggreg_col_based_on_corresp, get_subdf_from_date_range



def filter_input_data(df: pd.DataFrame, date_col: str, climatic_year_col: str, period_start: datetime, 
                      period_end: datetime, climatic_year: int) -> pd.DataFrame:
    # ERAA date format not automatically cast by pd
    df = cast_df_col_as_date(df=df, date_col=date_col, date_format=DATE_FORMAT)
    # keep only wanted date range
    df_filtered = get_subdf_from_date_range(df=df, date_col=date_col, date_min=period_start, date_max=period_end)
    # then selected climatic year
    df_filtered = selec_in_df_based_on_list(df=df_filtered, selec_col=climatic_year_col, 
                                            selec_vals=[climatic_year], rm_selec_col=True)
    return df_filtered


def set_aggreg_cf_prod_types_data(df_cf_list: List[pd.DataFrame], prod_type_col: str, pt_agg_col: str, val_col: str,
                                  agg_prod_types_def: Dict[str, List[str]]) -> pd.DataFrame:
    # concatenate, aggreg. over prod type of same aggreg. type and avg
    df_cf_agg = concatenate_dfs(dfs=df_cf_list)
    df_cf_agg = set_aggreg_col_based_on_corresp(df=df_cf_agg, col_name=prod_type_col, agg_col_name=pt_agg_col, 
                                                val_col=val_col, agg_corresp=agg_prod_types_def,
                                                aggreg_ope="mean")
    return df_cf_agg


def get_countries_data(countries: List[str], year: int, climatic_year: int, 
                       selec_prod_types: Dict[str, List[str]], agg_prod_types_with_cf_data: List[str],
                       aggreg_prod_types_def: Dict[str, List[str]], period_start: datetime, 
                       period_end: datetime = None) -> (Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]):
    # set default end of period if not provided
    n_days_period_default = 9
    if period_end is None:
        period_end = period_start + timedelta(days=n_days_period_default)
        print(f"End of period set to default value: {period_end:%Y/%m/%d} (period of {n_days_period_default} days)")
    dow_start = DAY_OF_WEEK[period_start.isoweekday()]
    dow_end = DAY_OF_WEEK[period_end.isoweekday()]
    print(f"ERAA data for period [{dow_start} {period_start.strftime(DATE_FORMAT_PRINT)}, {dow_end} {period_end.strftime(DATE_FORMAT_PRINT)}]")

    # get - per datatype - folder names
    demand_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.demand)
    res_cf_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.res_capa_factors)
    gen_capas_folder = os.path.join(INPUT_ERAA_FOLDER, DT_SUBFOLDERS.generation_capas)
    # file prefix
    demand_prefix = DT_FILE_PREFIX.demand
    res_cf_prefix = DT_FILE_PREFIX.res_capa_factors
    gen_capas_prefix = DT_FILE_PREFIX.generation_capas
    # column names
    date_col = COLUMN_NAMES.date
    climatic_year_col = COLUMN_NAMES.climatic_year
    prod_type_col = COLUMN_NAMES.production_type
    prod_type_agg_col = f"{prod_type_col}_agg"
    value_col = COLUMN_NAMES.value
    # separators for csv reader
    column_sep = FILES_FORMAT.column_sep
    decimal_sep = FILES_FORMAT.decimal_sep

    demand = {}
    agg_cf_data = {}

    n_spaces_msg = 2

    for country in countries:
        print(f"For country: {country}")
        # read csv files
        # [Coding trick] f"{year}_{country}" directly fullfill string with value of year 
        # and country variables (f-string completion)
        current_suffix = f"{year}_{country}"  # common suffix to all ERAA data files
        # get demand
        print("Get demand")
        current_df_demand = pd.read_csv(f"{demand_folder}/{demand_prefix}_{current_suffix}.csv",
                                        sep=column_sep, decimal=decimal_sep)
        # then keep only selected period date range and climatic year
        demand[country] = filter_input_data(df=current_df_demand, date_col=date_col, 
                                            climatic_year_col=climatic_year_col, period_start=period_start,
                                            period_end=period_end, climatic_year=climatic_year)

        # get RES capacity factor data
        print("Get RES capacity factors")
        agg_cf_data[country] = {}
        for agg_prod_type in selec_prod_types[country]:
            # if prod type with CF data
            if agg_prod_type in agg_prod_types_with_cf_data:
                print(n_spaces_msg * " " + f"- For aggreg. prod. type: {agg_prod_type}")
                current_df_res_cf_list = []
                aggreg_pt_cf_def = aggreg_prod_types_def[DATATYPE_NAMES.capa_factor]
                for prod_type in aggreg_pt_cf_def[agg_prod_type]:
                    cf_data_file = f"{res_cf_folder}/{res_cf_prefix}_{prod_type}_{current_suffix}.csv"
                    if os.path.exists(cf_data_file) is False:
                        print(2*n_spaces_msg * " " + f"[WARNING] RES capa. factor data file does not exist: {prod_type} not accounted for here")
                    else:
                        print(2*n_spaces_msg * " " + f"* Prod. type: {prod_type}")
                        current_df_res_cf = pd.read_csv(cf_data_file, sep=column_sep, decimal=decimal_sep) 
                        current_df_res_cf = \
                            filter_input_data(df=current_df_res_cf, date_col=date_col,
                                              climatic_year_col=climatic_year_col, 
                                              period_start=period_start, period_end=period_end, 
                                              climatic_year=climatic_year)
                        if len(current_df_res_cf) == 0:
                            print(2*n_spaces_msg * " " + f"[WARNING] No RES capa. factor data for prod. type {prod_type} and climatic year {climatic_year}")
                        else:
                            # add column with production type (for later aggreg.)
                            current_df_res_cf[prod_type_col] = prod_type
                            current_df_res_cf_list.append(current_df_res_cf)
                if len(current_df_res_cf_list) == 0:
                    print(n_spaces_msg * " " + f"[WARNING] No data available for aggregate RES prod. type {agg_prod_type} -> not accounted for in UC model here")
                else:
                    # concatenate, aggreg. over prod type of same aggreg. type and avg
                    agg_cf_data[country] = \
                        set_aggreg_cf_prod_types_data(df_cf_list=current_df_res_cf_list, prod_type_col=prod_type_col,
                                                      pt_agg_col=prod_type_agg_col, val_col=value_col,
                                                      agg_prod_types_def=aggreg_pt_cf_def)
    return demand, agg_cf_data
    