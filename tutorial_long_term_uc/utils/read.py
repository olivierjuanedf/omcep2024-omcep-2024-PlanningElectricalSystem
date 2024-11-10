import json

from common.long_term_uc_io import set_json_fixed_params_file, set_json_eraa_avail_values_file, \
      set_json_params_tb_modif_file, set_json_pypsa_static_params_file
from common.constants_extract_eraa_data import ERAADatasetDescr, PypsaStaticParams
from common.uc_run_params import UCRunParams
from common.error_msgs import print_out_msg
from utils.dir_utils import check_file_existence


def check_and_load_json_file(json_file: str, file_descr: str = None) -> dict:
    check_file_existence(file=json_file, file_descr=file_descr)

    f = open(json_file, mode="r", encoding='utf-8')

    # rk: when reading null values in a JSON file they are converted to None
    json_data = json.loads(f.read())

    return json_data


def read_and_check_uc_run_params():
    json_fixed_params_file = set_json_fixed_params_file()
    json_eraa_avail_values_file = set_json_eraa_avail_values_file()
    json_params_tb_modif_file = set_json_params_tb_modif_file()
    print_out_msg(msg_level="info", 
                  msg=f"Read and check long-term UC parameters; the ones modified in file {json_params_tb_modif_file}")

    json_params_fixed = check_and_load_json_file(json_file=json_fixed_params_file,
                                                 file_descr="JSON fixed params")
    json_eraa_avail_values = check_and_load_json_file(json_file=json_eraa_avail_values_file,
                                                      file_descr="JSON ERAA available values")
    # add "avail_" to the different keys of JSON available values to make them more explicit in the following
    json_eraa_avail_values = {f"available_{key}": val for key, val in json_eraa_avail_values.items()}
    # put this dictionary values into the "fixed values" one
    json_params_fixed |= json_eraa_avail_values
    json_params_tb_modif = check_and_load_json_file(json_file=json_params_tb_modif_file,
                                                    file_descr="JSON params to be modif.")

    print_out_msg(msg_level="info", 
                  msg="... and check that modifications done are coherent with available ERAA data")
    eraa_data_descr = ERAADatasetDescr(**json_params_fixed)
    eraa_data_descr.process()
    uc_run_params = UCRunParams(**json_params_tb_modif)
    uc_run_params.process(available_countries=eraa_data_descr.available_countries)
    uc_run_params.coherence_check(eraa_data_descr=eraa_data_descr)
    return eraa_data_descr, uc_run_params


def read_and_check_pypsa_static_params() -> PypsaStaticParams:
    json_pypsa_static_params_file = set_json_pypsa_static_params_file()
    print_out_msg(msg_level="info", 
                  msg=f"Read and check PyPSA static parameters file; the ones modified in file {json_pypsa_static_params_file}")

    json_pypsa_static_params = check_and_load_json_file(json_file=json_pypsa_static_params_file,
                                                        file_descr="JSON PyPSA static params")
    pypsa_static_params = PypsaStaticParams(**json_pypsa_static_params)
    pypsa_static_params.process()
    return pypsa_static_params
