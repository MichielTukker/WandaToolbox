# -*- coding: utf-8 -*-
"""
This is a somewhat more extensive example showing Monte Carlo simulations with Wanda
This also shows how you can run Wanda cases in parallel by using the multiprocessing features in python
"""

import csv
import multiprocessing as mp
import os
import pywanda as pw
import random
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging


class MonteCarloInputProperty:
    def __init__(self, comp_name, prop_name, min_val=0.0, max_val=0.0, dist_type="Empty", keyword=False):
        self.wanda_prop = []
        self.prop_name = prop_name
        self.comp_name = comp_name
        self.min_val = min_val
        self.max_val = max_val
        self.dist_type = dist_type
        self.is_initialized = False
        self.is_keyword = keyword
        self.results = []

    def initialize_property(self, model):
        if self.comp_name == "GENERAL":
            # it is a general property(e.g. density, viscosity)
            self.wanda_prop.append(model.get_property(self.prop_name))
        else:
            if self.is_keyword:
                comps = model.get_components_with_keyword(self.comp_name)  # getting all components with a given keyword
                for comp in comps:
                    # check if the component has the property, otherwise the component is skipped
                    if comp.contains_property(self.prop_name):
                        self.wanda_prop.append(comp.get_property(self.prop_name))
            else:
                self.wanda_prop.append(model.get_component(self.comp_name).get_property(self.prop_name))
        self.is_initialized = True

    def update(self, model):
        if not self.is_initialized:
            self.initialize_property(model)
        if self.dist_type == "uniform":
            value = random.uniform(self.min_val, self.max_val)
            for prop in self.wanda_prop:
                prop.set_scalar(value)
        elif self.dist_type == "normal":
            value = random.gauss(self.min_val, self.max_val)
            for prop in self.wanda_prop:
                prop.set_scalar(value)
        else:
            value = random.randint(self.min_val, self.max_val)
            for prop in self.wanda_prop:
                prop.set_scalar(value)


class MonteCarloOutputProperty:
    def __init__(self, comp_name, prop_name, keyword=False, extreme='MIN'):
        self.wanda_prop = []
        self.prop_name = prop_name
        self.comp_name = comp_name
        self.is_initialized = False
        self.is_keyword = keyword
        self.extreme = extreme
        self.results = []

    def initialize_property(self, model):
        if self.comp_name == "GENERAL":
            # it is a general property(e.g. density, viscosity)
            self.wanda_prop.append(model.get_property(self.prop_name))
        else:
            if self.is_keyword:
                comps = model.get_components_with_keyword(self.comp_name)  # getting all components with a given keyword
                for comp in comps:
                    # check if the component has the property, otherwise the component is skipped
                    if comp.contains_property(self.prop_name):
                        self.wanda_prop.append(comp.get_property(self.prop_name))
            else:
                self.wanda_prop.append(model.get_component(self.comp_name).get_property(self.prop_name))
        self.is_initialized = True

    def get_extreme(self, model):
        if self.extreme == 'MIN':
            return self.get_min(model)
        else:
            return self.get_max(model)

    def get_max(self, model):
        if not self.is_initialized:
            self.initialize_property(model)
        result = []
        unit_factor = 1.0
        for prop in self.wanda_prop:
            unit_factor = prop.get_unit_factor()
            if prop.get_number_of_elements() > 1:
                result.append(max(prop.get_extr_max_pipe()))
            else:
                result.append(prop.get_extr_max())
        return max(result) * unit_factor

    def get_min(self, model):
        if not self.is_initialized:
            self.initialize_property(model)
        result = []
        unit_factor = 1.0
        for prop in self.wanda_prop:
            unit_factor = prop.get_unit_factor()
            if prop.get_number_of_elements() > 1:
                result.append(min(prop.get_extr_min_pipe()))
            else:
                result.append(prop.get_extr_min())
        return min(result) * unit_factor

    def get_results(self):
        return list(self.results)


