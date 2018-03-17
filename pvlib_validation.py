import pandas as pd
import matplotlib.pyplot as mpl
import numpy as np
import os
from collections import OrderedDict

import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib import irradiance

import read_htw_data
import get_weather_data
import analysis_tools
import tools


#ToDo nochmal prüfen welche Werte Instantanwerte und Mittelwerte sind und am
# besten Index bei Mittelwerten auf Mittelpunkt des Zeitintervalls setzen;
# resample der HTW Werte eventuell nochmal anpassen

def setup_correlation_df(htw_weather_data_df, reanalysis_weather_data_df,
                         parameter, weather_data='open_FRED', corrected=True):
    # Note: in case of DNI FRED DNI and calculated DNI (calculated from FRED
    # GHI and DHI) are compared; in case of GHI and GNI HTW (measured) values
    # are compared to FRED (calculated) values

    # setup dataframe with given parameter of HTW and FRED weather dataset
    if parameter == 'dni':
        df = calculate_dni_pvlib(reanalysis_weather_data_df, weather_data,
                                 corrected)
    else:
        df = reanalysis_weather_data_df[parameter].to_frame().join(
            htw_weather_data_df[parameter].to_frame(),
            lsuffix='_fred', rsuffix='_htw')
    return df


def compare_parameters(df, parameter, resample_rule, plot_directory):
    # calculate correlation
    corr = analysis_tools.correlation_tmp(df, resample_rule=resample_rule)

    # plot correlation
    corr.plot()
    mpl.savefig(os.path.join(
        plot_directory, '{}_correlation_{}.png'.format(
            parameter, resample_rule)))

    # calculate RMSE
    rmse = analysis_tools.variability(df, resample_rule=resample_rule)

    # plot correlation
    rmse.plot()
    mpl.savefig(os.path.join(
        plot_directory, '{}_rmse_{}.png'.format(
            parameter, resample_rule)))


def plot_week(df, parameter, weather_data, measured_data, plot_directory,
              winter_week=('1/25/2015', '2/1/2015'),
              summer_week=('6/2/2015', '6/8/2015')):
    # winter_week - tuple with start and end date

    # plot winter week

    # set frequency of index
    if weather_data == 'open_FRED':
        index = pd.date_range(start=winter_week[0], end=winter_week[1],
                              freq='30Min', tz='UTC') \
                - pd.Timedelta(minutes=15)
    elif weather_data == 'MERRA':
        index = pd.date_range(start=winter_week[0], end=winter_week[1],
                              freq='60Min', tz='UTC')

    df.loc[index, :].plot()
    mpl.savefig(os.path.join(plot_directory, '{}_winter_week_{}_{}.png'.format(
        parameter, weather_data, measured_data)))

    # plot summer week

    # set frequency of index
    if weather_data == 'open_FRED':
        index = pd.date_range(start=summer_week[0], end=summer_week[1],
                              freq='30Min', tz='UTC') \
                - pd.Timedelta(minutes=15)
    elif weather_data == 'MERRA':
        index = pd.date_range(start=summer_week[0], end=summer_week[1],
                              freq='60Min', tz='UTC')

    df.loc[index, :].plot()
    mpl.savefig(os.path.join(plot_directory, '{}_summer_week_{}_{}.png'.format(
        parameter, weather_data, measured_data)))


