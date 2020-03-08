import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import pywanda as pw

from wandatoolbox.wanda_plot import PlotSyschar, PlotText, PlotTable, PlotImage, plot

description_text = """
Flow scenario 1: Flow rate at this supplier from 0 to Future Maximum, other suppliers at Current Minimum 
Flow scenario 2: Flow rate at this supplier from 0 to Future Maximum, other suppliers at Current Maximum
Flow scenario 3: Flow rate at this supplier from 0 to Future Maximum, other suppliers at Future Minimum 
Flow scenario 4: Flow rate at this supplier from 0 to Future Maximum, other suppliers at Future Maximum 
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
The discharge-head characteristics show the required head of the pumps for
a certain flow rate in the range of flow rates of this supplier for different
flow scenarios of other industries.
In the above figure, 4 curves are provided for the 4 flow scenarios.
By varying the flow rate at this supplier from 0 to the Future Maximum while
the other suppliers are delivering flow rates at Current minimum, Current Maximum,
Future Minimum or Future Maximum, the required pump head is obtained.
"""

if __name__ == '__main__':
    df = pd.read_excel(r'example_data\syschar_test.xlsx', header=0, index_col=0)
    df['Wanda_name'] = 'BOUNDQ ' + df['name']
    print(df)

    Industry_names = df['name'].tolist()
    Industry_names_dbg = ['Ind_01-G']  # , 'Ind_09-C', 'Ind_12', 'SecInd_A-D', 'SecInd_B-D']
    model = pw.WandaModel(r'example_data\syschar_test.wdi', r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
    model.reload_output()
    scenario_names = ["Current min"]  # , "Current max", "Future min", "Future max"]
    img = plt.imread(r'example_data\Wanda_init.png')

    try:
        with PdfPages(f'Document.pdf') as pdf:
            counter = 1

            subplots_table = [
                PlotTable(df, ['description', "Current min", "Current max", "Future min", "Future max"]),
                PlotImage(img)
            ]
            plot(model, subplots_table,
                 'Discharge head for Suppliers',
                 f'All flow scenarios',
                 'flow rates',
                 '1120XXXX',
                 'Appendix A',
                 f'Fig A.{counter}',
                 company_image=None,
                 fontsize=10)
            pdf.savefig()
            plt.close()

            for name in Industry_names_dbg:
                counter = counter + 1
                i = Industry_names.index(name)
                industry_description = df.iloc[i]['description']
                max_flowrate = df.iloc[i]['syschar_flow']
                component_name = df.iloc[i]['Wanda_name']

                subplots = [
                    PlotSyschar(component_name, max_flowrate, industry_description, df, 'Wanda_name',
                                scenario_names, 3, industry_description, 'Discharge (m3/day)', 'Head (m)'),
                    PlotText(description_text)
                ]
                plot(model, subplots,
                     'Discharge head for suppliers',
                     f'All flow scenarios',
                     industry_description,
                     '1120XXXX',
                     'Appendix A',
                     f'Fig A.{counter}',
                     company_image=None,
                     # company_image=plt.imread('WandaToolbox\data\DELTARES_ENABLING_CMYK.png'),
                     fontsize=10)
                pdf.savefig()
                plt.close()
    except Exception as e:
        raise
        # print(e)
        model.close()

    model.close()
