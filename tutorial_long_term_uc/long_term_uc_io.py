from dataclasses import dataclass


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


COLUMN_NAMES = ColumnNames()
DT_FILE_PREFIX = DtFilePrefix()
DT_SUBFOLDERS = DtSubfolders()
FILES_FORMAT = FilesFormat()
INPUT_ERAA_FOLDER = "data/ERAA_2023-2"
OUTPUT_DATA_FOLDER = "output/long_term_uc/data"
OUTPUT_FIG_FOLDER = "output/long_term_uc/figures"

def set_prod_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prod_{country}_{year}_{start_horizon}.png"


def set_price_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prices_{country}_{year}_{start_horizon}.png"
