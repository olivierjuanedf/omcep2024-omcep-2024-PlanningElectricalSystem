# -*- coding: utf-8 -*-
"""
First very simple toy Unit Commitment model of Italy zone - alone... with PyPSA and ERAA data
"""

"""
Fix a few "global" parameters to simply modify a few elements when making "sensitivity tests"
"""
from long_term_uc_constants import COUNTRIES
year = 2025  # select first ERAA year available, as an example 
climatic_year = 2000  # and a given "climatic year" (to possibly test different climatic*weather conditions)
start_horizon = 31 * 24  # idx of first time-slot of the temporal period to be considered 
time_horizon_in_hours = 7 * 24  # number of - hourly - time-slots in considered period

"""
Get needed data
"""
from data_reader import get_countries_data

# here get data for all (meta-)countries (not only Italy)... just for test 
demand, wind_on_shore, wind_off_shore, solar_pv = \
    get_countries_data(countries=COUNTRIES, year=year, climatic_year=climatic_year)

"""Initialize PyPSA Network (basis of all!). And print it to check that for now it is... empty"""
import pypsa
modeled_countries = ["italy"]  # unique country modeled in this example
network = pypsa.Network(snapshots=demand[modeled_countries[0]].index[0:time_horizon_in_hours])
network

"""Add bus for considered country"""

# [Coding trick] capitalize to put a string with first character in capital letter
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
                            wind_on_shore_data=wind_on_shore[country][start_horizon:start_horizon+time_horizon_in_hours],
                            wind_off_shore_data=wind_off_shore[country][start_horizon:start_horizon+time_horizon_in_hours],
                            solar_pv_data=solar_pv[country][:time_horizon_in_hours])

"""Loop over previous dictionary to add each of the generators to the PyPSA network"""
for generator in generators:
    network.add("Generator", bus=f"{country.capitalize()}", **generator, )

"""Add load"""

loads = [
    {"name": f"{country.capitalize()}-load", "bus": f"{country.capitalize()}",
     "carrier": "AC", "p_set": demand[country][0:time_horizon_in_hours]["value"].values},
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

"""**[Optional]** For those who want to get a standard .lp file containing the equations associated to the solved pb"""

from pathlib import Path
import pypsa.optimization as opt
from long_term_uc_io import OUTPUT_DATA_FOLDER
m = opt.create_model(network)
m.to_file(Path(f'{OUTPUT_DATA_FOLDER}/model_{country_trigram}.lp'))

"""Plot a few info/results"""
import matplotlib.pyplot as plt

# p_nom_opt is the optimized capacity (that can be also a variable in PyPSA...
# but here not optimized -> values in input data plotted)
network.generators.p_nom_opt.drop(f"Failure_{country_trigram}").div(1e3).plot.bar(ylabel="GW", figsize=(8, 3))
# [Coding trick] Matplotlib can directly adapt size of figure to fit with values plotted
plt.tight_layout()

# And "stack" of optimized production profiles
network.generators_t.p.div(1e3).plot.area(subplots=False, ylabel="GW")
from long_term_uc_io import set_prod_figure, set_price_figure
plt.savefig(set_prod_figure(country=country, year=year, start_horizon=start_horizon))
plt.tight_layout()

# Finally, "marginal prices" -> meaning? How can you interprete the very constant value plotted?
network.buses_t.marginal_price.mean(1).plot.area(figsize=(8, 3), ylabel="Euro per MWh")
plt.savefig(set_price_figure(country=country, year=year, start_horizon=start_horizon))
plt.tight_layout()
