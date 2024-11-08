# Tutorial - Long-Term Unit Commitment part

## Appendices

### Input data description

**Preliminary remarks**: (i) JSON files used to store dict-like infos. (ii) "null" is used for None in these JSON files

The ones in folder *input\long_term_uc*; **file by file description**:
- *elec-europe_params_fixed.json*: containing parameters... **not to be modified during this practical class**. 
    - "aggreg_prod_types_def": **correspondence between "aggregate" production type (the ones that will be used in this class) and the ones - more detailed - in ERAA data**. It will be used in the data reading phase; to simplify (diminish size!) of the used data in this UC exercise
    - "available_climatic_years", "available countries", "available_target_years" (or simply years; "target year" is the used terminology in ERAA): **available values for the dimensions of provided extract of ERAA data**
    - "gps_coordinates": the ones of the capitals excepting meta-countries with coordinates of Rotterdam for "benelux", Madrid for "iberian-peninsula", and Stockholm for "scandinavia". N.B. Only for plotting - very schematic - representation of the "network" associated to your UC model
    - "eraa_edition": edition of ERAA data used - 2023.2 (one/two ERAA editions per year from 2021)

- *elec-europe_params_to-be-modif.json*: containing parameters... **you can play with during this practical class**
    - "selected_climatic_year": to **choose climatic year" considered for UC model (unique deterministic scenario)
    - "selected_countries": to **choose countries** that you would like to be part of your European - copper-plate - long-term UC model. N.B. Following yesterday's toy model test, only Italy is completed at first
    - "selected_agg_prod_types": **per country selection of the (generation unit) aggregate production types** to be part of your model. N.B. Using aggregate production types, i.e. the ones of field "available_aggreg_prod_types" in file *elec-europe_params_fixed.json*
    - "uc_period_start": **date from which UC optimization period starts; under format "1900/%M/%d"**. Ex.: "1900/1/1" to start from beginning of the year. N.B. "1900" to clearly indicate that a "fictive calendar" (modelling one) be used in ERAA data, with 364 days (to get 52 full weeks... an important granularity for some unit optim., as discussed in class)
    - (optional) "uc_period_end": idem, **end of period; same format**. Default value: period of 9 days starting from "uc_period_start". 

