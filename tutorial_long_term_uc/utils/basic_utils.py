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
