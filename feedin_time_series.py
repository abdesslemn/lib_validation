# Imports from Windpowerlib
from windpowerlib import wind_turbine as wt
from windpowerlib import power_output

# Imports from lib_validation
import visualization_tools
import analysis_tools
import tools

# Other imports
from matplotlib import pyplot as plt
import pandas as pd
import os
import pickle


def read_data(filename, **kwargs):
    r"""
    Fetches power time series from a file.

    Parameters
    ----------
    filename : string, optional
        Name of data file.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the data file is stored. Default: './data'
    usecols : list of strings or list of integers, optional
        .... Default: None

    Returns
    -------
    pandas.DataFrame

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__),
                                          'data')
    if 'usecols' not in kwargs:
        kwargs['usecols'] = None

    df = pd.read_csv(os.path.join(kwargs['datapath'], filename), sep=';',
                     decimal=',', thousands='.', index_col=0,
                     usecols=kwargs['usecols'])
    return df


def restructure_data(filename, filename_column_names=None, filter_cols=False,
                     drop_na=False, **kwargs):
    r"""
    Restructure data read from a csv file.

    Create a DataFrame. Data are filtered (if filter_cols is not None) and
    Nan's are droped (if drop_na is not None).

    Parameters:
    -----------
    filename : string
        Name of data file.
    filename_column_names : string, optional
        Name of file that contains column names to be filtered for.
        Default: None.
    filter_cols : list
        Column names to filter for. Default: None.
    drop_na : boolean
        If True: Nan's are droped from DataFrame with method how='any'.
        Default: None.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the data file is stored. (for read_data()) Default: './data'

    """
    df = read_data(filename, **kwargs)
    if filter_cols:
        filter_cols = []
        with open(filename_column_names) as file:
            for line in file:
                line = line.strip()
                filter_cols.append(line)
        df2 = df.filter(items=filter_cols, axis=1)
    if drop_na:
        df2 = df.dropna(axis='columns', how='all')
    return df2


def data_evaluation(filename):
    """
    Evaluate the data in terms of which variables are given for each dataset.

    Parameters:
    -----------
    filename : string
        Name of file that contains names of files to be evaluated.

    """
    # Initialise pandas.DataFrame
    df_compare = pd.DataFrame()
    # Read file and add to DataFrame for each line (= filenames)
    with open(filename) as file:
            for line in file:
                name = line.strip()
                df = restructure_data(name, drop_na=True)
                df2 = pd.DataFrame(data=df, index=list(df),
                                   columns=[name])
                df_compare = pd.concat([df_compare, df2], axis=1)
    df_compare.to_csv('evaluation.csv')
    return df_compare


def get_data(filename_files, filename_column_names, new_column_names,
             filename_pickle='pickle_dump.p', pickle_load=True):
    r"""
    Fetches data of the requested files and renames columns.

    Returns
    -------
    data : pandas.DataFrame
        Data of ArgeNetz wind farms with readable column names

    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'dumps/validation_data',
                                        filename_pickle))
    if not pickle_load:
        with open(filename_files) as file:
            data = pd.DataFrame()
            for line in file:
                name = line.strip()
                df = restructure_data(name, filename_column_names,
                                      filter_cols=True)
                df.columns = new_column_names
                data = pd.concat([data, df])  # data could also be dictionary
        pickle.dump(data, open(path, 'wb'))
    if pickle_load:
        data = pickle.load(open(path, 'rb'))
    return data


def fast_plot(df, save_folder, y_limit=None, x_limit=None):
    r"""
    Plot all data from DataFrame to single plots and save them.

    Parameters:
    -----------
    df : pandas.DataFrame
        Contains data to be plotted.
    y_limit, x_limit : list of floats or integers
        Values for ymin, ymax, xmin and xmax

    """
    for column in df.columns:
        fig = plt.figure(figsize=(8, 6))
        df[column].plot()
        plt.title(column, fontsize=20)
        plt.xticks(rotation='vertical')
        if y_limit:
            plt.ylim(ymin=x_limit[0], ymax=y_limit[1])
        if x_limit:
            plt.xlim(xmin=x_limit[0], xmax=x_limit[1])
        plt.tight_layout()
        fig.savefig(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '../Plots', save_folder,
                                                 str(column) + '.pdf')))
    plt.close()

