# -*- coding: utf-8 -*-
"""Copie de toy_example_pypsa_v2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17wzJZx_pnNkNnJpV2heuB0gTW-X_ajD6
"""
import os
from pathlib import Path

# Commented out IPython magic to ensure Python compatibility.
# %pip install pypsa[highs] "xarray>=2023.8.0" Cartopy highspy

"""Needed imports"""

import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

"""Fix a few "global" parameters to simply modify a few elements when making "sensitivity tests"
"""

countries = ["germany", "poland", "france", "iberian-peninsula", "scandinavia",
             "benelux", "italy"]
year = 2025
climatic_year = 2000
start_horizon = 31 * 24
time_horizon_in_hours = 7 * 24

"""Get needed data - that should be put in a created data subfolder here

"""

# [Coding trick] A bit "technical" operation directly done after reading
# -> groubpy, to get all data with same climatic_year values together
# [Coding trick] f"{year}" directly fullfill string with value of year variable
full_demand = {}
full_wind_on_shore = {}
full_wind_off_shore = {}
full_solar_pv = {}
full_solar_csp = {}
demand = {}
wind_off_shore = {}
wind_on_shore = {}
solar_pv = {}
solar_csp = {}
for country in countries:
    # read csv files
    full_demand[country] = pd.read_csv(f"data/ERAA_2023-2/demand_{year}_{country}.csv", sep=";", index_col=1, parse_dates=True).groupby(
        pd.Grouper(key="climatic_year"))
    full_wind_on_shore[country] = pd.read_csv(f"data/ERAA_2023-2/PECD/capa_factor_wind_onshore_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
      pd.Grouper(key="climatic_year"))
    full_wind_off_shore[country] = pd.read_csv(f"data/ERAA_2023-2/PECD/capa_factor_wind_offshore_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
      pd.Grouper(key="climatic_year"))
    full_solar_pv[country] = pd.read_csv(f"data/ERAA_2023-2/PECD/capa_factor_solar_pv_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
      pd.Grouper(key="climatic_year"))
    # then keep only selected climatic year
    demand[country] = full_demand[country].get_group(climatic_year)
    wind_on_shore[country] = full_wind_on_shore[country].get_group(climatic_year)
    wind_off_shore[country] = full_wind_off_shore[country].get_group(climatic_year)
    solar_pv[country] = full_solar_pv[country].get_group(climatic_year)

"""Get data only for the considered climatic year

**[Optional, for better parametrization of assets]**
"""

# [Coding trick] dataclass is a simple way to define object to store multiple attributes
@dataclass
class FuelSources:
    name: str
    co2_emissions: float
    committable: bool
    min_up_time: float
    min_down_time: float
    energy_density_per_ton: float  # in MWh / ton
    cost_per_ton: float
    primary_cost: float = None  # € / MWh (multiply this by the efficiency of your power plant to get the marginal cost)
# [Coding trick] this function will be applied automatically at initialization of an object of this class
    def __post_init__(self):
      if self.energy_density_per_ton != 0:
          self.primary_cost = self.cost_per_ton / self.energy_density_per_ton
      else:
          self.primary_cost = 0

"""**[Optional, following previous point]** Define dictionary of asset parameters"""

fuel_sources = {
    "Coal": FuelSources("Coal", 760, True, 4, 4, 8, 128),
    "Gas": FuelSources("Gas", 370, True, 2, 2, 14.89, 134.34),
    "Oil": FuelSources("Oil", 406, True, 1, 1, 11.63, 555.78),
    "Uranium": FuelSources("Uranium", 0, True, 10, 10, 22394, 150000.84),
    "Solar": FuelSources("Solar", 0, False, 1, 1, 0, 0),
    "Wind": FuelSources("Wind", 0, False, 1, 1, 0, 0),
    "Hydro": FuelSources("Hydro", 0, True, 2, 2, 0, 0),
    "Biomass": FuelSources("Biomass", 0, True, 2, 2, 5, 30)
}
# print a given attribute, of asset Coal here, to check proper initialization
fuel_sources["Coal"].primary_cost

"""Initialize PyPSA Network (basis of all!). And print it to check that for now it is... empty"""

modeled_countries = ["italy"]  # unique country modeled in this example
network = pypsa.Network(snapshots=demand[modeled_countries[0]].index[0:time_horizon_in_hours])
network

"""Add bus for considered country"""

