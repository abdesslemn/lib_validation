import pandas as pd
import os


def create_column_format(number_of_columns, position='c', index_columns='l'):
        r"""
        Creates column format for pd.DataFrame.to_latex() function.

        Parameters
        ----------
        number_of_columns : Integer
            Number of columns of the table to be created without index column.
        position : String
            Position of text in columns. For example: 'c', 'l', 'r'.

        """
        column_format = index_columns
        for i in range(number_of_columns):
            column_format = column_format.__add__(position)
        return column_format


def replacement_of_characters(string, replacement_list):
    for replacement in replacement_list:
        string = string.replace(replacement[0], replacement[1])
    return string


def write_latex_output(latex_output, weather_data_list, approach_list,
                       restriction_list, val_obj_dict, annual_energy_dicts,
                       wind_farm_names, key_figures_print, output_methods,
                       path_latex_tables, filename_add_on, year, case,
                       replacement):
    print(year)
    if 'annual_energy_approaches' in latex_output:
        for weather_data_name in weather_data_list:
            latex_df = pd.DataFrame()
            for outerKey, innerDict in annual_energy_dicts[
                    weather_data_name].items():
                df_part = pd.DataFrame(
                    {(replacement_of_characters(innerKey, replacement),
                      innerstKey): [values] for
                     innerKey, innerstDict in innerDict.items() if (
                         innerKey != 'measured_annual_energy' and
                         innerKey not in restriction_list) for
                     innerstKey, values in innerstDict.items()},
                    index=[outerKey.replace('wf_', 'WF ').replace(
                        '_', ' ')])
                df_part['measured', '[MWh]'] = (
                    annual_energy_dicts[weather_data_name][outerKey][
                        'measured_annual_energy'])
                latex_df = pd.concat([latex_df, df_part], axis=0)
            latex_df.sort_index(axis=1, ascending=False, inplace=True)
            latex_df.sort_index(axis=0, inplace=True)
            # Column order
            order = ['measured']
            order.extend([replacement_of_characters(approach, replacement) for
                          approach in approach_list if
                          approach not in restriction_list])
            latex_df = latex_df[order]
            filename_table = os.path.join(
                path_latex_tables,
                'annual_energy_approach_{0}_{1}_{2}{3}.tex'.format(
                    case, year, weather_data_name, filename_add_on))
            latex_df.round(2).to_latex(
                buf=filename_table,
                column_format=create_column_format(len(latex_df.columns), 'c'),
                multicolumn_format='c')
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'annual_energy_approach_{0}_{1}_{2}{3}.csv'.format(
                    case, year, weather_data_name, filename_add_on))
            latex_df.to_csv(filename_csv)

    if 'annual_energy_weather' in latex_output:
        for approach in approach_list:
            if approach not in restriction_list:
                latex_df = pd.DataFrame()
                for weather_data_name in weather_data_list:
                    df_part_weather = pd.DataFrame()
                    for outerKey, innerDict in annual_energy_dicts[
                            weather_data_name].items():
                        df_part = pd.DataFrame(
                            {(weather_data_name, innerstKey): [values] for
                             innerKey, innerstDict in innerDict.items() if
                             (innerKey == approach and innerKey not in
                              restriction_list) for
                             innerstKey, values in innerstDict.items()},
                            index=[outerKey.replace('wf_', 'WF ').replace(
                                   '_', ' ')]).round(2)
                        if weather_data_name == weather_data_list[0]:
                            df_part['measured', '[MWh]'] = round(
                                annual_energy_dicts[weather_data_name][
                                    outerKey]['measured_annual_energy'], 2)
                        df_part_weather = pd.concat([df_part_weather, df_part],
                                                    axis=0)
                    latex_df = pd.concat([latex_df, df_part_weather], axis=1)
                # Sort columns and index
                latex_df.sort_index(axis=1, ascending=True, inplace=True)
                latex_df.sort_index(axis=0, inplace=True)
                # Column order
                order = ['measured']
                order.extend(weather_data_list)
                latex_df = latex_df[order]
                filename_table = os.path.join(
                    path_latex_tables,
                    'annual_energy_weather_{0}_{1}_{2}{3}.tex'.format(
                        case, year, approach, filename_add_on))
                latex_df.to_latex(
                    buf=filename_table, column_format=create_column_format(
                        len(latex_df.columns), 'c'), multicolumn_format='c')

    if 'annual_energy_weather_approaches' in latex_output:
        latex_df = pd.DataFrame()
        for weather_data_name in weather_data_list:
            df_part_weather = pd.DataFrame()
            for outerKey, innerDict in annual_energy_dicts[
                    weather_data_name].items():
                df_part = pd.DataFrame(
                    {(innerKey, weather_data_name): [values] for
                     innerKey, innerstDict in innerDict.items() if (
                         innerKey != 'measured_annual_energy' and
                         innerKey not in restriction_list) for
                     innerstKey, values in innerstDict.items() if
                     innerstKey == 'deviation [%]'},
                    index=[outerKey.replace('wf_', 'WF ').replace(
                           '_', ' ')]).round(2)
                df_part_weather = pd.concat([df_part_weather, df_part], axis=0)
            latex_df = pd.concat([latex_df, df_part_weather], axis=1)
        # Sort columns and index
        latex_df.sort_index(axis=1, ascending=True, inplace=True)
        latex_df.sort_index(axis=0, inplace=True)
        # Column order
        latex_df = latex_df[[approach for approach in approach_list if
                             approach not in restriction_list]]
        filename_table = os.path.join(
            path_latex_tables,
            'annual_energy_weather_approaches_{0}_{1}{2}.tex'.format(
                case, year, filename_add_on))
        latex_df.to_latex(
            buf=filename_table, column_format=create_column_format(
                len(latex_df.columns), 'c'), multicolumn_format='c')

    if 'key_figures_approaches' in latex_output:
        if 'wind_speed' in case:
            unit = '[m/s]'
        else:
            unit = '[MW]'
        for weather_data_name in weather_data_list:
            print(weather_data_name)
            latex_df = pd.DataFrame()
            for outerKey, innerDict in val_obj_dict[
                    weather_data_name].items():
                print(outerKey)
                for wf_name in wind_farm_names:
                    if (wf_name not in restriction_list and not
                            (wf_name == 'single_BE' and
                                outerKey == 'monthly') and not
                            (wf_name == 'single')):
                        print(wf_name)
                        df_wf_part = pd.DataFrame()
                        if 'rmse' in key_figures_print:
                            df_part = pd.DataFrame(
                                {('RMSE {}'.format(unit),
                                  replacement_of_characters(innerKey,
                                                            replacement)):
                                 val_obj.rmse for
                                 innerKey, innerstList in innerDict.items() if
                                 innerKey not in restriction_list for
                                 val_obj in innerstList if
                                 val_obj.object_name == wf_name},
                                index=[[wf_name.replace('wf_', 'WF ').replace(
                                    'single_', '').replace('_', ' ')],
                                    [outerKey.replace('_', '-')]])
                            df_wf_part = pd.concat([df_wf_part, df_part],
                                                   axis=1)
                        if 'rmse_normalized' in key_figures_print:
                            df_part = pd.DataFrame(
                                {('RMSE [%]', replacement_of_characters(
                                    innerKey, replacement)):
                                 val_obj.rmse_normalized for
                                 innerKey, innerstList in
                                 innerDict.items() for
                                 val_obj in innerstList if
                                 val_obj.object_name == wf_name},
                                index=[[wf_name.replace('wf_', 'WF ').replace(
                                    'single_', '').replace('_', ' ')],
                                    [outerKey.replace('_', '-')]])
                            df_wf_part = pd.concat([df_wf_part, df_part],
                                                   axis=1)
                        if 'pearson' in key_figures_print:
                            df_part = pd.DataFrame(
                                {('Pearson coefficient',
                                  replacement_of_characters(
                                      innerKey, replacement)):
                                 val_obj.pearson_s_r for
                                 innerKey, innerstList in innerDict.items() for
                                 val_obj in innerstList if
                                 val_obj.object_name == wf_name},
                                index=[[wf_name.replace('wf_', 'WF ').replace(
                                    'single_', '').replace('_', ' ')],
                                    [outerKey.replace('_', '-')]])
                            df_wf_part = pd.concat([df_wf_part, df_part],
                                                   axis=1)
                        if 'mean_bias' in key_figures_print:
                            df_part = pd.DataFrame(
                                {('mean bias {}'.format(unit),
                                  replacement_of_characters(
                                      innerKey, replacement)):
                                 val_obj.mean_bias for
                                 innerKey, innerstList in innerDict.items() for
                                 val_obj in innerstList if
                                 val_obj.object_name == wf_name},
                                index=[[wf_name.replace('wf_', 'WF ').replace(
                                    'single_', '').replace('_', ' ')],
                                    [outerKey.replace('_', '-')]])
                            df_wf_part = pd.concat([df_wf_part, df_part],
                                                   axis=1)
                        if 'standard_deviation' in key_figures_print:
                            df_part = pd.DataFrame(
                                {('std deviation {}'.format(unit),
                                  replacement_of_characters(
                                      innerKey, replacement)):
                                 val_obj.standard_deviation for
                                 innerKey, innerstList in innerDict.items() for
                                 val_obj in innerstList if
                                 val_obj.object_name == wf_name},
                                index=[[wf_name.replace('wf_', 'WF ').replace(
                                    'single_', '').replace('_', ' ')],
                                    [outerKey.replace('_', '-')]])
                            df_wf_part = pd.concat([df_wf_part, df_part],
                                                   axis=1)
                        latex_df = pd.concat([latex_df, df_wf_part])
            # Sort index
            latex_df.sort_index(axis=0, inplace=True)
            # Order by height depending on case
            latex_df = sort_columns_height(latex_df, case)
            filename_table = os.path.join(
                path_latex_tables,
                'key_figures_approaches_{0}_{1}_{2}{3}.tex'.format(
                    case, year, weather_data_name, filename_add_on))
            column_format = create_column_format(
                number_of_columns=(
                    len(val_obj_dict[weather_data_name][
                        output_methods[1]]) * len(key_figures_print)),
                index_columns='ll')
            latex_df.round(2).to_latex(buf=filename_table,
                                       column_format=column_format,
                                       multicolumn_format='c')
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'key_figures_approaches_{0}_{1}_{2}{3}.csv'.format(
                    case, year, weather_data_name, filename_add_on))
            latex_df.to_csv(filename_csv)

