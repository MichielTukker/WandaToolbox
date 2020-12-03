import unittest
import unittest.mock
from pytest_mock import mocker

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from wandatoolbox.wanda_plot import PlotSyschar, PlotText, PlotTable, PlotImage, plot

mocker.patch('pw.WandaModel')

class TestWandaPlot(unittest.TestCase):
    def test_wandaplot_text(self):

        model = pw.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                              r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
        with PdfPages(f'test_wandaplottext.pdf') as pdf:
            counter = 1

            subplots_table = [PlotText("Testing text")]
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

    def test_wandaplot_image(self):
        model = pw.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                              r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
        img = plt.imread(r'Examples\example_data\Wanda_init.png')
        with PdfPages(f'test_wandaplotimage.pdf') as pdf:
            counter = 1

            subplots_table = [PlotImage(img)]
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

    def test_wandaplot_table(self):
        model = pw.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                              r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
        df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                   columns=['Aaa', 'Bbb', 'Ccc'])
        with PdfPages(f'test_wandaplottable.pdf') as pdf:
            counter = 1

            subplots_table = [PlotTable(df, df.columns)]
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

    def test_wandaplot_route(self):
        pass

    def test_wandaplot_time(self):
        pass

    def test_wandaplot_syschar(self):
        pass


if __name__ == '__main__':
    unittest.main()
