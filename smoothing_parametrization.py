# Imports from Windpowerlib
from windpowerlib.wind_turbine import WindTurbine
from windpowerlib.wind_farm import WindFarm
from windpowerlib import tools
from windpowerlib.power_curves import smooth_power_curve

# Imports from lib_validation
from wind_farm_specifications import (get_joined_wind_farm_data,
                                      initialize_turbines)
import tools as lib_tools

# Other imports
from matplotlib import pyplot as plt
import os
import pandas as pd
import numpy as np
import pickle


def plot_smoothed_pcs(standard_deviation_method, block_width,
                      wind_speeds_block_range, turbines, grouped=False,
                      mean_roughness_length=None):
    for turbine in turbines:
        if standard_deviation_method == 'turbulence_intensity':
            turbulence_intensity = tools.estimate_turbulence_intensity(
                turbine.hub_height, mean_roughness_length)
        else:
            turbulence_intensity = None
        # Start figure with original power curve
        fig = plt.figure()
        a, = plt.plot(turbine.power_curve['wind_speed'],
                      turbine.power_curve['power'] / 1000, label='original')
        # Get smoothed power curve
        if grouped == False:
            smoothed_power_curve = smooth_power_curve(
                turbine.power_curve.wind_speed, turbine.power_curve['power'],
                block_width=block_width,
                standard_deviation_method=standard_deviation_method,
                turbulence_intensity=turbulence_intensity,
                wind_speeds_block_range=wind_speeds_block_range)
            b, = plt.plot(smoothed_power_curve['wind_speed'],
                          smoothed_power_curve['power'] / 1000,
                          label='smoothed')
            handles = [a, b]
        if grouped == 'wind_speed_range':
            handles = [a]
            for range in wind_speeds_block_range:
                smoothed_power_curve = smooth_power_curve(
                    turbine.power_curve.wind_speed, turbine.power_curve['power'],
                    block_width=block_width,
                    standard_deviation_method=standard_deviation_method,
                    turbulence_intensity=turbulence_intensity,
                    wind_speeds_block_range=range)
                handle, = plt.plot(smoothed_power_curve['wind_speed'],
                              smoothed_power_curve['power'] / 1000,
                              label='range {}'.format(range))
                handles.append(handle)
        if grouped == 'block_width':
            handles = [a]
            for width in block_width:
                smoothed_power_curve = smooth_power_curve(
                    turbine.power_curve.wind_speed,
                    turbine.power_curve['power'],
                    block_width=width,
                    standard_deviation_method=standard_deviation_method,
                    turbulence_intensity=turbulence_intensity,
                    wind_speeds_block_range=wind_speeds_block_range)
                handle, = plt.plot(smoothed_power_curve['wind_speed'],
                                   smoothed_power_curve['power'] / 1000,
                                   label='block width {}'.format(width))
                handles.append(handle)
        if grouped == 'std_dev':
            handles = [a]
            for std_dev_method in standard_deviation_method:
                if std_dev_method == 'turbulence_intensity':
                    turbulence_intensity = tools.estimate_turbulence_intensity(
                        turbine.hub_height, mean_roughness_length)
                else:
                    turbulence_intensity = None
                smoothed_power_curve = smooth_power_curve(
                    turbine.power_curve.wind_speed,
                    turbine.power_curve['power'],
                    block_width=block_width,
                    standard_deviation_method=std_dev_method,
                    turbulence_intensity=turbulence_intensity,
                    wind_speeds_block_range=wind_speeds_block_range)
                handle, = plt.plot(smoothed_power_curve['wind_speed'],
                                   smoothed_power_curve['power'] / 1000,
                                   label=std_dev_method.replace(
                                       'turbulence_intensity', 'TI'))
                handles.append(handle)
        plt.ylabel('Power in kW')
        plt.xlabel('Wind speed in m/s')
        plt.title(turbine.object_name)
        plt.legend(handles=handles)
        fig.savefig(os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../../../User-Shares/Masterarbeit/Latex/inc/images/power_curves/smoothed_pc',
            '{}_{}_{}_{}_blockwidth{}_range{}.pdf'.format(
                'single' if grouped == False else grouped, turbine.object_name,
                weather_data_name, standard_deviation_method,
                block_width, wind_speeds_block_range))))
        plt.close()


