# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:55:52 2020

@author: Andrea Mangipinto
"""
#%% Support functions for the charging process 
   
import numpy as np
import pandas as pd
import pkg_resources
import pytz

#%% Functions

def get_csv_data(country_equivalent):
    # %% Files with the inputs to be loaded
    inputfolder = r"database/"

    # Composition of the population by percentage share
    stream = pkg_resources.resource_stream(__name__, inputfolder + "pop_share.csv")
    pop_data = pd.read_csv(stream, header=0, index_col=0)

    # Share of the type of vehicles in the country
    stream = pkg_resources.resource_stream(__name__, inputfolder + "vehicle_share.csv")
    vehicle_data = pd.read_csv(stream, header=0, index_col=0)

    # Total daily distance [km]
    stream = pkg_resources.resource_stream(__name__, inputfolder + "d_tot.csv")
    d_tot_data = pd.read_csv(stream, header=0, index_col=0)

    # Distance by trip [km]
    stream = pkg_resources.resource_stream(__name__, inputfolder + "d_min.csv")
    d_min_data = pd.read_csv(stream, header=0, index_col=[0, 1])

    # Functioning time by trip [min]
    stream = pkg_resources.resource_stream(__name__, inputfolder + "t_func.csv")
    t_func_data = pd.read_csv(stream, header=0, index_col=[0, 1])

    # Functioning windows
    stream = pkg_resources.resource_stream(__name__, inputfolder + "windows.csv")
    window_data = pd.read_csv(stream, header=[0, 1], index_col=[0, 1, 2])
    window_data = window_data * 60
    window_data = window_data.astype(int)

    # Trips distribution by time
    trips = {}
    for day in ['weekday', 'saturday', 'sunday']:
        file = inputfolder + f"trips_by_time_{day}.csv"
        stream = pkg_resources.resource_stream(__name__, file)
        trips[day] = pd.read_csv(stream, header=0)
        trips[day] = trips[day][country_equivalent] / 100

    return pop_data, vehicle_data, d_tot_data, d_min_data, t_func_data, window_data, trips


def charge_prob(SOC):
    
    k = 15
    per_SOC = 0.5
    
    p = 1-1/(1+np.exp(-k*(SOC-per_SOC)))
       
    return p

def charge_prob_const(SOC):        
    
    p = 1       
    
    return p

def SOC_initial_f(SOC_max, SOC_min, SOC_initial):
    
    SOC_i = np.random.rand()*(SOC_max-SOC_min) + SOC_min
    
    return SOC_i

def SOC_initial_f_const(SOC_max, SOC_min, SOC_initial):
    
    SOC_i = SOC_initial
        
    return SOC_i

def charge_check_smart(ind_park_range, charge_range):
    
    b = np.isin(ind_park_range, charge_range, assume_unique = True).any()

    return b

def charge_check_normal(ind_park_range, charge_range):
    
    b = True

    return b

def pv_indexing(minutes, country, year, inputfile_pv = r"database\ninja_pv_europe_v1.1_merra2.csv"):
      
    pv_af = pd.read_csv(inputfile_pv, index_col = 0) #Read the input file
    pv_af = pd.DataFrame(pv_af[country]) #Filter only for needed country
    ind_init = pd.date_range(start=pv_af.index[0], end=pv_af.index[-1], freq='H', tz = 'UTC')
    pv_af.set_index(ind_init, inplace = True) #Set index to datetime
    pv_af_tz = pv_af.tz_convert(pytz.country_timezones[country][0]) # Convert to country timezone
    
    pv_af_loc = pv_af_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    pv_af_loc = pv_af_loc[~pv_af_loc.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    pv_af_loc = pv_af_loc.loc[str(year)]
    pv_non_zero_mean = pv_af_loc[pv_af_loc != 0].mean().values #calculate mean of non zero values

    pv_af_tz_high = pv_af_loc[pv_af_loc > pv_non_zero_mean].fillna(0) # filter values higher than the mean
    
    pv_af = pv_af_tz_high.resample('T', closed='right').pad() #resample with minute time detail
    pv_af = pv_af.loc[minutes[0]:  minutes[-1]] #filter for the simulated period
    
    pv_ind = np.nonzero(pv_af.values)[0] #extract indexes 
        
    return pv_ind

def residual_load(minutes, residual_load, year, country):
    
    if country == 'EL':
        country_tz = 'GR'
    elif country == 'UK':
        country_tz = 'GB'
    else:
        country_tz = country

    residual_load_temp = pd.DataFrame(residual_load.values)
    
    ind_init = pd.date_range(start= f'{year}-01-01', end=f'{year}-12-31 23:00', freq='T', tz = 'UTC')
    residual_load_temp.set_index(ind_init, inplace = True)
    
    residual_load_temp_tz = residual_load_temp.tz_convert(pytz.country_timezones[country_tz][0])
    
    residual_load_temp = residual_load_temp_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    residual_load_temp = residual_load_temp[~residual_load_temp.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    residual_load_temp = residual_load_temp.loc[minutes[0]: minutes[-1]] #filter for the simulated period

    res_load_neg = residual_load_temp[residual_load_temp < 0].fillna(0)
            
    res_load_neg_ind = np.nonzero(res_load_neg.values)[0]
    
    return res_load_neg_ind
    
def tot_users_calc(User_list):
    # Calculation of the total number of users
    num_users = {}
    for i in range(len(User_list)):
        num_users[User_list[i].user_name] = User_list[i].num_users
        tot_users = sum(num_users.values())
    
    return tot_users

def tot_battery_cap_calc(User_list):
    # Calculation of the total fleet battery capacity
    cap_users = {}
    for Us in User_list:
        cap_users[Us.user_name] = Us.num_users *  Us.App_list[0].Battery_cap
        tot_cap_users = sum(cap_users.values())
    
    return tot_cap_users