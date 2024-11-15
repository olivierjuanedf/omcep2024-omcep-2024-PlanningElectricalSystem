import sys
from typing import Optional

from common.error_msgs import print_out_msg


# TODO: Dict[str, Dict[str, List[str]]], Dict[str, List[int]], Dict[str, Dict[str, Union[str or num]]]


def check_str(data_val) -> bool:
    return isinstance(data_val, str)


def check_list_of_given_type(data_val, needed_type: type) -> bool:
    if isinstance(data_val, list) is False:
        return False
    return all([isinstance(elt, needed_type) for elt in data_val])


def check_list_of_int(data_val) -> bool:
    return check_list_of_given_type(data_val=data_val, needed_type=int)


def check_none_or_list_of_str(data_val) -> bool:
    if data_val is None:
        return True
    return check_list_of_given_type(data_val=data_val, needed_type=str)


def check_str_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    keys_and_vals = list(data_val.keys())
    keys_and_vals.extend(data_val.values())
    return all([isinstance(elt, str) for elt in keys_and_vals])


def check_three_level_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    return all([(isinstance(key, str) and check_str_str_dict(data_val=val)) for key, val in data_val.items()])


def apply_data_type_check(data_type: str, data_val) -> bool:
    if data_type not in CHECK_FUNCTIONS:
        print_out_msg(msg_level="error", msg=f"Unknown data type for check {data_type} -> STOP")
        sys.exit(1)
    if CHECK_FUNCTIONS[data_type] is None:
        print_out_msg(msg_level="error", 
                      msg=f"Function to check data type {data_type} is None (not defined) -> STOP")
        sys.exit(1)


# correspondence between types and associated functions (and additional keyword args when applicable) 
# to be applied for type check
CHECK_FUNCTIONS = {"dict_str_dict": None, "dict_str_str": (check_str_str_dict,),
                   "dict_str_list_of_float": None,
                   "list_of_int": (check_list_of_given_type, {"needed_type": int}),
                   "list_of_str": (check_list_of_given_type, {"needed_type": str}),
                   "none_or_list_of_str": (check_none_or_list_of_str,),
                   "str": (check_str,), 
                   "two_level_dict_str_str_list-of-str": None,
                   "two_level_dict_str_str_str": None}
