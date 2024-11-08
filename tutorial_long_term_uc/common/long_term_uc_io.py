import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DtSubfolders:
    demand: str = "demand"
    res_capa_factors: str = "res_capa-factors"
    generation_capas: str = "generation_capas"


@dataclass
class DtFilePrefix:
    demand: str = "demand"
    res_capa_factors: str = "capa_factor"
    generation_capas: str = "generation-capa"


@dataclass
class ColumnNames:
    date: str = "date"
    target_year: str = "year"
    climatic_year: str = "climatic_year"
    production_type: str = "production_type"
    value: str = "value"


@dataclass
class FilesFormat:
    column_sep: str = ";"
    decimal_sep: str = "."


@dataclass
class ComplemDataSources:
    from_json_tb_modif: str = "from_json_tb_modif"
    from_eraa_data: str = "from_eraa_data"


COLUMN_NAMES = ColumnNames()
COMPLEM_DATA_SOURCES = ComplemDataSources()
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_PRINT = "%Y/%m/%d"
DT_FILE_PREFIX = DtFilePrefix()
DT_SUBFOLDERS = DtSubfolders()
FILES_FORMAT = FilesFormat()
GEN_CAPA_SUBDT_COLS = ["power_capacity", "power_capacity_turbine", "power_capacity_pumping", 
                       "power_capacity_injection", "power_capacity_offtake"]
INPUT_ERAA_FOLDER = "data/ERAA_2023-2"
INPUT_LT_UC_FOLDER = "input/long_term_uc"
# first date in ERAA data (fictive 364 days calendar)
MIN_DATE_IN_DATA = datetime(year=1900, month=1, day=1)
# first date NOT in ERAA data (fictive 364 days calendar)
MAX_DATE_IN_DATA = datetime(year=1901, month=1, day=1)
OUTPUT_DATA_FOLDER = "output/long_term_uc/data"
OUTPUT_FIG_FOLDER = "output/long_term_uc/figures"


def set_json_fixed_params_file():
    return os.path.join(INPUT_LT_UC_FOLDER, "elec-europe_params_fixed.json")


def set_json_params_tb_modif_file():
    return os.path.join(INPUT_LT_UC_FOLDER, "elec-europe_params_to-be-modif.json")


def set_prod_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prod_{country}_{year}_{start_horizon}.png"


def set_price_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prices_{country}_{year}_{start_horizon}.png"
