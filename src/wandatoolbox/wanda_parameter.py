import shutil
import pywanda
import pandas as pd
import numpy as np
import multiprocessing as mp
import time
import queue
import yaml
from wanda_plot import plot, PlotTimeseries, PlotRoute, PlotText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileMerger
import collections
import os


# routine to merge all files in the input lis into the file in the output.
def merge_pdf(input_files, output_file):
    merger = PdfFileMerger()
    for pdf in input_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()


def parse_figures(series):
    figure_dict = {}
    for i in range(len(series['fig'])):
        times = []
        if 'times' in series:
            index = series.columns.get_loc('times')
            times.append(series.values[i][index])
            index += 1
            while series.columns[index][0:7] == 'Unnamed':
                if series.values[i][index] == series.values[i][index]:  #check for nan
                    times.append(series.values[i][index])
                index += 1
        if not (series['fig'][i] in figure_dict):
            x_axis = (series['Xmin'][i], series['Xtick'][i], series['Xmax'][i], series['Xscale'][i])
            y_axis = (series['Ymin'][i], series['Ytick'][i], series['Ymax'][i], series['Yscale'][i])
            figure_dict[series['fig'][i]] = {series['plot'][i]: FigureDate(series['title'][i], series['Xlabel'][i],
                                                                           series['Ylabel'][i], x_axis, y_axis,
                                                                           times)}
        elif not (series['plot'][i] in figure_dict[series['fig'][i]]):
            x_axis = (series['Xmin'][i], series['Xtick'][i], series['Xmax'][i], series['Xscale'][i])
            y_axis = (series['Ymin'][i], series['Ytick'][i], series['Ymax'][i], series['Yscale'][i])
            figure_dict[series['fig'][i]][series['plot'][i]] = FigureDate(series['title'][i], series['Xlabel'][i],
                                                                          series['Ylabel'][i], x_axis, y_axis, times)
    return figure_dict


def parse_text_data(point_data):
    point_data_parsed = {}
    for fig, plot_num, x, y, text, dx, dy in zip(point_data['fig'], point_data['plot'], point_data['x'],
                                                 point_data['y'], point_data['text'], point_data['dx'],
                                                 point_data['dy']):
        if fig in point_data_parsed:
            if plot_num in point_data_parsed[fig]:
                point_data_parsed[fig][plot_num].append([x, y, dx, dy, text])
            else:
                point_data_parsed[fig][plot_num] = [[x, y, dx, dy, text]]
        else:
            point_data_parsed[fig] = {plot_num: [[x, y, dx, dy, text]]}
    return point_data_parsed

