import unittest
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import pywanda as pw
from wandatoolbox.wanda_plot import PlotSyschar, PlotText, PlotTable, PlotImage, plot


class WandaPlotTest(unittest.TestCase):
    def wandaplot_text(self):
        model = pw.WandaModel(r'..\Examples\example_data\syschar_test.wdi', r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
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

    def wandaplot_image(self):
        model = pw.WandaModel(r'..\Examples\example_data\syschar_test.wdi', r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
        img = plt.imread(r'..\Examples\example_data\Wanda_init.png')
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

    def wandaplot_route(self):
        pass

    def wandaplot_time(self):
        pass

    def wandaplot_syschar(self):
        pass



if __name__ == '__main__':
    unittest.main()
