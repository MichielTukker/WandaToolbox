import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import pandas as pd
import numpy as np
import pywanda as pw

from WandaToolbox.graphics.WandaPlot import PlotSyschar, PlotText, plot

description_text = """
Flow scenario 1: Flow rate at this industry from 0 to Future Maximum, other industries at Current Minimum 
Flow scenario 2: Flow rate at this industry from 0 to Future Maximum, other  industries at Current Maximum
Flow scenario 3: Flow rate at this industry from 0 to Future Maximum, other  industries at Future Minimum 
Flow scenario 4: Flow rate at this industry from 0 to Future Maximum, other  industries at Future Maximum 
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
The discharge-head characteristics show the required head of the pumps for
a certain flow rate in the range of flow rates of this industry for different
flow scenarios of other industries.
In the above figure, 4 curves are provided for the 4 flow scenarios.
By varying the flow rate at this industry from 0 to the Future Maximum while
the other industries are delivering flow rates at Current minimum, Current Maximum,
Future Minimum or Future Maximum, the required pump head is obtained.
"""

def get_syschar(model, dataframe, industry_name, max_flowrate, scenario):
    compname = 'BOUNDQ ' + industry_name
    index = -999
    for i, row in dataframe.iterrows():
        if(row['name'] == industry_name):
            # print(f'found industry {row["description"]}')
            index = i
            pass
        targetname = 'BOUNDQ '+ row['name']
        discharge_setting = row[scenario]
        # print(f'Setting component={targetname} value={discharge_setting}')
        comp = model.get_component(targetname)
        prop = comp.get_property('Discharge at t = 0 [s]')
        prop.set_scalar(discharge_setting)

    model.save_model_input()
    target_comp = model.get_component(compname)
    target_prop = target_comp.get_property('Discharge at t = 0 [s]')
    result_prop = target_comp.get_property('Head 1')
    target_flowrate = max_flowrate # dataframe.iloc[index - 1][scenario]
    discharges = np.linspace(0,target_flowrate,10).tolist()
    syschar = []
    print(f"Computing syschar for {compname}...", end="", flush=True)
    for flow in discharges:
        target_prop.set_scalar(flow)
        model.save_model_input()
        print(f" {flow:{2}.{6}}", end="", flush=True)
        model.run_steady()
        model.reload_output()
        syschar.append(result_prop.get_scalar_float())
    print(' Done.')
    if(len(discharges) != len(syschar)):
        raise Exception('Length of lists should be equal')
    return discharges, syschar


if __name__ == '__main__':
    df = pd.read_excel('../Wanda/flowrates.xlsx', header=0, index_col=0)
    print(df)

    Industry_names = df['name'].tolist()
    Industry_names_dbg = ['Ind_01-G', 'Ind_09-C', 'Ind_12', 'SecInd_A-D', 'SecInd_B-D']
    model = pw.WandaModel(r'..\Wanda\Jubail_IWW_Rev1.0_Syschar.wdi', 'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
    model.reload_output()

    try:
        with PdfPages(f'..\Appendix_A.pdf') as pdf:
            counter = 1
            for name in Industry_names:
                flows = {}
                syschars = {}
                for scenario in ["Current min", "Current max", "Future min", "Future max"]:
                    i = Industry_names.index(name)
                    industry_description = df.iloc[i]['description']
                    max_flowrate = df.iloc[i]['syschar_flow']
                    print(f'Generating plot for {industry_description}, max Q={max_flowrate*3600*24:{2}.{6}} m3/day')
                    discharges, heads = get_syschar(model, df, name, max_flowrate, scenario)
                    flows[scenario] = [q *3600*24 for q in discharges] # display discharge in m3/day
                    syschars[scenario] = heads

                subplots = []
                subplots.append(
                    PlotSyschar(flows, syschars, name, industry_description, 'Discharge (m3/day)', 'Head (m)'))
                subplots.append(
                    PlotText(description_text)
                )

                plot(model, subplots,
                     'Discharge head for Industries',
                     f'All flow scenarios',
                     industry_description,
                     '11202658',
                     'Appendix A',
                     f'Fig A.{counter}',
                     company_image='..\data\DELTARES_ENABLING_CMYK.png',
                     fontsize=10)
                counter = counter + 1
                pdf.savefig()
                plt.close()
    except Exception as e:
        print(e)
        model.close()

    model.close()