# TODO set_names([]) for index names

    if 'key_figures_weather' in latex_output:
        if 'wind_speed' in case:
            unit = '[m/s]'
        else:
            unit = '[MW]'
        for approach in approach_list:
            if approach not in restriction_list:
                latex_df = pd.DataFrame()
                for weather_data_name in weather_data_list:
                    df_part_weather = pd.DataFrame()
                    for outerKey, innerDict in val_obj_dict[
                            weather_data_name].items():
                        if outerKey != 'half_hourly':
                            for wf_name in wind_farm_names:
                                if wf_name not in restriction_list:
                                    df_wf_part = pd.DataFrame()
                                    if 'rmse' in key_figures_print:
                                        df_part = pd.DataFrame(
                                            {('RMSE {}'.format(unit),
                                              weather_data_name):
                                             val_obj.rmse for
                                             innerKey, innerstList in
                                             innerDict.items() for
                                             val_obj in innerstList if
                                             val_obj.object_name == wf_name},
                                            index=[[wf_name.replace(
                                                'wf_', 'WF ').replace(
                                                'single_', '')],
                                                [outerKey.replace('_', '-')]])
                                        df_wf_part = pd.concat(
                                            [df_wf_part, df_part], axis=1)
                                    if 'rmse_normalized' in key_figures_print:
                                        df_part = pd.DataFrame(
                                            {('RMSE [%]',
                                              weather_data_name):
                                             val_obj.rmse_normalized for
                                             innerKey, innerstList in
                                             innerDict.items() for
                                             val_obj in innerstList if
                                             val_obj.object_name == wf_name},
                                            index=[[wf_name.replace(
                                                'wf_', 'WF ').replace(
                                                'single_', '')],
                                                [outerKey.replace('_', '-')]])
                                        df_wf_part = pd.concat(
                                            [df_wf_part, df_part], axis=1)
                                    if 'pearson' in key_figures_print:
                                        df_part = pd.DataFrame(
                                            {('Pearson coeff.',
                                              weather_data_name):
                                             val_obj.pearson_s_r for
                                             innerKey, innerstList in
                                             innerDict.items() for
                                             val_obj in innerstList if
                                             val_obj.object_name == wf_name},
                                            index=[[wf_name.replace(
                                                'wf_', 'WF ').replace(
                                                'single_', '')],
                                                [outerKey.replace('_', '-')]])
                                        df_wf_part = pd.concat(
                                            [df_wf_part, df_part], axis=1)
                                    if 'mean_bias' in key_figures_print:
                                        df_part = pd.DataFrame(
                                            {('mean bias {}'.format(unit),
                                              weather_data_name):
                                             val_obj.mean_bias for
                                             innerKey, innerstList in
                                             innerDict.items() for
                                             val_obj in innerstList if
                                             val_obj.object_name == wf_name},
                                            index=[[wf_name.replace(
                                                'wf_', 'WF ').replace(
                                                'single_', '')],
                                                [outerKey.replace('_', '-')]])
                                        df_wf_part = pd.concat(
                                            [df_wf_part, df_part], axis=1)
                                    if ('standard_deviation' in
                                            key_figures_print):
                                        df_part = pd.DataFrame(
                                            {('std deviation {}'.format(unit),
                                              weather_data_name):
                                             val_obj.standard_deviation for
                                             innerKey, innerstList in
                                             innerDict.items() for
                                             val_obj in innerstList if
                                             val_obj.object_name == wf_name},
                                            index=[[wf_name.replace(
                                                'wf_', 'WF ').replace(
                                                'single_', '')],
                                                [outerKey.replace('_', '-')]])
                                        df_wf_part = pd.concat(
                                            [df_wf_part, df_part], axis=1)
                                    df_part_weather = pd.concat(
                                        [df_part_weather, df_wf_part])
                    latex_df = pd.concat([latex_df, df_part_weather],
                                         axis=1).round(2)
            # Sort columns and index
            columns_names = list(set(latex_df.columns.get_level_values(0)))
            optional_names_order = ['RMSE [m/s]', 'RMSE [%]', 'Pearson coeff.',
                                    'mean bias [m/s]']
            name_order = [name for name in optional_names_order if
                          name in columns_names]
            latex_df = latex_df[name_order]
            latex_df.sort_index(axis=0, inplace=True)
            filename_table = os.path.join(
                path_latex_tables,
                'Key_figures_weather_{0}_{1}_{2}{3}.tex'.format(
                    case, year, approach, filename_add_on))
            column_format = create_column_format(
                number_of_columns=(
                    len(val_obj_dict[weather_data_name][
                        output_methods[1]]) * len(key_figures_print)),
                index_columns='ll')
            latex_df.to_latex(buf=filename_table, column_format=column_format,
                              multicolumn_format='c')

    if 'std_dev_time_series' in latex_output:
        if 'wind_speed' in case:
            unit = '[m/s]'
        else:
            unit = '[MW]'
        for weather_data_name in weather_data_list:
            latex_df = pd.DataFrame()
            for outerKey, innerDict in val_obj_dict[
                    weather_data_name].items():
                for wf_name in wind_farm_names:
                    if wf_name not in restriction_list:
                        df_wf_part = pd.DataFrame(
                            {replacement_of_characters(innerKey, replacement):
                             val_obj.std_dev_sim for
                             innerKey, innerstList in innerDict.items() for
                             val_obj in innerstList if
                             val_obj.object_name == wf_name},
                            index=[[wf_name.replace('wf_', 'WF ').replace(
                                'single_', '').replace('_', ' ')],
                                [outerKey.replace('_', '-')]])
                        # Check weather measured value consistent
                        measured = set(
                            [val_obj.std_dev_val for
                             innerKey, innerstList in innerDict.items() for
                             val_obj in innerstList if
                             val_obj.object_name == wf_name])
                        if len(measured) > 1:
                            raise ValueError(
                                "Standard deviation values of measured time " +
                                "series not consistent.")
                        # Add value to data frame
                        df_wf_part['measured'] = measured
                        latex_df = pd.concat([latex_df, df_wf_part])
            # Sort index
            latex_df.sort_index(axis=0, inplace=True)
            # Order by height depending on case
            latex_df = sort_columns_height(latex_df, case)
            filename_table = os.path.join(
                path_latex_tables,
                'std_dev_time_series_{0}_{1}_{2}{3}.tex'.format(
                    case, year, weather_data_name, filename_add_on))
            column_format = create_column_format(
                number_of_columns=(
                    len(val_obj_dict[weather_data_name][
                        output_methods[1]]) * len(key_figures_print)),
                index_columns='ll')
            latex_df.round(2).to_latex(buf=filename_table,
                                       column_format=column_format,
                                       multicolumn_format='c')
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'std_dev_time_series_{0}_{1}_{2}{3}.csv'.format(
                    case, year, weather_data_name, filename_add_on))
            latex_df.to_csv(filename_csv)


