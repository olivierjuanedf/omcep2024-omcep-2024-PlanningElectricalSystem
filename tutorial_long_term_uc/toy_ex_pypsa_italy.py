# -*- coding: utf-8 -*-
"""
First very simple toy Unit Commitment model of Italy zone - alone... with PyPSA and ERAA data
"""

"""
Fix a few "global" parameters to simply modify a few elements when making "sensitivity tests"
"""
from datetime import datetime, timedelta
from common.uc_run_params import UCRunParams

modeled_countries = ["italy"]  # unique country modeled in this example
year = 2025  # select first ERAA year available, as an example 
climatic_year = 1989  # and a given "climatic year" (to possibly test different climatic*weather conditions)
res_for_reading_test = ["wind_onshore", "wind_offshore", "solar_pv"]
uc_period_start = datetime(year=1900, month=1, day=1)
uc_period_end = uc_period_start + timedelta(days=14)
uc_run_params = UCRunParams(selected_countries=modeled_countries, selected_target_year=year, 
                            selected_climatic_year=climatic_year, 
                            selected_agg_prod_types={"italy": res_for_reading_test},
                            uc_period_start=uc_period_start,
                            uc_period_end=uc_period_end)
AGG_PROD_TYPES_DEF = {"res_capa-factors": {"solar_pv": ["lfsolarpv"],
                                           "solar_thermal": ["csp_nostorage"], 
                                           "wind_offshore": ["wind_offshore"],
                                           "wind_onshore": ["wind_onshore"]
                                           },
                      "generation_capas": {"batteries": ["batteries"],
                                           "biofuel": ["biofuel"],
                                           "coal": ["coal", "hard_coal", "lignite"],
                                           "dsr": ["demand_side_response_capacity"],
                                           "gas": ["gas"],
                                           "hydro_pondage": ["hydro_pondage"],
                                           "hydro_pump_storage_closed_loop": ["hydro_pump_storage_closed_loop"],
                                           "hydro_pump_storage_open_loop": ["hydro_pump_storage_open_loop"],
                                           "hydro_reservoir": ["hydro_reservoir"],
                                           "hydro_run_of_river": ["hydro_run_of_river"],
                                           "nuclear": ["nuclear"], "oil": ["oil"],
                                           "others_fatal": ["others_non-renewable", "others_renewable"],
                                           "solar_pv": ["solar_photovoltaic"],
                                           "solar_thermal": ["solar_thermal"],
                                           "wind_offshore": ["wind_offshore"], "wind_onshore": ["wind_onshore"]
                                        }
                      }
"""
Get needed data
"""
from utils.eraa_data_reader import get_countries_data

# get data for Italy... just for test 
demand, agg_cf_data, agg_gen_capa_data = \
    get_countries_data(uc_run_params=uc_run_params, agg_prod_types_with_cf_data=res_for_reading_test,
                       aggreg_prod_types_def=AGG_PROD_TYPES_DEF)

# in this case decompose aggreg. CF data into three sub-dicts (for following ex. to be more explicit)
from utils.df_utils import selec_in_df_based_on_list
solar_pv = {"italy": selec_in_df_based_on_list(df=agg_cf_data["italy"], selec_col="production_type_agg",
                                               selec_vals=["solar_pv"], rm_selec_col=True)}
wind_on_shore = {"italy": selec_in_df_based_on_list(df=agg_cf_data["italy"], selec_col="production_type_agg",
                                                    selec_vals=["wind_onshore"], rm_selec_col=True)}
wind_off_shore = {"italy": selec_in_df_based_on_list(df=agg_cf_data["italy"], selec_col="production_type_agg",
                                                     selec_vals=["wind_offshore"], rm_selec_col=True)}

"""Initialize PyPSA Network (basis of all!). And print it to check that for now it is... empty"""
import pypsa
print("Initialize PyPSA network")
network = pypsa.Network(snapshots=demand[modeled_countries[0]].index)
network

"""Add bus for considered country"""

# N.B. Italy coordinates set randomly!
from italy_parameters import gps_coords
coordinates = {"italy": gps_coords}
for country in modeled_countries:
    network.add("Bus", name=f"{country.capitalize()}", x=coordinates[country][0], y=coordinates[country][1])

"""Generators definition, beginning with only simple parameters. Almost "real Italy"... excepting hydraulic storage and Demand-Side Response capacity"""

# N.B. In this toy example values directly set in italy_parameters.py
# p_nom -> capacity (MW)
# p_min_pu -> minimal power level - as % of capacity, set to 0 to start simple
# p_max_pu -> idem, maximal power. Can integrate Capacity Factors (or maintenance)
country_trigram = country.upper()[:3]
from fuel_sources import FUEL_SOURCES
from italy_parameters import get_generators
generators = get_generators(country_trigram=country_trigram, fuel_sources=FUEL_SOURCES, 
                            wind_on_shore_data=wind_on_shore[country], wind_off_shore_data=wind_off_shore[country],
                            solar_pv_data=solar_pv[country])

"""Loop over previous dictionary to add each of the generators to the PyPSA network"""
for generator in generators:
    network.add("Generator", bus=f"{country.capitalize()}", **generator, )

"""Add load"""

loads = [
    {"name": f"{country.capitalize()}-load", "bus": f"{country.capitalize()}",
     "carrier": "AC", "p_set": demand[country]["value"].values},
]

"""Add loads, here unique for now"""

for load in loads:
    network.add("Load", **load)

"""Print the network after having completed it"""

network

"""Plot network. Maybe better when having multiple buses (countries)"""

network.plot(
    title="Mixed AC (blue) - DC (red) network - DC (cyan)",
    color_geomap=True,
    jitter=0.3,
)

"""Print out list of generators"""

network.generators

""""OPtimize network" i.e., solve the associated Unit-Commitment pb"""

result = network.optimize(solver_name="highs")
print(result)
print(f"Total cost at optimum: {network.objective:.2f}")

"""**[Optional]** For those who want to get a standard .lp file containing the equations associated to the solved pb"""

from pathlib import Path
import pypsa.optimization as opt
from common.long_term_uc_io import OUTPUT_DATA_FOLDER
m = opt.create_model(network)
m.to_file(Path(f'{OUTPUT_DATA_FOLDER}/model_{country_trigram.lower()}.lp'))

"""Plot a few info/results"""
import matplotlib.pyplot as plt

print("Plot generation and prices figures")

# p_nom_opt is the optimized capacity (that can be also a variable in PyPSA...
# but here not optimized -> values in input data plotted)
network.generators.p_nom_opt.drop(f"Failure_{country_trigram}").div(1e3).plot.bar(ylabel="GW", figsize=(8, 3))
# [Coding trick] Matplotlib can directly adapt size of figure to fit with values plotted
plt.tight_layout()

# And "stack" of optimized production profiles
network.generators_t.p.div(1e3).plot.area(subplots=False, ylabel="GW")
from common.long_term_uc_io import set_prod_figure, set_price_figure
plt.savefig(set_prod_figure(country=country, year=year, start_horizon=uc_run_params.uc_period_start))
plt.tight_layout()

# Finally, "marginal prices" -> meaning? How can you interprete the very constant value plotted?
network.buses_t.marginal_price.mean(1).plot.area(figsize=(8, 3), ylabel="Euro per MWh")
plt.savefig(set_price_figure(country=country, year=year, start_horizon=uc_run_params.uc_period_start))
plt.tight_layout()
