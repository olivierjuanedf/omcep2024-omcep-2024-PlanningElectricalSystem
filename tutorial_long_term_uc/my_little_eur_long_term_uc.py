"""
Read JSON parametrization files... and check coherence of them
"""
from utils.read import read_and_check_uc_run_params

eraa_data_descr, uc_run_params = read_and_check_uc_run_params()

"""
Get needed data (demand, RES Capa. Factors, installed generation capacities)
"""
from data_reader import get_countries_data
from common.constants_temporal import DAY_OF_WEEK
from common.long_term_uc_io import DATE_FORMAT_PRINT

period_start = uc_run_params.uc_period_start
period_end = uc_run_params.uc_period_end
dow_start = DAY_OF_WEEK[period_start.isoweekday()]
dow_end = DAY_OF_WEEK[period_end.isoweekday()]
uc_period_msg = f"[{dow_start} {period_start.strftime(DATE_FORMAT_PRINT)}, {dow_end} {period_end.strftime(DATE_FORMAT_PRINT)}]"

print(f"Read needed ERAA ({eraa_data_descr.eraa_edition}) data for period {uc_period_msg}")
demand, agg_cf_data = get_countries_data(countries=uc_run_params.selected_countries, 
                                         year=uc_run_params.selected_target_year, 
                                         climatic_year=uc_run_params.selected_climatic_year,
                                         selec_agg_prod_types=uc_run_params.selected_agg_prod_types, 
                                         agg_prod_types_with_cf_data=eraa_data_descr.agg_prod_types_with_cf_data,
                                         aggreg_prod_types_def=eraa_data_descr.aggreg_prod_types_def, 
                                         period_start=uc_run_params.uc_period_start, period_end=uc_run_params.uc_period_end)

print("THE END of European PyPSA-ERAA UC simulation")