def sort_columns_height(df, case):
    if (case == 'wind_speed_1' or case == 'wind_speed_2' or
            case == 'wind_speed_3'):
        sorted_df = pd.DataFrame()
        column_names_1 = list(pd.Series([item[0] for
                                         item in list(df)]).drop_duplicates())
        for col_name in column_names_1:
            df_part = df[col_name]
            df_part = df_part[[
                '{} {}'.format(list(df_part)[0].split(' ')[0], height) for
                height in ['100', '80', '10']]]
            df_part.columns = [[col_name, col_name, col_name], df_part.columns]
            sorted_df = pd.concat([sorted_df, df_part], axis=1)
    else:
        sorted_df = df
    return sorted_df


def mean_figure_table(latex_tables_folder, case, figure):
    """

    """
    weather_data_list = ['MERRA', 'open_FRED']
    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     latex_tables_folder)
    years = [2015, 2016]
    resolutions = ['hourly', 'monthly']
    mean_rmse_df_years = pd.DataFrame()
    for year in years:
        mean_rmse_df_weather = pd.DataFrame()
        for weather_data_name in weather_data_list:
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'key_figures_approaches_{0}_{1}_{2}.csv'.format(
                    case, year, weather_data_name))
            latex_df = pd.read_csv(filename_csv, index_col=[0, 1],
                                   header=[0, 1])
            mean_rmse_df = pd.DataFrame()
            rmse_df = latex_df[figure]
            for resolution in resolutions:
                mean_rmse_df['{} {}'.format(resolution, year)] = rmse_df.iloc[
                    rmse_df.index.get_level_values(1) == resolution].mean()
            mean_rmse_df = mean_rmse_df.transpose()
            if case == 'power_output_1':
                mean_rmse_df.columns = [
                    mean_rmse_df.columns,
                    ['-curve', weather_data_name, '-curve', weather_data_name]]
            else:
                mean_rmse_df.columns = [
                    mean_rmse_df.columns,
                    ['-curve', weather_data_name, '-curve']]
            mean_rmse_df_weather = pd.concat([mean_rmse_df_weather,
                                              mean_rmse_df], axis=1)
            if weather_data_name != weather_data_list[-1]:
                mean_rmse_df_weather.drop(['P', 'Cp'], axis=1,
                                          inplace=True)
            else:
                mean_rmse_df_weather.sort_index(axis=1, inplace=True)
        mean_rmse_df_years = pd.concat([mean_rmse_df_years,
                                        mean_rmse_df_weather], axis=0)
    filename_table = os.path.join(
        path_latex_tables,
        'mean_{}_weather_{}.tex'.format(figure.replace(' ', '_').replace(
            '%', 'percent'), case))
    column_format = create_column_format(
        number_of_columns=len(list(mean_rmse_df_years)),
        index_columns='l')
    # Mean RMSE in kW
    if figure == 'RMSE [MW]':
        mean_rmse_df_years = mean_rmse_df_years * 1000
    mean_rmse_df_years.round(2).to_latex(
        buf=filename_table, column_format=column_format,
        multicolumn_format='c')


