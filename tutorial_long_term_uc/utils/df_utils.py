import pandas as pd
from typing import Dict, List
from datetime import datetime

from utils.basic_utils import get_key_of_val


def cast_df_col_as_date(df: pd.DataFrame, date_col: str, date_format: str) -> pd.DataFrame:
    df[date_col] = df[date_col].apply(lambda x: datetime.strptime(x, date_format))
    return df


def selec_in_df_based_on_list(df: pd.DataFrame, selec_col, selec_vals: list, rm_selec_col: bool = False) \
        -> pd.DataFrame:
    pd.options.mode.chained_assignment = None
    selec_bool_col = f"is_selec_{selec_col}"
    df[selec_bool_col] = df[selec_col].apply(lambda x: 1 if x in selec_vals else 0)
    df_selec = df[df[selec_bool_col] == 1]
    if rm_selec_col is True:
        all_cols = list(df_selec.columns)
        all_cols.remove(selec_bool_col)
        df_selec = df_selec[all_cols]
    return df_selec


def concatenate_dfs(dfs: List[pd.DataFrame], reset_index: bool = True) -> pd.DataFrame:
    df_concat = pd.concat(dfs, axis=0)
    if reset_index is True:
        df_concat = df_concat.reset_index(drop=True)
    return df_concat


def set_aggreg_col_based_on_corresp(df: pd.DataFrame, col_name: str, created_agg_col_name: str, val_cols: List[str],
                                    agg_corresp: Dict[str, List[str]], common_aggreg_ope, other_col_for_agg: str = None) -> pd.DataFrame:
    df[created_agg_col_name] = df[col_name].apply(get_key_of_val, args=(agg_corresp,)) 
    agg_operations = {col: common_aggreg_ope for col in val_cols}
    if other_col_for_agg is not None:
        gpby_cols = [created_agg_col_name]
        gpby_cols.append(other_col_for_agg)
    else:
        gpby_cols = created_agg_col_name
    df = df.groupby(gpby_cols).agg(agg_operations).reset_index()
    return df


def get_subdf_from_date_range(df: pd.DataFrame, date_col: str, date_min: datetime, date_max: datetime) -> pd.DataFrame:
    """
    Get values in a dataframe from a date range
    """
    df_range = df[(date_min <= df[date_col]) & (df[date_col] < date_max)]
    return df_range
