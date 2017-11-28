from windpowerlib import wind_turbine as wt
from windpowerlib import wind_farm as wf
import visualization_tools
import analysis_tools
import tools
import os
import pandas as pd
import numpy as np
import feedin_time_series

# Get all turbine types of windpowerlib
#turbines = wt.get_turbine_types(print_out=False)
#visualization_tools.print_whole_dataframe(turbines)

# ----------------------------- Set parameters ------------------------------ #
pickle_load_weather = True
pickle_load_arge = True
weather_data_name = 'MERRA'  # 'MERRA' or 'open_FRED'
validation_data_name = 'ArgeNetz'  # 'ArgeNetz' or ... # TODO
year = 2016


# Select time of day you want to observe or None for all day
time_period = (
#        12, 15  # time of day to be selected (from h to h)
        None   # complete time series will be observed
        ) 

output_methods = [
    'hourly_energy_output',
    'monthly_energy_output',
    'power_output'
    ]
visualization_methods = [
    'box_plots',
    'feedin_comparison',
    'plot_correlation'  # Attention: this takes a long time for high resolution
    ]

# Start and end date for time period to be plotted
# Attention: only for 'feedin_comparison' and not for monthly output
#start = '{0}-10-01 11:00:00+00:00'.format(year)
#end = '{0}-10-01 16:00:00+00:00'.format(year)
#start = '{0}-10-01'.format(year)
#end = '{0}-10-03'.format(year)
start = None
end = None

plot_arge_feedin = False  # If True all ArgeNetz data is plotted
plot_wind_farms = False  # If True usage of plot_or_print_farm()
plot_wind_turbines = False  # If True usage of plot_or_print_turbine()

latex_output = False  # If True Latex tables will be created

# Specify folder and title add on for saving the plots
if time_period is not None:
    save_folder = '../Plots/{0}/{1}/CertainTimeOfDay/{2}_{3}/'.format(
                    year, weather_data_name + '_' + validation_data_name,
                    time_period[0], time_period[1])
    title_add_on = ' time of day: {0}:00 - {1}:00'.format(
        time_period[0], time_period[1])
else:
    save_folder = '../Plots/{0}/{1}/'.format(
                    year, weather_data_name + '_' + validation_data_name)
    title_add_on = ''

# --------------------- Turbine data and initialization --------------------- #
# TODO: scale power curves??
# Turbine data
enerconE70 = {
    'turbine_name': 'ENERCON E 70 2300',  # NOTE: Peak power should be 2.37 MW - is 2,31 for turbine in windpowerlib
    'hub_height': 64,  # in m
    'rotor_diameter': 71  # in m    source: www.wind-turbine-models.com
}
enerconE66 = {
    'turbine_name': 'ENERCON E 66 1800',  # NOTE: Peak power should be 1.86 MW - ist 1,8 for turbine in windpowerlib
    'hub_height': 65,  # in m
    'rotor_diameter': 70  # in m    source: www.wind-turbine-models.com
}

# Initialize WindTurbine objects
# TODO: Put if statments in case of other turbines in other validation data
# TODO: idea for less lines: use second file for turbine and wind farm data
e70 = wt.WindTurbine(**enerconE70)
e66 = wt.WindTurbine(**enerconE66)
if plot_wind_turbines:
    visualization_tools.plot_or_print_turbine(e70)
    visualization_tools.plot_or_print_turbine(e66)

# ----------------------------- Wind farm data ------------------------------ #
# Bredstedt (54.578219, 8.978092)
bredstedt = {
    'wind_farm_name': 'Bredstedt',
    'wind_turbine_fleet': [{'wind_turbine': e70,
                            'number_of_turbines': 16}],
    'coordinates': [54.5, 8.75]
}
# Nordstrand (54.509708, 8.9007)
nordstrand = {
    'wind_farm_name': 'Nordstrand',
    'wind_turbine_fleet': [{'wind_turbine': e70,
                            'number_of_turbines': 6}],
    'coordinates': [54.5, 8.75]
}
# PPC_4919 (54.629167, 9.0625)
PPC_4919 = {
    'wind_farm_name': 'PPC_4919',
    'wind_turbine_fleet': [{'wind_turbine': e70,
                            'number_of_turbines': 13},
                           {'wind_turbine': e66,
                            'number_of_turbines': 4}],
    'coordinates': [55, 8.75]  # NOTE: lon exactly in between two coordinates
}
# PPC_4950 (54.629608, 9.029239)
PPC_4950 = {
    'wind_farm_name': 'PPC_4950',
    'wind_turbine_fleet': [{'wind_turbine': e70,
                            'number_of_turbines': 22}],
    'coordinates': [54.5, 8.75]
}
# PPC_5598 (54.596603, 8.968139)
PPC_5598 = {
    'wind_farm_name': 'PPC_5598',
    'wind_turbine_fleet': [{'wind_turbine': e70,
                            'number_of_turbines': 14}],
    'coordinates': [54.5, 8.75]
}


