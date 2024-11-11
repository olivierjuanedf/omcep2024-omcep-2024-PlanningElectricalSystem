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


DATA_TYPE_CHECKERS = {"str": check_str, "none_or_list_of_str": check_none_or_list_of_str}


def check_data_type(checker_name: str, data_val) -> bool:
    if checker_name not in DATA_TYPE_CHECKERS:
        print_out_msg(msg_level="error", msg="Unknown data type checker name -> STOP")
        sys.exit(1)
    return DATA_TYPE_CHECKERS[checker_name]
