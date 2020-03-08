![Python package](https://github.com/MichielTukker/WandaToolbox/workflows/Python%20package/badge.svg)

# Wanda Toolbox
Toolbox (python scripts) for Wanda modellers

This toolbox includes several tools and utilities that can help with Wanda modelling and 
running simulations. 

## Installation
Run the following to install this package:
```python
pip install WandaToolbox
```

## Usage
Generic usage of the WandaPlot classes:
```python
from src import PlotSyschar, PlotText, PlotTable, PlotImage, plot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pywanda as pw

model = pw.WandaModel(r'c:\Wandamodel.wdi', 'c:\Wanda 4.6\Bin\\')

with PdfPages(f'Document.pdf') as pdf:
    counter = 1

    img = plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png')
    subplots_table = []
    subplots_table.append(PlotTable(df, ['description', "Current min", "Current max", "Future min", "Future max"]))
    subplots_table.append(PlotImage(img))

    plot(model, subplots_table,
         'Main title',
         f'Subtitle 1',
         'Subtitle 2',
         'Subtitle 3',
         'Subtitle 4',
         f'Figure number: {counter}',
         company_image=plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png'),
         fontsize=10)
    pdf.savefig()
    plt.close()
```

# Support
No official support! For questions/improvements/comments, contact Deltares or Wanda support desk?

