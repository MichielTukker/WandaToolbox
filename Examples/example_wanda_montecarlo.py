from wandatoolbox.analysis.monte_carlo import MonteCarloInputProperty, MonteCarloOutputProperty, WandaMonteCarlo
import pywanda as pw
import os

n_runs = 25  # total number of runs per worker which need to be performed
n_workers = 8  # Number of parallel workers which will be used. The optimal number depends on your PC
cwd = os.getcwd()
wandacase_fullpath = os.path.join(cwd, "wandamodel", "Sewage_transient.wdi")
wanda_bin_directory = r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\'
model = pw.WandaModel(wandacase_fullpath, wanda_bin_directory)

parameters = [MonteCarloInputProperty("PIPES", "Wall roughness", 2.5 / 1000, 0.5 / 1000, "normal", True),
              MonteCarloInputProperty("BOUNDH B1", "Head at t = 0 [s]", -5, 5, "uniform"),
              MonteCarloInputProperty("BOUNDH B3", "Head at t = 0 [s]", -3, 3, "uniform"),
              MonteCarloInputProperty("GENERAL", "Bulk modulus", 1.8e9, 2.5e9, "uniform")]

outputs = [MonteCarloOutputProperty("PIPES", "Pressure", keyword=True),
           MonteCarloOutputProperty("PIPES", "Pressure", keyword=True, extreme="MAX")]

analysis = WandaMonteCarlo(model, parameters, outputs, nruns=n_runs, n_workers=n_workers)
analysis.run()
df = analysis.get_results()
print(df.head())
analysis._plot_results(filename_prefix="test", width="", height="")
analysis.cleanup()


