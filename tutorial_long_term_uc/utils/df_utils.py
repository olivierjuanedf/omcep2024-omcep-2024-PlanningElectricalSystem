import pandas as pd
from typing import List


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
