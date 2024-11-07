from typing import List
import pandas as pd

from long_term_uc_io import INPUT_ERAA_FOLDER


def get_countries_data(countries: List[str], year: int, climatic_year: int):
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
        full_demand[country] = pd.read_csv(f"{INPUT_ERAA_FOLDER}/demand_{year}_{country}.csv", sep=";", index_col=1, parse_dates=True).groupby(
            pd.Grouper(key="climatic_year"))
        full_wind_on_shore[country] = pd.read_csv(f"{INPUT_ERAA_FOLDER}/PECD/capa_factor_wind_onshore_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
        pd.Grouper(key="climatic_year"))
        full_wind_off_shore[country] = pd.read_csv(f"{INPUT_ERAA_FOLDER}/PECD/capa_factor_wind_offshore_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
        pd.Grouper(key="climatic_year"))
        full_solar_pv[country] = pd.read_csv(f"{INPUT_ERAA_FOLDER}/PECD/capa_factor_solar_pv_{year}_{country}.csv", index_col=1, parse_dates=True, sep=";").groupby(
        pd.Grouper(key="climatic_year"))
        # then keep only selected climatic year
        demand[country] = full_demand[country].get_group(climatic_year)
        wind_on_shore[country] = full_wind_on_shore[country].get_group(climatic_year)
        wind_off_shore[country] = full_wind_off_shore[country].get_group(climatic_year)
        solar_pv[country] = full_solar_pv[country].get_group(climatic_year)
    return demand, wind_on_shore, wind_off_shore, solar_pv
    