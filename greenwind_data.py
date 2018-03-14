"""
The ``greenwind_data`` module contains functions to read and dump measured
feed-in time series from a GreenWind wind farm.

# The following data is available (year 2016) for the 17 turbines:
# - meter (Zählerstand) in kW
# - power output in kW
# - wind speed in m/s
# - wind direction (gondel position) in °
# ATTENTION: gondel position is not correct!!
#
# Additionally the sum of the power output of all wind turbines is available in
# column 'wf_9_power_output'.

DateTimeIndex in 'Europe/Berlin' time zone.
"""

# Imports from lib_validation
import visualization_tools
import analysis_tools
import tools

# Other imports
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import os
import pickle


def read_data(filename):
    r"""
    Fetches data from a csv file.

    Parameters
    ----------
    filename : string
        Name of data file.

    Returns
    -------
    pandas.DataFrame

    """
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  'data/GreenWind', filename),
                     sep=',', decimal='.', index_col=0)
    return df


def get_greenwind_data(year, pickle_load=False, filename='greenwind_dump.p',
                      resample=True, plot=False, x_limit=None,
                      frequency='30T', pickle_dump=True):
    # TODO: add plots to check data
    r"""
    Fetches GreenWind data.

    Parameters
    ----------
    year : Integer
        Year to fetch.
    pickle_load : Boolean
        If True data frame is loaded from the pickle dump if False the data is
        loaded from the original csv files (or from smaller csv file that was
        created in an earlier run if `csv_load` is True).
        Either set `pickle_load` or `csv_load` to True. Default: False.
    filename : String
        Filename including path of pickle dump. Default: 'greenwind_dump.p'.
    resample : Boolean
        If True the data will be resampled to the `frequency`. (mean power)
        Default: True.
    plot : Boolean
        If True each column of the data farme is plotted into a seperate
        figure. Default: False
    x_limit : list of floats or integers
        Values for xmin and xmax in case of `plot` being True and x limits
        wanted. Default: None.
    frequency : String (or freq object...?)
        # TODO add
    pickle_dump : Boolean
        If True the data frame is dumped to `filename`. Default: True.

    Returns
    -------
    greendwind_df : pandas.DataFrame
        GreenWind wind farm data.

    """
    if pickle_load:
        greenwind_df = pickle.load(open(filename, 'rb'))
    else:
        filenames = [
            # 'WF1_{0}.csv'.format(year),
            'WF2_{0}.csv'.format(year),
            'WF3_{0}.csv'.format(year)]
        greenwind_df = pd.DataFrame()
        for name in filenames:
            df_part = read_data(name).drop_duplicates()
            # Add to DataFrame
            greenwind_df = pd.concat([greenwind_df, df_part], axis=1)
        # Convert index to DatetimeIndex and make time zone aware
        greenwind_df.index = pd.to_datetime(greenwind_df.index).tz_localize(
            'UTC').tz_convert('Europe/Berlin')
        if resample:
            greenwind_df = greenwind_df.resample(frequency).mean()
        else:
            # Add frequency attribute
            freq = pd.infer_freq(greenwind_df.index)
            greenwind_df.index.freq = pd.tseries.frequencies.to_offset(freq)
        if pickle_dump:
            pickle.dump(greenwind_df, open(filename, 'wb'))
    return greenwind_df


def get_error_numbers(year):
    filename = os.path.join(
        os.path.dirname(__file__), 'dumps/validation_data',
        'greenwind_data_{0}.p'.format(year))
    df = get_greenwind_data(year=year, resample=False,
                            pickle_load=False, filename=filename,
                            pickle_dump=False)
    error_numbers = []
    for column_name in list(df):
        if 'error_number' in column_name:
            error_numbers.extend(df[column_name].unique())
    sorted_error_numbers = pd.Series(
        pd.Series(error_numbers).unique()).sort_values()
    sorted_error_numbers.index = np.arange(len(sorted_error_numbers))
    return sorted_error_numbers


if __name__ == "__main__":
    years = [
        2015,
        2016
    ]
    Decide whether to resample to a certain frequency
    resample = True
    frequency = '30T'
    for year in years:
        filename = os.path.join(os.path.dirname(__file__), 'dumps/validation_data',
                                'greenwind_data_{0}.p'.format(year))
        df = get_greenwind_data(year=year, resample=resample, filename=filename)

    # Evaluation of error numbers - decide whether to execute:
    error_numbers = False
    if error_numbers:
        error_numbers_total =[]
        for year in years:
            error_numbers = get_error_numbers(year)
            error_numbers.to_csv(
                '../../../User-Shares/Masterarbeit/Daten/Twele/' +
                'error_numbers_{}.csv'.format(year))
            error_numbers_total.extend(error_numbers)
        sorted_error_numbers_total = pd.Series(
            pd.Series(error_numbers_total ).unique()).sort_values()
        sorted_error_numbers_total.index = np.arange(
            len(sorted_error_numbers_total ))
        sorted_error_numbers_total.to_csv(
            '../../../User-Shares/Masterarbeit/Daten/Twele/error_numbers_total.csv')