def calculate_dni_pvlib(weather_df, weather_data, corrected=True):

    if weather_data == 'open_FRED':
        # save initial index in column 'time'
        weather_df_copy = weather_df.copy()
        weather_df_copy.reset_index(inplace=True)
        weather_df_copy.set_index('time', drop=False, inplace=True)
        weather_df_copy['new_index'] = weather_df_copy.index + \
                                       pd.Timedelta(minutes=15)
        weather_df_copy.set_index('new_index', drop=True, inplace=True)

    # calculate DNI
    times = weather_df_copy.index
    location = setup_pvlib_location_object()
    solarposition = location.get_solarposition(
        times, pressure=None, temperature=weather_df_copy['temp_air'])
    if corrected:
        # calculate corrected DNI
        clearsky = location.get_clearsky(times, solar_position=solarposition)
        dni = irradiance.dni(weather_df_copy['ghi'], weather_df_copy['dhi'],
                             zenith=solarposition['zenith'],
                             clearsky_dni=clearsky['dni'],
                             clearsky_tolerance=1.1,
                             zenith_threshold_for_zero_dni=88.0,
                             zenith_threshold_for_clearsky_limit=80.0)
    else:
        dni = (weather_df_copy['ghi'] - weather_df_copy['dhi']) / np.cos(
            np.radians(solarposition['zenith']))

    # setup df with calculated and Fred DNI
    dni.name = 'dni'
    df = weather_df_copy['dni'].to_frame().join(
        dni.to_frame(),
        lsuffix='_fred', rsuffix='_pvlib')
    dni.set_index('time', inplace=True)

    return df


def setup_pvlib_location_object():
    return Location(latitude=52.456032, longitude=13.525282,
                    tz='UTC', altitude=60, name='HTW Berlin')


def setup_htw_pvlib_pvsystem(converter_number):

    # get module and inverter parameters
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    sandia_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')
    CEC_modules = pvlib.pvsystem.retrieve_sam('CECMod')
    CEC_inverters = pvlib.pvsystem.retrieve_sam('sandiainverter')

    inv_sma = 'SMA_Solar_Technology_AG__SB3000HFUS_30___240V_240V__CEC_2011_'
    inv_danfoss = 'Danfoss_Solar__DLX_2_9_UL__240V__240V__CEC_2013_'

    # module 1 - Schott aSi 105W / Danfoss DLX 2.9
    if converter_number == 'wr1':
        pass
    # module 2 - Aleo S19 285W / Danfoss DLX 2.9 'Aleo_Solar_S19H270' CEC
    elif converter_number == 'wr2':
        pass

    # module 3 - Aleo S18 240W / Danfoss DLX 2.9
    elif converter_number == 'wr3':
        pv_module = PVSystem(module='aleo_solar_S18_240', inverter=inv_danfoss,
                             module_parameters=CEC_modules[
                                 'aleo_solar_S18_240'],
                             inverter_parameters=CEC_inverters[inv_danfoss],
                             surface_tilt=14.57, surface_azimuth=215.,
                             albedo=0.2,
                             modules_per_string=14, strings_per_inverter=1,
                             name='HTW_module_3')
        pv_module.module_parameters['EgRef'] = 1.121
        pv_module.module_parameters['dEgdT'] = -0.0002677
        pv_module.module_parameters['alpha_sc'] = 0.04

    # module 4 - Aleo S19 245W / SMA SB 3000HF-30
    elif converter_number == 'wr4':
        pv_module = PVSystem(module='Aleo_Solar_S19U245_ulr', inverter=inv_sma,
                             module_parameters=CEC_modules[
                                 'Aleo_Solar_S19U245_ulr'],
                             inverter_parameters=CEC_inverters[inv_sma],
                             surface_tilt=14.57, surface_azimuth=215.,
                             albedo=0.2,
                             modules_per_string=13, strings_per_inverter=1,
                             name='HTW_module_4')
        pv_module.module_parameters['EgRef'] = 1.121
        pv_module.module_parameters['dEgdT'] = -0.0002677
        pv_module.module_parameters['alpha_sc'] = 0.03
    # module 5 - Schott aSi 105W / SMA SB 3000HF-30
    elif converter_number == 'wr5':
        pass
    return pv_module


def setup_and_run_modelchain(pv_system, location, weather_data):

    mc = ModelChain(system=pv_system, location=location,
                    aoi_model='no_loss', spectral_model='no_loss')
    mc.run_model(weather_data.index, weather=weather_data)
    return mc