def mean_std_dev_smoothing_2(latex_tables_folder):
    weather_data_list = ['MERRA', 'open_FRED']
    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     latex_tables_folder)
    years = [2015, 2016]
    counter = 0

    for year in years:
        for weather_data_name in weather_data_list:
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'std_dev_time_series_smoothing_2_{0}_{1}.csv'.format(
                    year, weather_data_name))
            latex_df = pd.read_csv(filename_csv, index_col=[0, 1], header=0)
            raw_columns = list(latex_df)
            latex_df.rename(columns={col: col + ' {} {}'.format(
                year, weather_data_name) for col in latex_df.columns},
                            inplace=True)
            if counter == 0:
                dfs_by_column_list = [latex_df[[col]] for
                                      col in list(latex_df)]
            else:
                dfs_by_column_list = [pd.concat([dfs_by_column_list[i],
                                                 latex_df[[col]]], axis=1) for
                                      i, col in zip(
                        range(len(list(latex_df))), list(latex_df))]
            counter += 1
    # Average each row of each data frame and concat again
    joined_dfs = [pd.DataFrame(df.mean(axis=1)) for df in dfs_by_column_list]
    joined_dfs = [df.rename(columns={list(df)[0]: new_col}) for
                  df, new_col in zip(joined_dfs, raw_columns)]
    mean_std_dev_df = pd.concat(joined_dfs, axis=1)
    mean_std_dev_df.index.set_names(['name', 'resolution'], inplace=True)
    mean_std_dev_df.reset_index(inplace=True)
    first_columns = ['Weather data', 'Temporal']
    first_columns.extend(['Standard deviation in MW' for i in range(4)])
    mean_std_dev_df.columns = [col.replace(
        'aggregation', 'Aggregation').replace('mea', 'Mea') for col in mean_std_dev_df.columns]
    mean_std_dev_df.columns = [first_columns, mean_std_dev_df.columns]
    filename_table = os.path.join(
        path_latex_tables,
        'mean_std_dev_smoothing_2.tex')
    column_format = create_column_format(
        number_of_columns=len(list(mean_std_dev_df)), index_columns='ll')
    mean_std_dev_df.round(2).to_latex(
        buf=filename_table, column_format=column_format,
        multicolumn_format='c', index=False)
    filename_csv = os.path.join(
        os.path.dirname(__file__), 'csv_for_plots',
        'mean_std_dev_smoothing_2.csv')
    mean_std_dev_df.to_csv(filename_csv, index=False)