# [Coding trick] capitalize to put a string with first character in capital letter
# N.B. Italy coordinates set randomly!
coordinates = {"italy": (12.5674, 41.8719)}
for country in modeled_countries:
    network.add("Bus", name=f"{country.capitalize()}", x=coordinates[country][0], y=coordinates[country][1])

"""Generators definition, beginning with only simple parameters. Almost "real Italy"... excepting hydraulic storage and Demand-Side Response capacity"""

# N.B. Look at the values in file ERAA2023 PEMMDB Generation.xlsx/Sheet TY
# p_nom -> capacity (MW)
# p_min_pu -> minimal power level - as % of capacity, set to 0 to start simple
# p_max_pu -> idem, maximal power. Can integrate Capacity Factors (or maintenance)
country_trigram = country.upper()[:3]
generators = [
    {"name": f"Hard-Coal_{country_trigram}", "carrier": "Coal", "p_nom": 2362,
     "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Coal"].primary_cost * 0.37,
     "efficiency": 0.37, "committable": False},
    {"name": f"Gas_{country_trigram}", "carrier": "Gas", "p_nom": 43672,
     "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Gas"].primary_cost * 0.5,
     "efficiency": 0.5, "committable": False},
    {"name": f"Oil_{country_trigram}", "carrier": "Oil", "p_nom": 866,
     "p_min_pu": 0, "p_max_pu": 1,
     "marginal_cost": fuel_sources["Gas"].primary_cost * 0.4,
     "efficiency": 0.4, "committable": False},
    {"name": f"Other-non-renewables_{country_trigram}",
     "carrier": "Other-non-renewables", "p_nom": 8239, "p_min_pu": 0,
     "p_max_pu": 1, "marginal_cost": fuel_sources["Gas"].primary_cost * 0.4,
     "efficiency": 0.4, "committable": False},
    {"name": f"Wind-on-shore_{country_trigram}", "carrier": "Wind",
     "p_nom": 14512, "p_min_pu": 0,
     "p_max_pu": wind_on_shore[country][start_horizon:start_horizon+time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Wind"].primary_cost, "efficiency": 1,
     "committable": False},
    {"name": f"Wind-off-shore_{country_trigram}", "carrier": "Wind",
     "p_nom": 791, "p_min_pu": 0,
     "p_max_pu": wind_on_shore[country][start_horizon:start_horizon+time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Wind"].primary_cost, "efficiency": 1,
     "committable": False},
    {"name": f"Solar-pv_{country_trigram}", "carrier": "Solar", "p_nom": 39954,
     "p_min_pu": 0, "p_max_pu": solar_pv[country][:time_horizon_in_hours]["value"].values,
     "marginal_cost": fuel_sources["Solar"].primary_cost, "efficiency": 1,
     "committable": False},
    {"name": f"Other-renewables_{country_trigram}", "carrier": "Other-renewables",
     "p_nom": 4466, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": 0,
     "efficiency": 1, "committable": False},
    # what is this - very necessary - last fictive asset?
    {"name": f"Failure_{country_trigram}", "carrier": "Failure",
     "p_nom": 1e10, "p_min_pu": 0, "p_max_pu": 1, "marginal_cost": 1e5,
     "efficiency": 1, "committable": False}
]

"""Loop over previous dictionary to add each of the generators to the PyPSA network"""

# [Coding trick] ** allows to pass a variable number of keyword args to a function
# see https://www.guvi.in/blog/python-single-double-asterisk/
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

import pypsa.optimization as opt

m = opt.create_model(network)
os.makedirs('output', exist_ok=True)
m.to_file(Path('output/model.lp'))

"""Plot a few info/results"""

# p_nom_opt is the optimized capacity (that can be also a variable in PyPSA...
# but here not optimized -> values in input data plotted)
network.generators.p_nom_opt.drop(f"Failure_{country_trigram}").div(1e3).plot.bar(ylabel="GW", figsize=(8, 3))
# [Coding trick] Matplotlib can directly adapt size of figure to fit with values plotted
plt.tight_layout()

# And "stack" of optimized production profiles
network.generators_t.p.div(1e3).plot.area(subplots=False, ylabel="GW")
plt.savefig(f"output/prod_{country}_{year}_{start_horizon}.png")
plt.tight_layout()

# Finally, "marginal prices" -> meaning? How can you interprete the very constant value plotted?
network.buses_t.marginal_price.mean(1).plot.area(figsize=(8, 3), ylabel="Euro per MWh")
plt.tight_layout()