def reindl(ghi, i0_h, elevation):

    elevation = pvlib.tools.sind(elevation)

    # calculate clearness index kt
    kt = np.maximum(0, ghi / (i0_h * elevation))

    # calculate diffuse fraction DHI/GHI
    # for kt <= 0.3
    df = 1.02 - 0.254 * kt + 0.0123 * elevation
    # for kt > 0.3 and kt <= 0.78
    df = np.where((kt > 0.3) & (kt <= 0.78),
                  np.fmin(0.97, np.fmax(
                      0.1, 1.4 - 1.794 * kt + 0.177 * elevation)),
                  df)
    # for kt > 0.78
    df = np.where(kt > 0.78, np.fmax(0.1, 0.486 * kt + 0.182 * elevation), df)

    # eliminate extreme data according to limits Case 1 and Case 2 in Reindl
    df = np.where(((df < 0.9) & (kt < 0.2)) |
                  ((df > 0.8) & (kt > 0.6)) |
                  (df > 1) | (ghi - i0_h > 0), 0, df)

    dhi = df * ghi
    dni = (ghi - dhi) / elevation

    data = OrderedDict()
    data['dni'] = dni
    data['dhi'] = dhi
    data['kt'] = kt

    if isinstance(ghi, pd.Series):
        data = pd.DataFrame(data)

    return data


def decomposition(merra_df, model, location):

    solar_position = location.get_solarposition(
        merra_df.index, pressure=merra_df['pressure'].mean(),
        temperature=merra_df['temp_air'].mean())

    if model == 'reindl':

        solar_position = location.get_solarposition(
            merra_df.index, pressure=merra_df['pressure'].mean(),
            temperature=merra_df['temp_air'].mean())

        df = reindl(merra_df.ghi, merra_df.i0_h, solar_position.elevation)
        df['dni_corrected'] = irradiance.dni(
            merra_df['ghi'], df['dhi'], solar_position.zenith,
            clearsky_dni=location.get_clearsky(
                merra_df.index, solar_position=solar_position).dni,
            clearsky_tolerance=1.1,
            zenith_threshold_for_zero_dni=88.0,
            zenith_threshold_for_clearsky_limit=80.0)

    elif model == 'erbs':

        df = irradiance.erbs(merra_df.ghi, solar_position.zenith,
                                  merra_df.index)
        df['dni_corrected'] = irradiance.dni(
            merra_df['ghi'], df['dhi'], solar_position.zenith,
            clearsky_dni=location.get_clearsky(
                merra_df.index, solar_position=solar_position).dni,
            clearsky_tolerance=1.1,
            zenith_threshold_for_zero_dni=88.0,
            zenith_threshold_for_clearsky_limit=80.0)

    elif model == 'disc':

        df = irradiance.disc(merra_df.ghi, solar_position.zenith,
                             merra_df.index, merra_df.pressure.mean())

    return df


def compare_decomposition_models(merra_df, location, htw_weather_df,
                                 plot=False):
    """
    Compares the decomposition models Reindl, Erbs and Disc. Calculates
    correlation and RMSE and optionally plots these plus a winter and summer
    week.

    """

    # reindl
    df_reindl = decomposition(merra_df, 'reindl', location=location)
    df_reindl['gni'] = (df_reindl.dni + df_reindl.dhi).fillna(0)
    df_reindl['gni_corrected'] = (df_reindl.dni_corrected +
                                  df_reindl.dhi).fillna(0)

    # erbs
    df_erbs = decomposition(merra_df, 'erbs', location=location)
    df_erbs['gni'] = df_erbs.dni + df_erbs.dhi
    df_erbs['gni_corrected'] = df_erbs.dni_corrected + df_erbs.dhi

    # disc
    df_disc = decomposition(merra_df, 'disc', location=location)

    # combine dataframes
    df_comp = df_reindl.loc[:, ['gni', 'gni_corrected']].join(
        df_erbs.loc[:, ['gni', 'gni_corrected']],
        how='outer', rsuffix='_erbs', lsuffix='_reindl')
    df_comp = df_comp.join(df_disc.gni.rename('gni_disc').to_frame(),
                           how='outer', rsuffix='_disc')

    # calculate correlation and rmse
    plot_directory = 'plot'
    weather_data = 'MERRA'
    measured_data = 'HTW'

    parameter_list = ['gni_disc', 'gni_corrected_reindl', 'gni_corrected_erbs']
    count = 0
    for param in parameter_list:
        df = htw_weather_df['gni'].to_frame().join(
            df_comp[param].to_frame(), how='outer')
        corr = analysis_tools.correlation_tmp(df, '1W', min_count=100).rename(
            'corr_gni_htw_{}'.format(param))
        var = analysis_tools.variability(df, '1W', min_count=100).rename(
            'rmse_gni_htw_{}'.format(param))
        corr_year = analysis_tools.correlation_tmp(df, '1Y')
        print('Correlation {}: {}'.format(param, corr_year.iloc[0]))
        var_year = analysis_tools.variability(df, '1Y')
        print('RMSE {}: {}'.format(param, var_year.iloc[0]))
        if plot:
            plot_week(df.fillna(0), param, weather_data, measured_data,
                      plot_directory,
                      winter_week=('1/25/2015', '2/1/2015'),
                      summer_week=('6/2/2015', '6/8/2015'))
        if count == 0:
            corr_df = corr.to_frame()
            var_df = var.to_frame()
        else:
            corr_df = corr_df.join(corr.to_frame())
            var_df = var_df.join(var.to_frame())
        count += 1

    if plot:
        corr_df.plot()
        mpl.savefig(
            os.path.join(plot_directory, '{}_winter_week_{}_{}.png'.format(
                'correlation', weather_data, measured_data)))
        var_df.plot()
        mpl.savefig(
            os.path.join(plot_directory, '{}_winter_week_{}_{}.png'.format(
                'RMSE', weather_data, measured_data)))


    return df_comp


