from windpowerlib.wind_turbine import WindTurbine
from windpowerlib.wind_farm import WindFarm
from windpowerlib.power_output import summarized_power_curve
from windpowerlib import wind_farm_modelchain
from windpowerlib import power_output, tools
import pandas as pd
import numpy as np
import wind_farm_specifications
from tools import get_weather_data
from matplotlib import pyplot as plt
import os
import pickle


def smooth_pc(plot=True, print_out=False):
    # initialise WindTurbine object
    turbines = wind_farm_specifications.initialize_turbines(
        ['enerconE70', 'enerconE66'])
    z0 = pd.Series([0.04, 0.04, 0.04])
    block_width = 0.5
    standard_deviation_method = 'turbulence_intensity'
    # standard_deviation_method='Staffell'
    # turbulence_intensity = (2.4 * 0.41) / np.log(135/z0.mean()) *
    # np.exp(-135/500) # constant boundary layer
    for turbine in turbines:
        turbulence_intensity = tools.estimate_turbulence_intensity(
            turbine.hub_height, z0.mean())
        smoothed_power_curve = power_output.smooth_power_curve(
            turbine.power_curve.wind_speed, turbine.power_curve['power'],
            block_width=block_width,
            standard_deviation_method=standard_deviation_method,
            turbulence_intensity=turbulence_intensity)
        if print_out:
            print(turbine.power_curve)
            print(smoothed_power_curve)
        if plot:
            fig = plt.figure()
            a, = plt.plot(turbine.power_curve['wind_speed'],
                         turbine.power_curve['power']/1000, label='original')
            b, = plt.plot(smoothed_power_curve['wind_speed'],
                         smoothed_power_curve['power']/1000, label='smoothed')
            plt.ylabel('Power in kW')
            plt.xlabel('Wind speed in m/s')
            plt.title(turbine.object_name)
            plt.legend(handles=[a, b])
            fig.savefig(os.path.abspath(os.path.join(
                os.path.dirname(__file__), '../Plots/power_curves',
                '{0}_{1}_{2}.pdf'.format(turbine.object_name,
                                         standard_deviation_method,
                                         block_width))))
            plt.close()
        return smoothed_power_curve

# variables = pd.Series(data=np.arange(-15.0, 15.0, 0.5), index=np.arange(-15.0, 15.0, 0.5))
# wind_speed = 12
# # variables = np.arange(-15.0, 15.0, 0.5)
# gauss =  tools.gaussian_distribution(variables, standard_deviation=0.15*wind_speed, mean=0)
# gauss.index = gauss.index + wind_speed
# gauss.plot()
# plt.show()
# print(gauss)


def summarized_pc(plot=False):
    enerconE70 = {
            'object_name': 'ENERCON E 70 2300',
            'hub_height': 64,
            'rotor_diameter': 71
        }
    enerconE66 = {
                'object_name': 'ENERCON E 66 1800',
                'hub_height': 65,
                'rotor_diameter': 70
            }
    vestasV126 = {
                'object_name': 'VESTAS V 126 3300',
                'hub_height': 117,
                'rotor_diameter': 126
            }
    e70 = WindTurbine(**enerconE70)
    e66 = WindTurbine(**enerconE66)
    v126 = WindTurbine(**vestasV126)
    parameters = {'wind_turbine_fleet': [{'wind_turbine': e70,
                                          'number_of_turbines': 13},
                                         {'wind_turbine': e66,
                                          'number_of_turbines': 4},
                                         {'wind_turbine': v126,
                                          'number_of_turbines': 2}],
                  'smoothing': True,
                  'density_correction': False,
                  'roughness_length': 0.4
                  }
    power_curve_exp = 2
    summarized_power_curve_df = summarized_power_curve(**parameters)
    if plot:
        plt.plot(summarized_power_curve_df['wind_speed'],
                 summarized_power_curve_df['power'])
        plt.show()
        plt.close()
    return summarized_power_curve_df


def wind_farms_hub_height():
    e70, e66 = wind_farm_specifications.initialize_turbines(['enerconE70',
                                                             'enerconE66'])
    wf_3 = {
        'object_name': 'wf_3',
        'wind_turbine_fleet': [{'wind_turbine': e70,
                                'number_of_turbines': 13},
                               {'wind_turbine': e66,
                                'number_of_turbines': 4}],
        'coordinates': [54.629167, 9.0625]}
    wf = WindFarm(**wf_3)
    return wf.mean_hub_height


def wind_farm_model_chain():
    e70, e66 = wind_farm_specifications.initialize_turbines(['enerconE70',
                                                             'enerconE66'])
    wf_3 = {
        'object_name': 'wf_3',
        'wind_turbine_fleet': [{'wind_turbine': e70,
                                'number_of_turbines': 13},
                               {'wind_turbine': e66,
                                'number_of_turbines': 4}],
        'coordinates': [54.629167, 9.0625]}
    wf = WindFarm(**wf_3)
    filename_weather = os.path.join(os.path.dirname(__file__), 'dumps/weather',
                                    'weather_df_MERRA_2015.p')
    weather = get_weather_data(
        'MERRA', wf.coordinates, pickle_load=True, filename=filename_weather,
        year=2015, temperature_heights=[64, 65])
    mc = wind_farm_modelchain.WindFarmModelChain(wf).run_model(weather)
    return mc.power_output

if __name__ == "__main__":
#    print(summarized_pc(plot=False))
#    print(wind_farms_hub_height())
#    smooth_pc(plot=True, print_out=False)
    print(wind_farm_model_chain())