# -------------------------- Validation Feedin Data ------------------------- #
if validation_data_name == 'ArgeNetz':
    if year == 2015:
        wind_farm_data = [bredstedt, nordstrand, PPC_4919, PPC_4950, PPC_5598]
        temporal_resolution_validation = 5  # minutes # TODO: rename!!!!!
        # Create indices for DataFrame in standardized form
        indices = tools.get_indices_for_series(
            temporal_resolution_validation, start='5/1/2015', end='1/1/2016')
    if (year == 2016 or year == 2017):
        wind_farm_data = [bredstedt, PPC_4919, PPC_4950, PPC_5598]
        temporal_resolution_validation = 1  # minutes
        # Create indices for DataFrame in standardized form
        indices = tools.get_indices_for_series(temporal_resolution_validation,
                                               year=year)
    # Get ArgeNetz Data
    validation_data = feedin_time_series.get_and_plot_feedin(
        year, pickle_load=pickle_load_arge, plot=plot_arge_feedin)
if validation_data_name == '...':
    pass  # Add more data


# Initialise validation wind farms with power output and annual energy output
validation_farms = []
for description in wind_farm_data:
    # Initialise wind farm
    wind_farm = wf.WindFarm(**description)
    # Power output in MW with standard indices
    wind_farm.power_output = pd.Series(
        data=(validation_data[description['wind_farm_name'] +
                              '_P_W'].values / 1000),
        index=indices)
    # Convert indices to datetime UTC
    wind_farm.power_output.index = pd.to_datetime(indices).tz_convert('UTC')
    # Annual energy output in MWh
    wind_farm.annual_energy_output = tools.annual_energy_output(
        wind_farm.power_output, temporal_resolution_validation)
    validation_farms.append(wind_farm)

#if plot_arge_feedin:
#    # y_limit = [0, 60]
#    y_limit = None
#    visualization_tools.plot_or_print_farm(
#        validation_farms, save_folder='ArgeNetz_power_output/Plots_{0}'.format(year),
#        y_limit=y_limit)

# ------------------------- Power output simulation ------------------------- #
# TODO: new section: weather (for different weather sources)
# TODO: actually only for more complex caluclations like this.. for simple calculations
#       modelchain can be used (if temperature is not beeing used)
# TODO: weather for all the ArgeNetz wind farms identical - if change: save
#first for eventual other time series

if weather_data_name == 'MERRA':
    temporal_resolution_weather = 60
    filename_weather = os.path.join(os.path.dirname(__file__),
                                    'dumps/weather',
                                    'weather_df_merra_{0}.p'.format(year))
    # Create data frame from csv if pickle_load_weather == False
    if pickle_load_weather:
            data_frame = None
    else:
        print('Read MERRA data from csv...')
        data_frame = pd.read_csv(os.path.join(
            os.path.dirname(__file__), 'data/Merra',
            'weather_data_GER_{0}.csv'.format(year)),
            sep=',', decimal='.', index_col=0)
    # Visualize latitudes and longitudes of DataFrame
#    lat, lon = visualization_tools.return_lats_lons(data_frame)
#    print(lat, lon)

simulation_farms = []
for description in wind_farm_data:
    # Initialise wind farm
    wind_farm = wf.WindFarm(**description)
    # Get weather
    weather = tools.get_weather_data(pickle_load_weather, filename_weather,
                                     weather_data_name, year,
                                     wind_farm.coordinates, data_frame)
    if (validation_data_name == 'ArgeNetz' and year == 2015):
        weather = weather.loc[weather.index >= '2015-05-01']
    if weather_data_name == 'MERRA':
        data_height = {'wind_speed': 50,  # Source: https://data.open-power-system-data.org/weather_data/2017-07-05/
                       'roughness_length': 0,  # TODO: is this specified?
                       'temperature': weather.temperature_height,
                       'density': 0,
                       'pressure': 0}
    if weather_data_name == 'open_FRED':
        pass  # TODO: data_height = ...
    # Power output in MW
    wind_farm.power_output = tools.power_output_sum(
        wind_farm.wind_turbine_fleet, weather, data_height) / (1*10**6)
    # Convert indices to datetime UTC
    wind_farm.power_output.index = pd.to_datetime(
        wind_farm.power_output.index).tz_convert('UTC')
    # Annual energy output in MWh
    wind_farm.annual_energy_output = tools.annual_energy_output(
        wind_farm.power_output, temporal_resolution_weather)
    simulation_farms.append(wind_farm)

if plot_wind_farms:
    y_limit = [0, 60]
    visualization_tools.plot_or_print_farm(
        simulation_farms, save_folder='Merra_power_output/{0}'.format(year),
        y_limit=y_limit)

