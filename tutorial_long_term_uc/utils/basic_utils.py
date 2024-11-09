from datetime import datetime
from typing import Optional, Union

from common.constants_temporal import DAY_OF_WEEK
from common.long_term_uc_io import DATE_FORMAT_PRINT


def str_sanitizer(raw_str: Optional[str], replace_empty_char: bool = True, 
                  ad_hoc_replacements: dict = None) -> Optional[str]:
    # sanitize only if str
    if isinstance(raw_str, str) is False:
        return raw_str

    sanitized_str = raw_str
    sanitized_str = sanitized_str.strip()
    if replace_empty_char is True:
        sanitized_str = sanitized_str.replace(" ", "_")
    sanitized_str = sanitized_str.lower()

    # if specific replacements to be applied
    if ad_hoc_replacements is not None:
        for old_char, new_char in ad_hoc_replacements.items():
            sanitized_str = sanitized_str.replace(old_char, new_char)
    return sanitized_str


def get_key_of_val(val, my_dict: dict, dict_name: str = None):
    corresp_keys = []
    for key in my_dict:
        if val in my_dict[key]:
            corresp_keys.append(key)
    if dict_name is None:
        dict_name = ""
    else:
        dict_name = f" {dict_name}"
    if len(corresp_keys) == 0:
        print(f"[WARNING] No corresponding key found in {dict_name} dict. for value {val} -> None returned")
        return None
    if len(corresp_keys) > 1:
        print(f"[WARNING] Multiple corresponding keys found in{dict_name} dict. for value {val} "
              f"-> only first one returned")
    return corresp_keys[0]


def get_period_str(period_start: datetime, period_end: datetime):
    dow_start = DAY_OF_WEEK[period_start.isoweekday()]
    dow_end = DAY_OF_WEEK[period_end.isoweekday()]
    period_start_str = f"{dow_start} {period_start.strftime(DATE_FORMAT_PRINT)}"
    period_end_str = f"{dow_end} {period_end.strftime(DATE_FORMAT_PRINT)}"
    return f"[{period_start_str}, {period_end_str}]"


def is_str_bool(bool_str: Optional[str]) -> bool:
    if isinstance(bool_str, str) is False:
        return False
    return bool_str.lower() in ["true", "false"]


def cast_str_bool(bool_str: str) -> Union[str, bool]:
    if is_str_bool(bool_str=bool_str) is True:
        return bool(bool_str)
    else:
        return bool_str
    