def worker(n_runs, wandacase, working_directory, parameters, outputs, worker_id):
    # Every process gets its own Wandacase and Wandabin
    wancacase_directory, casename = os.path.split(wandacase)
    dst = os.path.join(working_directory, str(worker_id), casename)
    wandabin = os.path.join(working_directory, str(worker_id), "bin")
    model = pw.WandaModel(str(dst), str(wandabin + "\\"))

    results = []
    for i in range(n_runs):
        run_id = (n_runs * worker_id) + i
        # if(run_id == None):
        #     break
        print("Worker #" + str(worker_id) + " running task ID: " + str(run_id))
        for para in parameters:
            para.update(model)
        model.save_model_input()
        try:
            model.run_steady()
        except Exception as inst:
            print("Error in running steady thread " + str(worker_id))
            print(inst)
            break
        try:
            model.run_unsteady()
        except Exception as inst:
            print("Error in running unsteady thread " + str(worker_id))
            print(inst)
            break
        model.reload_input()
        model.reload_output()
        extreme_values = []
        for output in outputs:
            extreme_values.append(output.get_extreme(model))
        results.append(extreme_values)
    model.close()
    return results


class WandaMonteCarlo:
    def __init__(self, wanda_model, input_parameters, output_parameters, nruns=25, n_workers=None, work_directory=None):
        self.wanda_model = wanda_model
        self.inputs = input_parameters
        self.outputs = output_parameters
        self.n_runs = nruns
        self.df = pd.DataFrame(columns=None)
        if (n_workers == None):
            self.n_workers = mp.cpu_count()
        else:
            self.n_workers = n_workers
        if work_directory == None:
            self.work_directory = os.getcwd()
        else:
            if not os.path.isdir(work_directory):
                raise NotADirectoryError
            self.work_directory = work_directory

    def run(self, n_workers=None):
        # Todo self.work_directory integreren in runs
        # Todo Logging

        logger = logging.getLogger(__name__)
        if n_workers != None:
            self.n_workers = n_workers
        case_path = self.wanda_model.get_case_path()
        wanda_bin = self.wanda_model.get_wandabin()
        case_directory, case_name = os.path.split(case_path)
        for i in range(0, self.n_workers):
            if os.path.isdir(os.path.join(self.work_directory, str(i))):
                shutil.rmtree(os.path.join(self.work_directory, str(i)))  # delete directory if it already exists
            os.mkdir(str(i))
            dst = os.path.join(self.work_directory, str(i), case_name)
            shutil.copyfile(case_path, dst)
            shutil.copytree(wanda_bin, os.path.join(self.work_directory, str(i), "bin"))

        logger.debug("Starting workers...")
        # all_results = worker(self.n_runs, case_name, self.work_directory, self.inputs, self.outputs, 0)
        pool = mp.Pool(self.n_workers)
        output = [pool.apply_async(worker, args=(self.n_runs, case_name, self.work_directory,
                                                 self.inputs, self.outputs, worker_id))
                  for worker_id in range(0, self.n_workers)]
        pool.close()
        pool.join()
        logger.debug("workers have finished, generating output")

        # you need to transport the output data to the output objects manually, this cannot be transferred easily over the
        # Multi-process boundary
        all_results = [res for results in output for res in results.get()]
        for res in all_results:
            for i in range(len(res)):
                self.outputs[i].results.append(res[i])

        for outp in self.outputs:
            column_name = outp.comp_name + " " + outp.prop_name + "_" + outp.extreme
            self.df[column_name] = pd.Series(outp.get_results())
        logger.debug("Output is available!")

    def get_results(self):
        return self.df

    def plot_results(self, filename_prefix, width=300, height=300):
        for output in self.outputs:
            data = output.get_results()
            f, axarr = plt.subplots(3, sharex=False)
            axarr[0].hist(output.get_results(), 15)
            axarr[0].set_xlabel(output.prop_name + "_" + output.extreme)
            axarr[0].set_ylabel('Number of occurences')
            axarr[1].plot([np.mean(data[0:x]) for x in range(1, len(data))])
            axarr[1].set_xlabel('Number of runs')
            axarr[1].set_ylabel('Average of results')
            axarr[2].plot([np.std(data[0:x]) for x in range(1, len(data))])
            axarr[2].set_xlabel('Number of runs')
            axarr[2].set_ylabel('Standard deviation of results')
            dpi = f.get_dpi()
            f.set_size_inches(width / dpi, height / dpi)
            plt.tight_layout()
            plt.savefig(filename_prefix + "_" + output.prop_name + "_" + output.extreme,
                        bbox_inches='tight', pad_inches=0.1)

    def cleanup(self):
        for i in range(0, self.n_workers):
            shutil.rmtree(os.path.join(os.getcwd(), str(i)))