# ------------------------------ Data Evaluation ---------------------------- #
validation_sets = []
if 'hourly_energy_output' in output_methods:
    # ValidationObjects!!!!!
    val_set_hourly_energy = analysis_tools.evaluate_feedin_time_series(
        validation_farms, simulation_farms, temporal_resolution_validation,
        temporal_resolution_weather, 'hourly_energy_output',
        validation_data_name, weather_data_name, time_period, 'H')
    validation_sets.append(val_set_hourly_energy)

if 'monthly_energy_output' in output_methods:
    val_set_monthly_energy = analysis_tools.evaluate_feedin_time_series(
        validation_farms, simulation_farms, temporal_resolution_validation,
        temporal_resolution_weather, 'monthly_energy_output',
        validation_data_name, weather_data_name, time_period, 'M')
    validation_sets.append(val_set_monthly_energy)

if 'power_output' in output_methods:
    for farm in simulation_farms:
        farm.power_output = tools.power_output_fill(
            farm.power_output, temporal_resolution_validation, year)
    val_set_power = analysis_tools.evaluate_feedin_time_series(
        validation_farms, simulation_farms, temporal_resolution_validation,
        temporal_resolution_weather, 'power_output',
        validation_data_name, weather_data_name, time_period)
    validation_sets.append(val_set_power)

# Visualization of data evaluation
for validation_set in validation_sets:
    if 'box_plots' in visualization_methods:
        # All bias time series of a validation set in one DataFrame for Boxplot
        bias_df = pd.DataFrame()
        for validation_object in validation_set:
            if 'all' not in validation_object.object_name:
                df_part = pd.DataFrame(data=validation_object.bias,
                                       columns=[validation_object.object_name])
                bias_df = pd.concat([bias_df, df_part], axis=1)
        # Specify filename
        filename = save_folder + '{0}_Boxplot_{1}_{2}_{3}.pdf'.format(
                validation_set[0].output_method, year,
                validation_data_name, weather_data_name)
        visualization_tools.box_plots_bias(
            bias_df, filename=filename,
            title='Deviation of {0} {1} from {2}\n in {3}'.format(
                weather_data_name,
                validation_set[0].output_method.replace('_', ' '),
                validation_data_name, year) + title_add_on)

    if 'feedin_comparison' in visualization_methods:
    # TODO: rename this method for better understanding
#        if year == 2015 and validation_data_name == 'ArgeNetz':
#            tick_label=['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#        else:
#            tick_label=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
#                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for validation_object in validation_set:
            filename = save_folder + '{0}_{1}_Feedin_{2}_{3}_{4}.pdf'.format(
                validation_set[0].output_method,
                validation_object.object_name, year,
                validation_data_name, weather_data_name)
            visualization_tools.plot_feedin_comparison(
                validation_object, filename=filename,
                title='{0} of {1} and {2} of {3}\n {4}'.format(
                    validation_set[0].output_method.replace('_', ' '),
                    weather_data_name, validation_data_name,
                    validation_object.object_name, year) + title_add_on,
                start=start, end=end)
#                    , tick_label=tick_label)

    if 'plot_correlation' in visualization_methods:
        for validation_object in validation_set:
            filename = (save_folder +
                        '{0}_{1}_Correlation_{2}_{3}_{4}.pdf'.format(
                                validation_set[0].output_method,
                                validation_object.object_name, year,
                                validation_data_name, weather_data_name))
            visualization_tools.plot_correlation(
                    validation_object, filename=filename,
                    title='{0} of {1} and {2} of {3}\n {4}'.format(
                        validation_set[0].output_method.replace('_', ' '),
                        weather_data_name, validation_data_name,
                        validation_object.object_name, year) + title_add_on)

# ---------------------------------- LaTeX Output --------------------------- #
if latex_output:
    all_farm_lists = [validation_farms, simulation_farms]
    column_names = ['ArgeNetz', 'MERRA']  # evtl als if abfrage in funktion
    df = pd.DataFrame()
    i = 0
    for farm_list in all_farm_lists:
        index = [farm.wind_farm_name for farm in farm_list]
        # Annual energy output in GWh
        data = [round(farm.annual_energy_output, 3)
                for farm in farm_list]
        df_temp = pd.DataFrame(data=data, index=index,
                               columns=[[column_names[i]],
                                        ['Energy Output [MWh]']])
        df = pd.concat([df, df_temp], axis=1)
        if i != 0:
            data = [round((farm_list[j].annual_energy_output -
                          all_farm_lists[0][j].annual_energy_output) /
                          all_farm_lists[0][j].annual_energy_output * 100, 3)
                    for j in range(len(validation_farms))]
            df_temp = pd.DataFrame(
                data=data, index=index,
                columns=[[column_names[i]], ['Deviation [%]']])
            df = pd.concat([df, df_temp], axis=1)
        i += 1

    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     '../../../tubCloud/Latex/Tables/')
    name = os.path.join(path_latex_tables, 'name_of_table.tex')
    # TODO: make fully customized table
    df.to_latex(buf=name)

print('# ----------- Done ----------- #')