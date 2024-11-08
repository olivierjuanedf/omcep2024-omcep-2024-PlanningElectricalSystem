import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union


DATE_FORMAT = "%Y/%m/%d"
N_DAYS_UC_DEFAULT = 9


def uncoherent_param_stop(param_errors: List[str]):
    error_msg = "There are error(s) in JSON params to be modif. file:"
    for elt_error in param_errors:
        error_msg += f"\n- {elt_error}"
    error_msg += "\n-> STOP"
    sys.exit(1)


@dataclass
class UCRunParams:
    selected_climatic_year: int
    selected_countries: List[str]
    selected_target_year: int
    selected_agg_prod_types: Dict[str, Optional[List[str]]]
    uc_period_start: Union[str, datetime]
    uc_period_end: Union[str, datetime] = None

    def process(self):
        # if dates in str format, cast them as datetime 
        # - setting end of period to default value if not provided
        if isinstance(self.uc_period_start, str):
            self.uc_period_end = datetime.strptime(self.uc_period_start, DATE_FORMAT)
        if self.uc_period_end is None:
            self.uc_period_end = self.uc_period_start + timedelta(days=N_DAYS_UC_DEFAULT)
            print(f"End of period set to default value: {self.uc_period_end:%Y/%m/%d} (period of {N_DAYS_UC_DEFAULT} days)")
        elif isinstance(self.uc_period_end, str):
            self.uc_period_end = datetime.strptime(self.uc_period_end, DATE_FORMAT)
        # TODO: replace None and missing countries in dict of values by {country: []}
    
    def coherence_check(self):
        print("To be coded")
        errors_list = []
        # check that there is no repetition of countries
        if len(set(self.selected_countries)) < len(self.selected_countries):
            errors_list.append("Repeated countries") 

        # check coherence of values with fixed params
                
        # stop if any error
        if len(errors_list) > 0:
            uncoherent_param_stop(param_errors=errors_list)
