Plotting figures
========================================

Usage
--------
WandaToolbox supports plotting various objects to a formatted PDF, which can be included as an appendix in your 
report. WandaToolbox.wanda_plot supports time and location series where data is exported directly from Wanda models. 
It also supports adding tables, images or text blocks on pages, and supports generating system characteristics for 
a range of flow rates and discharge points.

Code example:

.. code-block:: python
    :linenos:
    
    from wandatoolbox.wanda_plot import PlotSyschar, PlotText, PlotTable, PlotImage, plot
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import pandas as pd
    import pywanda as pw

    model = pw.WandaModel(r'c:\Wandamodel.wdi', 'c:\Wanda 4.6\Bin\\')
    img = plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png')
    df = pd.read_excel(r'example_data\syschar_test.xlsx', header=0, index_col=0)
    scenario_names = ["Current min", "Current max", "Future min", "Future max"]

    with PdfPages(f'Document.pdf') as pdf:
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