def mean_annual_energy_deviation_tables(latex_tables_folder):
    """
    For case == power_output_1

    """
    weather_data_list = ['MERRA', 'open_FRED']
    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     latex_tables_folder)
    years = [2015, 2016]
    resolutions = ['hourly', 'monthly']
    mean_deviaton_df_years = pd.DataFrame()
    for year in years:
        mean_deviaton_df_weather = pd.DataFrame()
        for weather_data_name in weather_data_list:
            filename_csv = os.path.join(
                os.path.dirname(__file__), 'csv_for_plots',
                'annual_energy_approach_{0}_{1}_{2}.csv'.format(
                    'power_output_1', year, weather_data_name))
            latex_df = pd.read_csv(filename_csv, index_col=[0],
                                   header=[0, 1])
            deviation_df = latex_df.drop('measured', axis=1)
            deviation_df.drop('[MWh]', axis=1, level=1, inplace=True)
            deviation_df.columns = deviation_df.columns.droplevel(1)
            mean_deviation_df = pd.DataFrame()
            mean_deviation_df['{}'.format(year)] = deviation_df.mean()
            mean_deviation_df = mean_deviation_df.transpose()
            mean_deviation_df.columns = [
                mean_deviation_df.columns,
                ['-curve', '-curve', weather_data_name, weather_data_name]]
            mean_deviaton_df_weather = pd.concat([mean_deviaton_df_weather,
                                                  mean_deviation_df], axis=1)
            if weather_data_name != weather_data_list[-1]:
                mean_deviaton_df_weather.drop(['P', 'Cp'], axis=1,
                                              inplace=True)
            else:
                mean_deviaton_df_weather.sort_index(axis=1, inplace=True)
        mean_deviaton_df_years = pd.concat([mean_deviaton_df_years,
                                            mean_deviaton_df_weather], axis=0)
    filename_table = os.path.join(
        path_latex_tables,
        'mean_deviation_weather_power_output_1.tex')
    column_format = create_column_format(
        number_of_columns=len(list(mean_deviaton_df_years)),
        index_columns='l')
    mean_deviaton_df_years.round(2).to_latex(
        buf=filename_table, column_format=column_format,
        multicolumn_format='c')


