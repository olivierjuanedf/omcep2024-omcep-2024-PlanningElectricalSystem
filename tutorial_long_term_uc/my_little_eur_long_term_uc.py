"""
Read JSON parametrization files... and check coherence of them
"""
from utils.read import read_and_check_uc_run_params

eraa_data_descr, uc_run_params = read_and_check_uc_run_params()

"""
Get needed data (demand, RES Capa. Factors, installed generation capacities)
"""
from utils.eraa_data_reader import get_countries_data
from utils.basic_utils import get_period_str


uc_period_msg = get_period_str(period_start=uc_run_params.uc_period_start, 
                               period_end=uc_run_params.uc_period_end)

print(f"Read needed ERAA ({eraa_data_descr.eraa_edition}) data for period {uc_period_msg}")
demand, agg_cf_data, agg_gen_capa_data = \
  get_countries_data(countries=uc_run_params.selected_countries,
                     year=uc_run_params.selected_target_year,
                     climatic_year=uc_run_params.selected_climatic_year,
                     selec_agg_prod_types=uc_run_params.selected_agg_prod_types,
                     agg_prod_types_with_cf_data=eraa_data_descr.agg_prod_types_with_cf_data,
                     aggreg_prod_types_def=eraa_data_descr.aggreg_prod_types_def,
                     period_start=uc_run_params.uc_period_start, period_end=uc_run_params.uc_period_end)

print("THE END of European PyPSA-ERAA UC simulation")