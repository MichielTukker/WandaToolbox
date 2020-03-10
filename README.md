![Python package](https://github.com/MichielTukker/WandaToolbox/workflows/Python%20package/badge.svg)

# Wanda Toolbox
Toolbox (python scripts) for Wanda modellers

This toolbox includes several tools and utilities that can help with Wanda modelling and 
running simulations. 

## Installation
Run the following to install this package:
```shell script
pip install WandaToolbox
```

## Usage
Generic usage of the WandaPlot classes:
```python
from wandatoolbox.wanda_plot import PlotSyschar, PlotText, PlotTable, PlotImage, plot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import pywanda as pw

model = pw.WandaModel(r'c:\Wandamodel.wdi', 'c:\Wanda 4.6\Bin\\')

with PdfPages(f'Document.pdf') as pdf:
    img = plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png')
    df = pd.read_excel(r'example_data\syschar_test.xlsx', header=0, index_col=0)
    scenario_names = ["Current min", "Current max", "Future min", "Future max"]

    subplots_table = [
        PlotTable(df, ['description', "Current min", "Current max", "Future min", "Future max"]), 
        PlotImage(img), PlotText("Yada yada yada"), 
        PlotSyschar("BOUNDQ B1", 105.0, "Supplier #1", df, 'Wanda_name', 
        scenario_names, 3, "Industry description", 'Discharge (m3/day)', 'Head (m)')
    ]
    plot(model, subplots_table,
         'Main title',
         f'Subtitle 1',
         'Subtitle 2',
         'Subtitle 3',
         'Subtitle 4',
         f'Figure number: 1',
         company_image=plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png'),
         fontsize=10)
    pdf.savefig()
    plt.close()
```

Generic usage of the monte-carlo class:
```python
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
```
# Support
No official support! For questions/improvements/comments, contact Deltares or Wanda support desk?