def concat_std_dev_tables_smoothing_1(latex_tables_folder):
    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     latex_tables_folder)
    weather_data_names = ['MERRA', 'open_FRED']
    std_dev_df = pd.DataFrame()
    for weather_data_name in weather_data_names:
        filename_csv = os.path.join(
                        os.path.dirname(__file__), 'csv_for_plots',
                        'std_dev_time_series_smoothing_1_2016_{}.csv'.format(
                            weather_data_name))
        latex_df = pd.read_csv(filename_csv, index_col=[0, 1], header=0).drop(
            'measured', axis=1)
        if weather_data_name == 'MERRA':
            latex_df.index.set_levels([weather_data_name, weather_data_name],
                                      level=0, inplace=True)
        if weather_data_name == 'open_FRED':
            latex_df.index.set_levels([
                weather_data_name, weather_data_name, weather_data_name],
                level=0, inplace=True)
        latex_df.index.set_names(['name', 'resolution'], inplace=True)
        latex_df.reset_index(inplace=True)
        first_columns = ['Weather data', 'Temporal']
        first_columns.extend(['Standard deviation in MW' for i in range(2)])
        latex_df.columns = [col.replace('turb', 'Turb').replace(
            'farm', 'Farm') for col in latex_df.columns]
        latex_df.columns = [first_columns, latex_df.columns]
        std_dev_df = pd.concat([std_dev_df, latex_df], axis=0)
    filename_table = os.path.join(
        path_latex_tables,
        'std_dev_smoothing_1.tex')
    column_format = create_column_format(
        number_of_columns=len(list(std_dev_df)), index_columns='ll')
    std_dev_df.round(2).to_latex(
        buf=filename_table, column_format=column_format,
        multicolumn_format='c', index=False)


