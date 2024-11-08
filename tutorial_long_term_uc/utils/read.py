import json

from utils.dir_utils import check_file_existence


def check_and_load_json_file(json_file: str, file_descr: str = None) -> dict:
    check_file_existence(file=json_file, file_descr=file_descr)

    f = open(json_file, mode="r", encoding='utf-8')

    # rk: when reading null values in a JSON file they are converted to None
    json_data = json.loads(f.read())

    return json_data