#df_compare = data_evaluation('helper_files/filenames_all.txt')

# new_column_names_2016_2017 = [
#     'Bredstedt_P_W', 'Bredstedt_v_wind',
#     'Bredstedt_P_W_inst', 'Goeser_P_W',
#     'Goeser_v_wind', 'Goeser_P_W_inst',
#     'PPC_4919_P_W', 'PPC_4919_v_wind',
#     'PPC_4919_P_W_inst', 'PPC_4950_P_W',
#     'PPC_4950_v_wind',
#     'PPC_4950_P_W_inst', 'PPC_5598_P_W',
#     'PPC_5598_v_wind', 'PPC_5598_P_W_inst']
#
# new_column_names_2015 = [
#     'Bredstedt_P_W', 'Bredstedt_v_wind',
#     'Bredstedt_P_W_inst',
#     'Nordstrand_P_W', 'Nordstrand_P_W_inst',
#     'PPC_4919_P_W', 'PPC_4919_v_wind', 'PPC_4950_P_W',
#     'PPC_4950_v_wind', 'PPC_5598_P_W',
#     'PPC_5598_P_W_inst']

new_column_names_2016_2017 = [
   'Bredstedt_P_W', 'Bredstedt_P_W_theo', 'Bredstedt_v_wind',
   'Bredstedt_wind_dir', 'Bredstedt_P_W_inst', 'Goeser_P_W',
   'Goeser_P_W_theo', 'Goeser_v_wind', 'Goeser_wind_dir', 'Goeser_P_W_inst',
   'PPC_4919_P_W', 'PPC_4919_P_W_theo', 'PPC_4919_v_wind',
   'PPC_4919_wind_dir', 'PPC_4919_P_W_inst', 'PPC_4950_P_W',
   'PPC_4950_P_W_theo', 'PPC_4950_v_wind', 'PPC_4950_wind_dir',
   'PPC_4950_P_W_inst', 'PPC_5598_P_W', 'PPC_5598_P_W_theo',
   'PPC_5598_v_wind', 'PPC_5598_wind_dir', 'PPC_5598_P_W_inst']

new_column_names_2015 = [
   'Bredstedt_P_W', 'Bredstedt_P_W_theo', 'Bredstedt_v_wind',
   'Bredstedt_wind_dir', 'Bredstedt_P_W_inst',
   'Nordstrand_P_W', 'Nordstrand_P_W_theo', 'Nordstrand_P_W_inst',
   'PPC_4919_P_W', 'PPC_4919_P_W_theo', 'PPC_4950_P_W',
   'PPC_4950_P_W_theo', 'PPC_4950_v_wind', 'PPC_5598_P_W',
   'PPC_5598_P_W_inst', 'PPC_5598_P_W_theo']


def get_and_plot_feedin(year, pickle_load=False, plot=False, x_limit=None):
    r"""
    Fetches ArgeNetz data for specified year and plots feedin.
    
    Returns
    -------
    data : pandas.DataFrame
        Data of ArgeNetz wind farms with readable column names (see function
        get_data()).
    """
    if year == 2015:
        filename_column_names = 'helper_files/column_names_2015.txt'
        #new_column_names = new_column_names_2015
    if (year == 2016 or year == 2017):
        filename_column_names = 'helper_files/column_names_2016_2017.txt'
        new_column_names = new_column_names_2016_2017
    data = get_data('helper_files/filenames_{0}.txt'.format(year),
                    filename_column_names, new_column_names,
                    'arge_data_{0}.p'.format(year), pickle_load=pickle_load)
    if plot:
        fast_plot(
            data, save_folder='ArgeNetz_power_output/Plots_{0}'.format(
                year), x_limit=x_limit)
    return data


def get_energy_map_data(plz, place=None, peak_power=None,
                        pickle_load=False, pickle_path=None):
    if not pickle_load:
        df_energymap = pd.read_csv(
            os.path.join(os.path.join(os.path.dirname(__file__),
                                      'data/Energymap'),
                         'eeg_anlagenregister_2015.08.utf8.csv'),
            skiprows=[0, 1, 2, 4], sep=';', decimal=',', thousands='.')
        df_energymap['PLZ'] == plz
        pickle.dump(df_energymap, open(os.path.join(pickle_path,
                                                    'energy_map'), 'wb'))
    if pickle_load:
            df_energymap = pickle.load(open(pickle_path, 'rb'))
    df_energymap = df_energymap.loc[df_energymap['Ort'] == place]
    df_energymap = df_energymap.loc[df_energymap['Anlagentyp'] == 'Windkraft']
    df_energymap = df_energymap.loc[
        df_energymap['Nennleistung(kWp_el)'] == peak_power]
    return df_energymap