def concat_key_figures_tables_smoothing_1(latex_tables_folder):
    path_latex_tables = os.path.join(os.path.dirname(__file__),
                                     latex_tables_folder)
    weather_data_names = ['MERRA', 'open_FRED']
    std_dev_df = pd.DataFrame()
    for weather_data_name in weather_data_names:
        filename_csv = os.path.join(
                        os.path.dirname(__file__), 'csv_for_plots',
                        'key_figures_approaches_smoothing_1_2016_{}.csv'.format(
                            weather_data_name))
        latex_df = pd.read_csv(filename_csv, index_col=[0, 1], header=[0, 1])
        if weather_data_name == 'MERRA':
            latex_df.index.set_levels([weather_data_name, weather_data_name],
                                      level=0, inplace=True)
        if weather_data_name == 'open_FRED':
            latex_df.index.set_levels([
                weather_data_name, weather_data_name, weather_data_name],
                level=0, inplace=True)
        latex_df.index.set_names(['Weather data', 'Temporal'], inplace=True)
        latex_df.reset_index(inplace=True)
        second_columns = ['name', 'resolution']
        second_columns.extend(latex_df.columns.get_level_values(1)[2:])
        second_columns = [col.replace('turb', 'Turb').replace(
            'farm', 'Farm') for col in second_columns]
        latex_df.columns = [latex_df.columns.get_level_values(0), second_columns]
        std_dev_df = pd.concat([std_dev_df, latex_df], axis=0)
    filename_table = os.path.join(
        path_latex_tables,
        'key_figures_smoothing_1.tex')
    column_format = create_column_format(
        number_of_columns=len(list(std_dev_df)), index_columns='ll')
    std_dev_df.round(2).to_latex(
        buf=filename_table, column_format=column_format,
        multicolumn_format='c', index=False)


def carry_out_mean_figure_tables(latex_tables_folder, cases):
    figures = ['RMSE [MW]', 'RMSE [%]']
    for figure in figures:
        for case in cases:
            mean_figure_table(latex_tables_folder, case, figure=figure)


if __name__ == "__main__":
    latex_tables_folder = ('../../../User-Shares/Masterarbeit/Latex/Tables/' +
                           'automatic/')
    mean_annual_energy_deviation_tables(latex_tables_folder)
    concat_std_dev_tables_smoothing_1(latex_tables_folder)
    concat_key_figures_tables_smoothing_1(latex_tables_folder)
    mean_std_dev_smoothing_2(latex_tables_folder)
    cases = ['power_output_1', 'single_turbine_1']
    carry_out_mean_figure_tables(latex_tables_folder, cases)
