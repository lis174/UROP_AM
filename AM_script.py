from netCDF4 import Dataset
import cartopy
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import xarray as xr
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import integrate
import scipy

# add mpi
from mpi4py import MPI

comm = MPI.COMM_WORLD # communicator for process
rank = comm.Get_rank() # rank for process



def calculate_action_measure_list(daily_NT, p):
    action_measure_list = [0,0]
    included_days = []

    for i in range(2, len(daily_NT.values)):
        if i in included_days:
            continue
        else:
            temperature_day = daily_NT.values[i]
            if temperature_day > p:
                # find duration of event
                j = i - 2
                duration_count = 0
                while daily_NT.values[j] > p:
                    j += 1
                    duration_count += 1
                # if event lasts for 3 days or more, we'll find the action measure
                if duration_count  >= 3:
                    # slice data and calculate how much it exceeds threshold
                    exceedances = [k - p for k in daily_NT.data[(i-2):(i+duration_count-2)]]
                    # find action measure by integration
                    actionmeasure = scipy.integrate.trapezoid(exceedances, x=None, dx=1.0, axis=- 1)
                    included_days.extend(list(range(i, i+duration_count-2)))
                    # include all days
                    action_measure_list[-2:] = [actionmeasure]*2
                    action_measure_list.extend([actionmeasure for i in range(duration_count-2)])
                else: 
                    action_measure_list.append(0)
            else: 
                action_measure_list.append(0)
    return action_measure_list



def calculate_action_measures_grid(filename, extent):
    # break temperature data up in grids
    number_lat = np.shape(filename["tas"]["lat"])[0]
    number_lon = np.shape(filename["tas"]["lon"])[0]
    
    save_grid_points = []
    for grid_lat in range(number_lat):
        latitude = filename["tas"]["lat"].values[grid_lat]
        for grid_lon in range(number_lon):
            longitude = filename["tas"]["lon"].values[grid_lon]
            one_point = filename["tas"].sel(lat=latitude,
                                                lon=longitude)
            save_grid_points.append([[longitude, latitude], one_point])

    # decompose save_grid_points
    action_measure_dataset = []
    for datafile in save_grid_points:
        decomposition = seasonal_decompose(datafile[1], model='additive', period=3650)
        trend = decomposition.trend

        daily_temp_nt = datafile[1].values - trend
        daily_NT = datafile[1].copy()
        daily_NT.data = daily_temp_nt
        p = np.nanpercentile(daily_NT, 90)
        
        # calculate action measure in datalist
        action_measure_list = calculate_action_measure_list(daily_NT, p)

        coords = {'time': (np.array(datafile[1]['time'].data))
         }

        # define global attributes
        attrs = {'author':'Lisanne Blok'}

        # create dataset
        action_measure_array = xr.DataArray(action_measure_list,
                                            dims = ['time'],
                                coords=coords, 
                                attrs=attrs)

        lon_list = (np.array(datafile[1]['lon'].data))
        lat_list = (np.array((datafile[1]['lat'].data)))
        
        action_measure_array["lon"] = lon_list
        action_measure_array["lat"] = lat_list
        
        action_measure_array = action_measure_array.expand_dims("lat")
        action_measure_array = action_measure_array.expand_dims("lon")
        
        action_measure_array = action_measure_array.transpose("time", "lon", "lat")
        
        action_measure_dataset.append(action_measure_array)
        
    am_daily = xr.combine_by_coords(action_measure_dataset)
    am_daily = am_daily.to_dataset(name = "actionmeasure")
    
  #  plot_spatial_figures(am_daily, extent)
    
    return am_daily


bang_extent = [86, 95, 20, 27]
asia_extent = [70, 115, 8, 30]


had_HM_hist = xr.open_dataset('hadm_HM_hist.nc')
had_HM_fut = xr.open_dataset('hadm_HM_fut.nc')


AM_HM_had_hist = calculate_action_measures_grid(had_HM_hist, bang_extent)
new_filename_1 = 'amW_hist_HM_HADM3.nc'
AM_HM_had_hist.to_netcdf(path=new_filename_1)


AM_HM_had_fut = calculate_action_measures_grid(had_HM_fut, bang_extent)
new_filename_1 = 'amW_fut_HM_HADM3.nc'
AM_HM_had_fut.to_netcdf(path=new_filename_1)