# routine to perform the work.
def do_work(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.                '''
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:
            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            print(task)
            result = task()
            tasks_that_are_done.put(result)
            time.sleep(0.5)
    return


# class which holds the value for one parameter this cna be input or output
class WandaParameter:
    def __init__(self, wanda_component, wanda_property, value=None, output=None, fig_number=None, plot_number=None,
                 legend=None, direction=None):
        self.wanda_component = wanda_component.strip()
        self.wanda_property = wanda_property.strip()
        self.value = value
        self.output = output
        self.result = None
        self.fig_number = fig_number
        self.plot_number = plot_number
        self.legend = None
        self.direction = direction
        # check if legend is NAN
        if legend == legend:
            self.legend = legend

    def set_parameter(self, model):
        if self.value is not None:
            wanda_properties = self.get_properties(model)
            for wanda_property in wanda_properties:
                if type(wanda_property) == pywanda.WandaProperty:
                    wanda_property.set_scalar(self.value / wanda_property.get_unit_factor())
                else:
                    wanda_property(self.value)

    def get_wanda_property(self, wanda_item):
        if wanda_item.contains_property(self.wanda_property):
            return wanda_item.get_property(self.wanda_property)
        elif self.wanda_property.lower() == "Disuse".lower():
            return wanda_item.set_disused
        #raise Exception(self.wanda_property + " not in " + wanda_item.get_complete_name_spec())

    def get_properties(self, model):
        properties = []
        if self.wanda_component.lower() == 'GENERAL'.lower():
            properties.append(model.get_property(self.wanda_property))
        else:
            comps = model.get_components_with_keyword(self.wanda_component)
            if len(comps) != 0:
                for comp in comps:
                    prop = self.get_wanda_property(comp)
                    if prop is not None:
                        properties.append(prop)
            elif model.component_exists(self.wanda_component):
                comp = model.get_component(self.wanda_component)
                prop = self.get_wanda_property(comp)
                if prop is not None:
                    properties.append(prop)

            nodes = model.get_nodes_with_keyword(self.wanda_component)
            if len(nodes) != 0:
                for node in nodes:
                    properties.append(self.get_wanda_property(node))
            elif model.node_exists(self.wanda_component):
                node = model.get_node(self.wanda_component)
                prop = self.get_wanda_property(node)
                if prop is not None:
                    properties.append(prop)

            sig_lines = model.get_signal_lines_with_keyword(self.wanda_component)
            if len(sig_lines) != 0:
                for sig_line in sig_lines:
                    properties.append(self.get_wanda_property(sig_line))
            elif model.sig_line_exists(self.wanda_component):
                sig_line = model.get_signal_line(self.wanda_component)
                properties.append(self.get_wanda_property(sig_line))
        if not properties:
            raise Exception(self.wanda_property + " does not exist for " + self.wanda_component)
        return properties

    def get_result_extreme(self, model):
        if self.output is not None:
            wanda_properties = self.get_properties(model)
            if not wanda_properties:
                self.result = -999.0
            if self.output.lower() == 'Min'.lower():
                min_val = []
                for wanda_property in wanda_properties:
                    min_val.append(wanda_property.get_extr_min())
                    self.result = min(min_val) * wanda_property.get_unit_factor()
            elif self.output.lower() == 'Max'.lower():
                max_val = []
                for wanda_property in wanda_properties:
                    if not(wanda_property.is_disused()):
                        max_val.append(wanda_property.get_extr_max())
                    else:
                        max_val.append(-np.inf)
                    self.result = max(max_val) * wanda_property.get_unit_factor()
        return self.result

    def get_series(self, model):
        self.result = []
        if self.output is not None:
            if self.output == "Series":
                wanda_properties = self.get_properties(model)
                for wanda_property in wanda_properties:
                    if wanda_property is not None:
                        series = [x * wanda_property.get_unit_factor() for x in wanda_property.get_series()]
                        self.result.append(series)
        return self.result

    def create_graphs(self, model):
        with PdfPages(f'Document.pdf') as pdf:
            plot_time = [PlotTimeseries([(self.wanda_component, self.wanda_property, self.wanda_component)],
                                        title='test', xlabel='test2', ylabel='test2')]
            plot(model, plot_time, title='test', case_title='case_title', case_description='case_description',
                 proj_number='proj_number', section_name='section_name', fig_name='fig_name')
            pdf.savefig()
            plt.close()


# simple class to store some figure data
class FigureDate:
    def __init__(self, title, x_label, y_label, x_axis, y_axis, times):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.times = times


# class which contains all input and output parameters of one scenario
class WandaScenario:
    def __init__(self, model, wanda_bin, name, figure_data, plot_data, text_data, only_figure=False):
        self.name = name
        self.model_file = model[:-4] + "_" + name + ".wdi"
        self.model_dir = os.path.split(model)[0]
        self.only_figures = only_figure
        if not(os.path.exists(self.model_dir + '\\figures\\')):
            os.mkdir(self.model_dir + '\\figures\\')
        if not self.only_figures:
            shutil.copyfile(model, self.model_file)
        self.bin = wanda_bin
        self.parameters = []
        self.output = []
        self.figure_data = figure_data
        self.plot_data = plot_data
        self.text_data = text_data

    def add_parameter(self, component_name, property_name, value):
        self.parameters.append(WandaParameter(component_name, property_name, value=value))

    def add_output(self, component_name, property_name, kind, fig_number=None, plot_number=None, legend=None,
                   direction=None):
        self.output.append(WandaParameter(component_name, property_name, output=kind, fig_number=fig_number,
                                          plot_number=plot_number, legend=legend, direction=direction))

    def run_scenario(self):
        model = pywanda.WandaModel(self.model_file, self.bin)
        if self.only_figures:
            model.reload_output()
        else:
            for parameter in self.parameters:
                parameter.set_parameter(model)
            model.save_model_input()
            model.run_steady()
            model.run_unsteady()
        result = self.get_results(model)
        self.create_graphs(model)
        model.close()
        return result

    def get_results(self, model):
        results = [self.name]
        for output in self.output:
            if output.output == "Route":
                continue
            result = output.get_result_extreme(model)
            if result is not None:
                results.append(result)
            output.get_series(model)
        return results

    def create_graphs(self, model):
        figures = {}
        for output in self.output:
            if output.output == "Series":
                tuple_data = (output.wanda_component, output.wanda_property, output.legend)
            elif output.output == "Route":
                comps, directions = model.get_route(output.wanda_component)
                if sum(directions) < 0:
                    # flip direction
                    comps.reverse()
                    directions.reverse()
                    directions = [-1 * x for x in directions]
                if output.direction == -1:
                    # flip direction
                    comps.reverse()
                    directions.reverse()
                    directions = [-1 * x for x in directions]
                pipes = []
                pipes_dir = []
                for p, direction in zip(comps, directions):
                    if p.is_pipe():
                        pipes.append(p)
                        pipes_dir.append(direction)
                tuple_data = (pipes, pipes_dir, output.wanda_property)
            else:
                continue
            if output.fig_number in figures:
                if output.plot_number in figures[output.fig_number]:
                    figures[output.fig_number][output.plot_number].append(tuple_data)
                else:
                    figures[output.fig_number][output.plot_number] = [tuple_data]
            else:
                figures[output.fig_number] = {output.plot_number: [tuple_data]}
        # creation of plot object and then plotting
        number = int(self.plot_data["Case number"])
        pdf_file = self.model_dir + '\\figures\\' + self.plot_data["Appendix"] + "_" + f"{number:03}" + '.pdf'
        order_figures = collections.OrderedDict(sorted(figures.items()))
        with PdfPages(pdf_file) as pdf:
            for figure in order_figures.keys():
                plot_figures = []
                for plotter in figures[figure].keys():
                    if self.figure_data[figure][plotter].times:
                        text_data = []
                        if figure in self.text_data:
                            if plotter in self.text_data[figure]:
                                text_data = self.text_data[figure][plotter]
                        plot_figures.append(PlotRoute(figures[figure][plotter][0][0], figures[figure][plotter][0][1],
                                                      figures[figure][plotter][0][2],
                                                      self.figure_data[figure][plotter].times,
                                                      title=self.figure_data[figure][plotter].title,
                                                      xlabel=self.figure_data[figure][plotter].x_label,
                                                      ylabel=self.figure_data[figure][plotter].y_label,
                                                      plot_elevation=figures[figure][plotter][0][2].lower() == 'head',
                                                      plot_text=text_data))
                    else:
                        plot_figures.append(PlotTimeseries(figures[figure][plotter],
                                                           title=self.figure_data[figure][plotter].title,
                                                           xlabel=self.figure_data[figure][plotter].x_label,
                                                           ylabel=self.figure_data[figure][plotter].y_label))
                date = None
                if "Date" in self.plot_data:
                    date = self.plot_data["Date"]
                plot(model, plot_figures,
                     title=self.plot_data["Description"],
                     case_title=self.plot_data["Case description"],
                     case_description=self.plot_data["Extra description"],
                     proj_number=self.plot_data["Project number"],
                     section_name='Chapter ' + str(self.plot_data["Chapter"]),
                     date=date,
                     #fig_name='Fig ' + self.plot_data["Appendix"] + '.' + f"{number:03}" + figure)
                     fig_name=self.plot_data["Appendix"] + '.' + f"{number:03}" + figure)
                pdf.savefig()
                plt.close()


# class which holds all scenarios for scenario run can be used to run the case in parallel adn get the output.
# Plotting is also possible
class WandaParameterScript:
    def __init__(self, wanda_model, wanda_bin, excel_file, only_figures=False):
        self.wanda_model = wanda_model
        self.model_dir = os.path.split(wanda_model)[0]
        self.wanda_bin = wanda_bin
        self.excel_file = excel_file
        self.scenarios = []
        self.output_component = []
        self.output_properties = []
        self.output_value = []
        self.appendix = {}
        self.output_filled = False
        self.only_figures = only_figures

    def parse_excel_file(self):
        cols = pd.read_excel(self.excel_file, "Cases", header=None,nrows=1).values[0]
        input_data = pd.read_excel(self.excel_file, "Cases", header=None, skiprows=1)
        input_data.columns = cols
        output = pd.read_excel(self.excel_file, "Output")
        series = pd.read_excel(self.excel_file, 'Tplots')
        routes = pd.read_excel(self.excel_file, "Rplots")
        route_points = pd.read_excel(self.excel_file, "route_points")
        figures = parse_figures(series)
        figures.update(parse_figures(routes))
        if route_points.empty:
            text_data = []
        else:
            text_data = parse_text_data(route_points)
        column_start = input_data.columns.get_loc("Name") + 1
        for i in range(len(input_data.values)):
            # check if there number is a Nan, this means the row is not used and should be skipped.
            if input_data['Number'][i] != input_data['Number'][i]:
                continue
            # checking if the row is included or not
            if input_data['Include'][i] != 1:
                continue
            directions = np.ones(len(routes['name'])).tolist()
            if 'Direction' in routes:
                directions = routes['Direction']

            number = int(input_data['Number'][i])
            pdf_file = self.model_dir + '\\figures\\' + input_data['Appendix'][i] + "_" + f"{number:03}" + '.pdf'
            if input_data['Appendix'][i] in self.appendix:
                self.appendix[input_data['Appendix'][i]].append(pdf_file)
            else:
                self.appendix[input_data['Appendix'][i]] = [pdf_file]
            plot_data = {"Description": input_data["Description"][0], "Project number": input_data["Include"][0],
                         "Case description": input_data["Description"][i], "Extra description": input_data["Extra"][i],
                         "Appendix": input_data["Appendix"][i], "Chapter": input_data["Chapter"][i],
                         "Case number": input_data["Number"][i], "Date": input_data["Date"][i]}
            self.scenarios.append(WandaScenario(self.wanda_model, self.wanda_bin, input_data['Name'][i],
                                                figures, plot_data, text_data, self.only_figures))
            # looping over all parameters and adding them to the scenario
            for j in range(column_start, len(input_data.axes[1])):
                self.scenarios[-1].add_parameter(input_data.axes[1][j], input_data.iloc[0][j],
                                                 input_data.iloc[i][j])
            for j in range(0, len(output.values)):
                if not self.output_filled:
                    self.output_component.append(output.values[j][0])
                    self.output_properties.append(output.values[j][1])
                    self.output_value.append(output.values[j][2])
                self.scenarios[-1].add_output(output.values[j][0], output.values[j][1], output.values[j][2])
            for comp, prop, fig_number, plot_number, legend in zip(series['name'], series['property'],
                                                                   series['fig'], series['plot'], series['Legend']):
                self.scenarios[-1].add_output(comp, prop, 'Series', fig_number, plot_number, legend)
            for comp, prop, fig_number, plot_number, legend, direction in zip(routes['name'], routes['property'],
                                                                   routes['fig'], routes['plot'], routes['Legend'],
                                                                   directions):
                self.scenarios[-1].add_output(comp, prop, 'Route', fig_number, plot_number, legend, direction=direction)
            self.output_filled = True

    def run_scenarios(self, n_workers):
        number_of_processes = n_workers
        tasks_to_accomplish = mp.Queue()
        tasks_that_are_done = mp.Queue()
        processes = []
        for scenario in self.scenarios:
            tasks_to_accomplish.put(scenario.run_scenario)
        # creating processes
        for w in range(number_of_processes + 1):
            p = mp.Process(target=do_work, args=(tasks_to_accomplish, tasks_that_are_done))
            processes.append(p)
            p.start()
        # completing process
        print("waiting for processes to finish")
        for p in processes:
            p.join()
        # print the output
        result = []
        while not tasks_that_are_done.empty():
            res = tasks_that_are_done.get()
            result.append(res)
        self.output_component.insert(0, "Scenario")
        self.output_properties.insert(0, "Name")
        self.output_value.insert(0, " ")
        columns = pd.MultiIndex.from_tuples(zip(self.output_component, self.output_properties, self.output_value))
        frame = pd.DataFrame(result, columns=columns)
        frame.to_excel(self.wanda_model[:-3] + "xlsx")
        # combine pdfs into ond pdf.
        for appendix in self.appendix:
            merge_pdf(self.appendix[appendix], self.model_dir + '\\figures\\' + appendix + '.pdf')


def main(scenario, only_output):
    #
    #config_file_list = []
    #if (scenario == 'Phase 1a') or (scenario == 'All'):
    #    config_file_list.append(r'd:\akzo\model\V4\Sim_1A\config.yml')
    #elif (scenario == 'Phase 1b') or (scenario == 'All'):
    #    config_file_list.append(r'd:\akzo\model\V4\Sim_1B\config.yml')
    #elif (scenario == 'Phase 2') or (scenario == 'All'):
    #    config_file_list.append(r'd:\akzo\model\V4\Sim_2\config.yml')
    #elif (scenario == 'Phase 3') or (scenario == 'All'):
    #    config_file_list.append(r'd:\akzo\model\V4\Sim_3\config.yml')
    #elif scenario == 'Steady':
    #    config_file_list.append(r'd:\akzo\model\V4\config.yml')
    #else:
    #    raise Exception(scenario + ' not recognized')

    #for config_file in config_file_list:
    config_file = r'd:\work\11203980-Musaimeer\forced_flow\config.yml'
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)

    wanda_bin = cfg['General']['Wanda-bin-directory']
    wanda_model = cfg['parameterscript']['wanda-model']
    excel_file = cfg['parameterscript']['excel_sheet']
    nop = cfg['General']['number_of_processes']
    para = WandaParameterScript(wanda_model, wanda_bin, excel_file, only_output)
    para.parse_excel_file()
    para.scenarios[0].run_scenario()
    #para.run_scenarios(nop)


if __name__ == '__main__':
    scenario = 'Steady'
    only_output = False

    main(scenario, only_output)