def load_merra_data(year, lat, lon, directory):
    # read csv file
    merra_df = pd.read_csv(
        os.path.join(directory, 'weather_data_GER_{}.csv'.format(year)),
        header=[0], index_col=[0], parse_dates=True)
    # get closest coordinates to given location
    lat_lon = tools.get_closest_coordinates(merra_df, [lat, lon])
    # get weather data for closest location
    df = merra_df[(merra_df['lon'] == lat_lon['lon']) &
                  (merra_df['lat'] == lat_lon['lat'])]
    # convert time index to local time
    df.index = df.index.tz_localize('UTC').tz_convert('Europe/Berlin')
    # rename columns to fit needs of pvlib
    df.rename(columns={'T': 'temp_air', 'v_50m': 'wind_speed', 'p': 'pressure',
                       'SWTDN': 'i0_h', 'SWGDN': 'ghi'}, inplace=True)
    # convert temperature to °C
    df.loc[:, 'temp_air'] = df.temp_air - 273.15
    return df


if __name__ == '__main__':

    # year = 2015
    # location = setup_pvlib_location_object()
    # merra_df = load_merra_data(year, location.latitude, location.longitude,
    #                            'data/Merra')
    # htw_weather_data = read_htw_data.setup_weather_dataframe(
    #     weather_data='MERRA')
    # compare_decomposition_models(merra_df, location, htw_weather_data)

    plot_directory = 'plot'
    weather_data = 'MERRA'
    measured_data = 'HTW'
    converters = ['wr3', 'wr4']

    ###########################################################################
    # read HTW converter data
    ###########################################################################

    htw_wr_data = {}
    for converter in converters:
        htw_wr_data[converter] = read_htw_data.setup_converter_dataframe(
            converter, weather_data)

    ###########################################################################
    # get weather data HTW
    ###########################################################################

    htw_weather_data = read_htw_data.setup_weather_dataframe(weather_data)

    ###########################################################################
    # setup location
    ###########################################################################

    location = setup_pvlib_location_object()

    ###########################################################################
    # get weather data
    ###########################################################################

    if weather_data == 'open_FRED':
        path = 'data/Fred/BB_2015'
        filename = 'fred_data_2015_htw.csv'
        weather_data_df = get_weather_data.read_of_weather_df_pvlib_from_csv(
            path, filename, coordinates=None)
    else:
        weather_data_df = load_merra_data(
            2015, location.latitude, location.longitude, 'data/Merra')
        decomposition_df = decomposition(weather_data_df, 'erbs', location)
        try:
            weather_data_df['dni'] = decomposition_df.dni_corrected.fillna(0)
        except:
            weather_data_df['dni'] = decomposition_df.dni.fillna(0)
        weather_data_df['dhi'] = decomposition_df.dhi.fillna(0)
        weather_data_df['dirhi'] = weather_data_df.ghi - weather_data_df.dhi

    # ##############################################################################
    # # compare FRED and HTW weather data
    # ##############################################################################
    #
    # # ghi
    # parameter = 'ghi'
    # resample_rule = '1M'
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data)
    # compare_parameters(df, parameter, resample_rule, plot_directory)
    # plot_week(parameter, weather_data, measured_data, plot_directory)
    #
    # # gni
    # parameter = 'gni'
    # resample_rule = '1M'
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data)
    # compare_parameters(df, parameter, resample_rule, plot_directory)
    # plot_week(parameter, weather_data, measured_data, plot_directory)
    #
    # # dni
    # parameter = 'dni'
    # resample_rule = '1M'
    # weather_data = 'open_FRED'
    # corrected = True
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data, corrected=corrected)
    # compare_parameters(df, parameter + '_corrected', resample_rule,
    #                    plot_directory)
    # plot_week(parameter + '_corrected', weather_data, plot_directory)
    #
    # corrected = False
    # df = setup_correlation_df(htw_weather_data, fred_weather_data, parameter,
    #                           weather_data, corrected=corrected)
    # compare_parameters(df, parameter + '_uncorrected', resample_rule,
    #                    plot_directory)
    # plot_week(parameter + '_uncorrected', weather_data, plot_directory)
    #
    ###########################################################################
    # setup modules
    ###########################################################################

    modules = {}
    for converter in converters:
        modules[converter] = setup_htw_pvlib_pvsystem(converter)

    ###########################################################################
    # call modelchain with reanalysis data
    ###########################################################################

    for converter in converters:
        # set up modelchain
        mc = setup_and_run_modelchain(
            modules[converter], location, weather_data_df)

        # calculate monthly correlation and RMSE
        resample_rule = '1M'
        parameter = 'feedin_{}_{}'.format(converter, weather_data)
        feedin = mc.dc.p_mp.to_frame().join(
            htw_wr_data[converter]['P_DC'].to_frame())
        feedin.rename(columns={'p_mp': 'energy_calculated',
                               'P_DC': 'energy_measured'},
                      inplace=True)
        compare_parameters(feedin, parameter, resample_rule, plot_directory)
        plot_week(feedin, parameter, weather_data, 'htw', plot_directory)

        # compare monthly energy
        monthly_energy = feedin.resample('1M').sum()
        monthly_energy.plot()
        mpl.savefig(os.path.join(plot_directory,
                                 'feedin_{}_{}_energy.png'.format(
                                     converter, weather_data)))

    ###########################################################################
    # call modelchain with HTW data
    ###########################################################################

    htw_weather_data_modified = weather_data_df.copy()
    htw_weather_data_modified['ghi'] = htw_weather_data['ghi']
    htw_weather_data_modified['dhi'] = htw_weather_data_modified['ghi'] - \
                                       htw_weather_data_modified['dirhi']
    for converter in converters:
        # set up modelchain
        mc = setup_and_run_modelchain(modules[converter], location,
                                      htw_weather_data_modified)
        # calculate monthly correlation
        resample_rule = '1M'
        parameter = 'feedin_{}_{}'.format(converter, weather_data)
        feedin = mc.dc.p_mp.to_frame().join(
            htw_wr_data[converter]['P_DC'].to_frame())
        feedin.rename(columns={'p_mp': 'energy_calculated',
                               'P_DC': 'energy_measured'},
                      inplace=True)
        compare_parameters(feedin, parameter, resample_rule, plot_directory)
        plot_week(feedin, parameter, weather_data, 'htw', plot_directory)

        # compare monthly energy
        monthly_energy = feedin.resample('1M').sum()
        monthly_energy.plot()
        mpl.savefig(os.path.join(plot_directory,
                                 'feedin_{}_{}_energy.png'.format(
                                     converter, weather_data)))
