import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from common.constants_extract_eraa_data import ERAADatasetDescr
from common.long_term_uc_io import MIN_DATE_IN_DATA, MAX_DATE_IN_DATA


DATE_FORMAT = "%Y/%m/%d"
N_DAYS_UC_DEFAULT = 9


def uncoherent_param_stop(param_errors: List[str]):
    error_msg = "There are error(s) in JSON params to be modif. file:"
    for elt_error in param_errors:
        error_msg += f"\n- {elt_error}"
    error_msg += "\n-> STOP"
    sys.exit(1)


def check_unique_int_value(param_name: str, param_value) -> Optional[str]:
    if not isinstance(param_value, int):
        f"Unique {param_name} to be provided; must be an int"
    else:
        return None
    

@dataclass
class UCRunParams:
    selected_climatic_year: int
    selected_countries: List[str]
    selected_target_year: int
    selected_agg_prod_types: Dict[str, Optional[List[str]]]
    uc_period_start: Union[str, datetime]
    uc_period_end: Union[str, datetime] = None

    def process(self, available_countries: List[str]):
        # if dates in str format, cast them as datetime 
        # - setting end of period to default value if not provided
        if isinstance(self.uc_period_start, str):
            self.uc_period_start = datetime.strptime(self.uc_period_start, DATE_FORMAT)
        if self.uc_period_end is None:
            self.uc_period_end = min(MAX_DATE_IN_DATA, self.uc_period_start + timedelta(days=N_DAYS_UC_DEFAULT))
            print(f"End of period set to default value: {self.uc_period_end:%Y/%m/%d} (period of {N_DAYS_UC_DEFAULT} days; with bound on 1900, Dec. 31th)")
        elif isinstance(self.uc_period_end, str):
            self.uc_period_end = datetime.strptime(self.uc_period_end, DATE_FORMAT)
        # replace None and missing countries in dict of aggreg. prod. types
        for country in available_countries:
            if country not in self.selected_agg_prod_types \
                or self.selected_agg_prod_types[country] is None:
                self.selected_agg_prod_types[country] = []
    
    def coherence_check(self, eraa_data_descr: ERAADatasetDescr):
        errors_list = []
        # check that there is no repetition of countries
        countries_set = set(self.selected_countries)
        if len(countries_set) < len(self.selected_countries):
            errors_list.append("Repetition in selected countries") 

        # check coherence of values with fixed params
        # for selected countries
        unknown_countries = list(countries_set - set(eraa_data_descr.available_countries))
        if len(unknown_countries) > 0:
            errors_list.append(f"Unknown selected countrie(s): {unknown_countries}")

        # for selected target and climatic years
        # check that unique value provided
        target_yr_msg = check_unique_int_value(param_name="target year", param_value=self.selected_target_year)
        if target_yr_msg is not None:
            errors_list.append(target_yr_msg)
        climatic_yr_msg = check_unique_int_value(param_name="climatic year", param_value=self.selected_climatic_year)
        if climatic_yr_msg is not None:
            errors_list.append(climatic_yr_msg)
        if isinstance(self.selected_target_year, int) \
            and self.selected_target_year not in eraa_data_descr.available_target_years:
            errors_list.append(f"Unknown target year {self.selected_target_year}")
        if isinstance(self.selected_climatic_year, int) \
            and self.selected_climatic_year not in eraa_data_descr.available_climatic_years:
            errors_list.append(f"Unknown climatic year {self.selected_climatic_year}")
        
        # check that countries in aggreg. prod. types are not repeated, and known
        agg_pt_countries = list(self.selected_agg_prod_types)
        agg_pt_countries_set = set(agg_pt_countries)
        msg_suffix = "in keys of dict. of aggreg. prod. types selection"
        if len(agg_pt_countries_set) < len(agg_pt_countries):
            errors_list.append(f"Repetition of countries {msg_suffix}")
        unknown_agg_pt_countries = list(agg_pt_countries_set - set(eraa_data_descr.available_countries))
        if len(unknown_agg_pt_countries) > 0:
            errors_list.append(f"Unknown countrie(s) {msg_suffix}: {unknown_agg_pt_countries}")
 
        # check that aggreg. prod types are not repeated, and known
        msg_suffix = "in values of dict. of aggreg. prod. types selection, for country"
        for elt_country, current_agg_pt in self.selected_agg_prod_types.items():
            current_agg_pt_set = set(current_agg_pt)
            if len(current_agg_pt_set) < len(current_agg_pt):
                errors_list.append(f"Repetition of aggreg. prod. types {msg_suffix} {elt_country}")
            unknown_agg_prod_types = list(current_agg_pt_set - set(eraa_data_descr.available_aggreg_prod_types))
            if len(unknown_agg_prod_types) > 0:
                errors_list.append(f"Unknown aggreg. prod. types {msg_suffix} {elt_country}: {unknown_agg_prod_types}")

        # check that both dates are in allowed period
        allowed_period_msg = f"[{MIN_DATE_IN_DATA.strftime(DATE_FORMAT)}, {MAX_DATE_IN_DATA.strftime(DATE_FORMAT)}]"
        if not (MIN_DATE_IN_DATA <= self.uc_period_start <= MAX_DATE_IN_DATA):
            errors_list.append(f"UC period start {self.uc_period_start.strftime(DATE_FORMAT)} not in allowed period {allowed_period_msg}")
        if not (MIN_DATE_IN_DATA <= self.uc_period_end <= MAX_DATE_IN_DATA):
            errors_list.append(f"UC period end {self.uc_period_end.strftime(DATE_FORMAT)} not in allowed period {allowed_period_msg}")

        # stop if any error
        if len(errors_list) > 0:
            uncoherent_param_stop(param_errors=errors_list)
        else:
            print("Modified long-term UC parameters are coherent")