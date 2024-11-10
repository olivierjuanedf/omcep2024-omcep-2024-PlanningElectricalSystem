"""
Read JSON parametrization files... and check coherence of them
"""
from utils.read import read_and_check_uc_run_params

eraa_data_descr, uc_run_params = read_and_check_uc_run_params()

"""
Get needed data (demand, RES Capa. Factors, installed generation capacities)
"""
from utils.eraa_data_reader import get_countries_data
from utils.basic_utils import get_period_str


uc_period_msg = get_period_str(period_start=uc_run_params.uc_period_start, 
                               period_end=uc_run_params.uc_period_end)

print(f"Read needed ERAA ({eraa_data_descr.eraa_edition}) data for period {uc_period_msg}")
demand, agg_cf_data, agg_gen_capa_data, interco_capas = \
  get_countries_data(uc_run_params=uc_run_params,
                     agg_prod_types_with_cf_data=eraa_data_descr.agg_prod_types_with_cf_data,
                     aggreg_prod_types_def=eraa_data_descr.aggreg_prod_types_def
                     )

from include.dataset_builder import get_generation_units_data, control_min_pypsa_params_per_gen_units
print("Get generation units data, from both ERAA data - read just before - and JSON parameter file")
generation_units_data = \
  get_generation_units_data(pypsa_unit_params_per_agg_pt=eraa_data_descr.pypsa_unit_params_per_agg_pt,
                            units_complem_params_per_agg_pt=eraa_data_descr.units_complem_params_per_agg_pt, 
                            agg_res_cf_data=agg_cf_data, agg_gen_capa_data=agg_gen_capa_data)
print("Check that 'minimal' PyPSA parameters for unit creation have been provided (in JSON files)/read (from ERAA data)")
from utils.read import read_and_check_pypsa_static_params
pypsa_static_params = read_and_check_pypsa_static_params()
control_min_pypsa_params_per_gen_units(generation_units_data=generation_units_data,
                                       pypsa_min_unit_params_per_agg_pt=pypsa_static_params.min_unit_params_per_agg_pt)

# create PyPSA network
from include.dataset_builder import init_pypsa_network, add_gps_coordinates, add_energy_carrier, \
  add_generators, add_loads, add_interco_links, save_lp_model, get_stationary_batt_opt_dec
network = init_pypsa_network(df_demand_first_country=demand[uc_run_params.selected_countries[0]])
# add GPS coordinates
selec_countries_gps_coords = \
  {country: gps_coords for country, gps_coords in eraa_data_descr.gps_coordinates.items() 
   if country in uc_run_params.selected_countries}
network = add_gps_coordinates(network=network, countries_gps_coords=selec_countries_gps_coords)
from fuel_sources import FUEL_SOURCES
network = add_energy_carrier(network=network, fuel_sources=FUEL_SOURCES)
network = add_generators(network=network, generators_data=generation_units_data)
network = add_loads(network=network, demand=demand)
network = add_interco_links(network, countries=uc_run_params.selected_countries, 
                            interco_capas=interco_capas)
print("PyPSA network main properties:", network)
network.plot(title="My little elec. Europe network", color_geomap=True, jitter=0.3)
print("Optimize 'network' - i.e. solve associated UC problem")
result = network.optimize(solver_name="highs")
print(result)
save_lp_model(network, year=uc_run_params.selected_target_year, 
              n_countries=len(uc_run_params.selected_countries), 
              period_start=uc_run_params.uc_period_start)
print("THE END of European PyPSA-ERAA UC simulation... missing some interesting parts... to come at OMCEP2025?")
