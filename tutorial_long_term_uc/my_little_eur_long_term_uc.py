"""
Read JSON parametrization files... and check coherence of them
"""

print("Read JSON parametrization files... and check that modifications are coherent with available ERAA data -> TBD")
countries = ["italy", "france"]
selected_prod_types = {"italy": ["nuclear", "solar_pv"], "france": ["oil", "wind_onshore"]}
agg_prod_types = ["batteries", "biofuel", "coal", "dsr", "gas", "hydro", "nuclear", "oil",
                  "solar_pv", "solar_thermal", "wind_offshore", "wind_onshore"]
agg_pt_with_cf_data = ["solar_pv", "solar_thermal", "wind_offshore", "wind_onshore"]
year = 2025  # select first ERAA year available, as an example 
climatic_year = 2000  # and a given "climatic year" (to possibly test different climatic*weather conditions)

"""
Get needed data
"""
from data_reader import get_countries_data

print("Read needed ERAA (2023.2) data")
demand, agg_cf_data = get_countries_data(countries=countries, year=year, climatic_year=climatic_year,
                                         selec_prod_types=selected_prod_types, agg_prod_types_with_cf_data=agg_pt_with_cf_data,
                                         aggreg_prod_types=agg_prod_types)