def get_roughness_length(weather_data_name, coordinates):
    z0 = pd.DataFrame()
    for year in [2015, 2016]:
        filename_weather = os.path.join(
            os.path.dirname(__file__), 'dumps/weather',
            'weather_df_{0}_{1}.p'.format(weather_data_name, year))
        # Get weather data
        temperature_heights = [60, 64, 65, 105, 114]
        weather = lib_tools.get_weather_data(
            weather_data_name, coordinates, pickle_load=True,
            filename=filename_weather, year=year,
            temperature_heights=temperature_heights)
        z0 = pd.concat([z0, weather['roughness_length']], axis=0)
    return z0.mean()


if __name__ == "__main__":
    single_plots = False
    grouped_plots = True
    standard_deviaton_methods = ['turbulence_intensity', 'Staffell']
    block_widths = [0.1, 0.5, 1.0]
    wind_speeds_block_ranges = [5.0, 10.0, 15.0, 20.0]
    weather_data_names = ['MERRA', 'open_FRED']
    # Initialise WindTurbine objects
    e70, v90, v80, ge, e82 = initialize_turbines(
        ['enerconE70', 'vestasV90', 'vestasV80', 'ge_1500',
         # 'enerconE66_1800_65', # Note: war nur für wf_3
         'enerconE82_2000'])
    # Get wind farm data
    filenames = ['farm_specification_argenetz_2015.p',
                 'farm_specification_argenetz_2016.p',
                 'farm_specification_enertrag_2016.p',
                 'farm_specification_greenwind_2015.p',
                 'farm_specification_greenwind_2016.p']
    wind_farm_pickle_folder = os.path.join(os.path.dirname(__file__),
                                           'dumps/wind_farm_data')
    wind_farm_data = get_joined_wind_farm_data(
        filenames, wind_farm_pickle_folder, pickle_load=True)
    for weather_data_name in weather_data_names:
        for wf_data in wind_farm_data:
            z0 = get_roughness_length(weather_data_name,
                                      wf_data['coordinates'])[0]
            if (wf_data['object_name'] == 'wf_BE' or
                    wf_data['object_name'] == 'wf_BS'):
                turbines = [v90]
            elif wf_data['object_name'] == 'wf_BE':
                turbines = [v80]
            elif wf_data['object_name'] == 'wf_BNE':
                turbines = [ge, e82]
            elif wf_data['object_name'] == 'wf_SH':
                turbines = [e70]
            if single_plots:
                for std_dev_method in standard_deviaton_methods:
                    for block_width in block_widths:
                        for wind_speeds_block_range in wind_speeds_block_ranges:
                            plot_smoothed_pcs(
                                standard_deviation_method=std_dev_method,
                                block_width=block_width,
                                wind_speeds_block_range=wind_speeds_block_range,
                                turbines=turbines, mean_roughness_length=z0)
            if grouped_plots:
                # # different block widths:
                # for std_dev_method in standard_deviaton_methods:
                #     for range in [10.0, 15.0, 20.0]:
                #         plot_smoothed_pcs(
                #             standard_deviation_method=std_dev_method,
                #             block_width=block_widths,
                #             wind_speeds_block_range=range,
                #             turbines=turbines, mean_roughness_length=z0,
                #             grouped='block_width')
                # different standard deviation methods
                for range in [10.0, 15.0, 20.0]:
                    plot_smoothed_pcs(
                        standard_deviation_method=standard_deviaton_methods,
                        block_width=0.5,
                        wind_speeds_block_range=range,
                        turbines=turbines, mean_roughness_length=z0,
                        grouped='std_dev')
                # # different block ranges
                # for std_dev_method in standard_deviaton_methods:
                #     plot_smoothed_pcs(
                #         standard_deviation_method=std_dev_method,
                #         block_width=0.5,
                #         wind_speeds_block_range=wind_speeds_block_ranges,
                #         turbines=turbines, mean_roughness_length=z0,
                #         grouped='wind_speed_range')
