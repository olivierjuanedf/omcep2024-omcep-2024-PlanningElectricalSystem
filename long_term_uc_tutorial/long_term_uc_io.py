INPUT_ERAA_FOLDER = "data/ERAA_2023-2"
OUTPUT_DATA_FOLDER = "output/long-term_uc/data"
OUTPUT_FIG_FOLDER = "output/long-term_uc/figures"

def set_prod_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prod_{country}_{year}_{start_horizon}.png"


def set_price_figure(country: str, year: int, start_horizon: int) -> str:
    return f"{OUTPUT_FIG_FOLDER}/prices_{country}_{year}_{start_horizon}.png"
