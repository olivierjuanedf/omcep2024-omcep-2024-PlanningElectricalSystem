import pandas as pd
from typing import Dict, List

from utils.basic_utils import get_key_of_val


def selec_in_df_based_on_list(df: pd.DataFrame, selec_col, selec_vals: list, rm_selec_col: bool = False) \
        -> pd.DataFrame:
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


def set_aggreg_col_based_on_corresp(df: pd.DataFrame, col_name: str, agg_col_name: str, val_col: str,
                                    agg_corresp: Dict[str, List[str]], aggreg_ope) -> pd.DataFrame:
    df[agg_col_name] = df[col_name].apply(get_key_of_val, args=(agg_corresp,)) 
    df = df.groupby(agg_col_name).agg({agg_col_name: lambda x: x[0], val_col: aggreg_ope}).reset_index(drop=True)
    return df


def get_subdf_from_date_range(df: pd.DataFrame, date_col: str, date_min: datetime, date_max: datetime) -> pd.DataFrame:
    """
    Get values in a dataframe from a date range
    """
    df_range = df[(date_min <= df[date_col]) & (df[date_col] < date_max)]
    return df_range