def check_arge_netz_data(df, year, start, end):
    r"""


    """
    wind_farm_names = ['Bredstedt', 'PPC_4919', 'PPC_4950', 'PPC_5598']
    wind_turbine_amount = [(0, 16), (4, 13), (0, 22), (0, 14)]
    # Turbine data
    enerconE70 = {
        'turbine_name': 'ENERCON E 70 2300',
        'hub_height': 64,  # in m
        'rotor_diameter': 71  # in m
    }
    enerconE66 = {
        'turbine_name': 'ENERCON E 66 1800',
        'hub_height': 65,  # in m
        'rotor_diameter': 70  # in m
        }
    # Initialize WindTurbine objects
    e70 = wt.WindTurbine(**enerconE70)
    e66 = wt.WindTurbine(**enerconE66)
    for name, turbine_amount in zip(wind_farm_names, wind_turbine_amount):
        indices = tools.get_indices_for_series(1, year)
        power_output_theo = df[name + '_P_W_theo'] / 1000
        power_output_theo = pd.Series(data=power_output_theo.values,
                                      index=indices)
        power_output_by_wind_speed = (turbine_amount[0] * power_output.power_curve(
            df[name + '_v_wind'], e66.power_curve['wind_speed'],
            e66.power_curve['values']) +
            turbine_amount[1] * power_output.power_curve(
            df[name + '_v_wind'], e70.power_curve['wind_speed'],
            e70.power_curve['values'])) / (1*10**6)
        power_output_by_wind_speed = pd.Series(
            data=power_output_by_wind_speed.values, index=indices)
        val_obj = analysis_tools.ValidationObject(
            'validate_arge_4919', power_output_theo,
            power_output_by_wind_speed,
            weather_data_name='calculated by wind speed',
            validation_name='P_W theoretical')
        val_obj.output_method = 'power_output'
        visualization_tools.plot_feedin_comparison(
            val_obj, filename='../Plots/Test_Arge/{0}_{1}_feedin'.format(
                year, name),
            title='{0}'.format(name), start=start, end=end)
        visualization_tools.plot_correlation(
            val_obj, filename='../Plots/Test_Arge/{0}_{1}_corr'.format(
                year, name),
            title='{0}'.format(name))

if __name__ == "__main__":
    year = 2016  # dont use 2015 - no wind speed!
    start = None
    end = None
    # Get ArgeNetz Data
    arge_netz_data = get_and_plot_feedin(
        year, pickle_load=False, plot=True)
    check_arge_netz_data(arge_netz_data, year, start, end)
    print('Done')
#    print(arge_netz_data)

## Evaluate WEA data from Energymap
#pickle_load = False
#pickle_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dumps/validation_data'))
#plz = 25821
#place = 'Struckum'
#peak_power = 2300
#df_energymap = get_energy_map_data(plz, place, peak_power,
#                                   pickle_load, pickle_path)
#print(df_energymap)

# Get the data of 2015 (and 2016/2017) and plot the results
#x_limit = None
#data_2015 = get_data('filenames_2015.txt', new_column_names_2015,
#                     'arge_data_2015.p', pickle_load=True)
#fast_plot(data_2015, save_folder='ArgeNetz_power_output/Plots_2015',
#          x_limit=x_limit)
#data_2016_2017 = get_data('filenames_2016_2017.txt',
#                          'column_names_2016_2017.txt',
#                          new_column_names_2016_2017, 'arge_data_2016_2017.p',
#                          pickle_load=True)
#fast_plot(data_2016_2017, save_folder='ArgeNetz_power_output/Plots_2016_2017',
#          x_limit=x_limit)

# Sample for period of 2015 (possible mistakes in data)
#data = get_data('filenames.txt', 'column_names_2015.txt',
#                 new_column_names_2015, 'arge_data_2015.p', pickle_load=True)
#x_limit = [10, 50]
#fast_plot(data, save_folder='Plots_2015_period', x_limit=x_limit)