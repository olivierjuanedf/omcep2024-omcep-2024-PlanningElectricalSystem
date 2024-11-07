import pandas as pd
import numpy  as np


def read_capacity_data(v2g : bool, file_path : str) :
    '''
    
    return :    ev_number : total nb of EV plugged during the charge
                battery_capacity : battery capacity of each EV (kWh)
    '''

    data_capacity = pd.read_csv(file_path, sep=';',encoding='utf-8') 
    ev_number = data_capacity[data_capacity['v2g_capable']==v2g]['ev_number'].iloc[0]
    battery_capacity  = int(data_capacity[data_capacity['v2g_capable']==v2g]['battery_capacity_e'].iloc[0])/ev_number

    return ev_number, battery_capacity


def read_signal(v2g : bool, file_path : str) -> pd.DataFrame:
    '''
    return : signal : a DataFrame made of a first columns "time" with datetime.datetime and second columns "power" with float 
    '''

    name = 'fra_v1g'
    if v2g:
        name = 'fra_v2g'
    data_signal  = pd.read_csv(file_path, sep=';',encoding='utf-8') 
    data_signal =  data_signal[data_signal['aggregate_ev']==name]
    data_signal = data_signal.drop(['aggregate_ev'], axis = 1)
    data_signal['date'] = pd.to_datetime(data_signal['date'], dayfirst=True)
    data_signal = data_signal.rename(columns={"date":"time","consumption_p":"power"})

    return data_signal
