analysis tools
===============

Monte-carlo analysis
--------------------
Generic usage of the monte-carlo class:

.. code-block:: python
    :linenos:

    from wandatoolbox.analysis.monte_carlo import MonteCarloInputProperty, MonteCarloOutputProperty, WandaMonteCarlo
    import pywanda as pw
    import os

    def main():
        wandacase_fullpath = os.path.join(os.getcwd(), "Sewage_transient.wdi")
        wanda_bin_directory = r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\'
        model = pw.WandaModel(wandacase_fullpath, wanda_bin_directory)
        parameters = [MonteCarloInputProperty(" PIPES", "Wall roughness", 2.5 / 1000, 0.5 / 1000, "normal", True)]
        outputs = [MonteCarloOutputProperty(" PIPES", "Pressure", keyword=True, extreme="MIN"),
                MonteCarloOutputProperty(" PIPES", "Pressure", keyword=True, extreme="MAX")]
        analysis = WandaMonteCarlo(model, parameters, outputs, nruns=25, n_workers=2)
        analysis.run()
        analysis.plot_results(filename_prefix="test", width=1000, height=800)
        analysis.cleanup()


    if __name__ == "__main__":
        main()  # This main() method is essential due to the way Python's multiprocessing module works

The monte carlo toolset will run multiple simulation in parallel, greatly reducing the simulation time. 