"""
Read JSON parametrization files... and check coherence of them
"""
from utils.read import read_and_check_uc_run_params

eraa_data_descr, uc_run_params = read_and_check_uc_run_params()

selected_prod_types = {"italy": ["nuclear", "solar_pv"], "france": ["oil", "wind_onshore"]}
agg_prod_types_def = {
    "res_capa-factors": {
      "solar_pv": [
        "lfsolarpv"
      ],
      "solar_thermal": [
        "csp_nostorage"
      ],
      "wind_offshore": [
        "wind_offshore"
      ],
      "wind_onshore": [
        "wind_onshore"
      ]
    },
    "generation_capas": {
      "batteries": [
        "batteries"
      ],
      "biofuel": [
        "biofuel"
      ],
      "coal": [
        "coal",
        "hard_coal",
        "lignite"
      ],
      "dsr": [
        "demand_side_response_capacity"
      ],
      "gas": [
        "gas"
      ],
      "hydro": [
        "hydro_pondage",
        "hydro_pump_storage_closed_loop",
        "hydro_pump_storage_open_loop",
        "hydro_reservoir",
        "hydro_run_of_river"
      ],
      "nuclear": [
        "nuclear"
      ],
      "oil": [
        "oil"
      ],
      "solar_pv": [
        "solar_(photovoltaic)",
        "lfsolarpv"
      ],
      "solar_thermal": [
        "solar_(thermal)"
      ],
      "wind_offshore": [
        "wind_offshore"
      ],
      "wind_onshore": [
        "wind_onshore"
      ]
    }
  }
agg_pt_with_cf_data = ["solar_pv", "solar_thermal", "wind_offshore", "wind_onshore"]
year = 2025  # select first ERAA year available, as an example 
climatic_year = 1989  # and a given "climatic year" (to possibly test different climatic*weather conditions)
from datetime import datetime
uc_period_start = datetime(year=1900, month=1, day=1)

"""
Get needed data
"""
from data_reader import get_countries_data

print("Read needed ERAA (2023.2) data")
demand, agg_cf_data = get_countries_data(countries=countries, year=year, climatic_year=climatic_year,
                                         selec_prod_types=selected_prod_types, agg_prod_types_with_cf_data=agg_pt_with_cf_data,
                                         aggreg_prod_types_def=agg_prod_types_def, period_start=uc_period_start)

print("THE END of European PyPSA-ERAA UC simulation")