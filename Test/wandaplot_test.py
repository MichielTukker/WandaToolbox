# import pytest
# import mock
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import pywanda
from wandatoolbox.wanda_plot import PlotText, PlotTable, PlotImage, plot


def test_wandaplot_text(mocker):
    mocker.patch('pywanda.WandaModel')
    model = pywanda.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                               r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
    with PdfPages('test_wandaplottext.pdf') as pdf:
        counter = 1

        subplots_table = [PlotText("Testing text")]
        plot(model, subplots_table,
             'Title',
             'Case title',
             'Case description',
             '11201234',
             'Section name',
             f'Fig A.{counter}',
             company_image=None,
             fontsize=10)
        pdf.savefig()
        plt.close()


def test_wandaplot_image(mocker):
    mocker.patch('pywanda.WandaModel')
    model = pywanda.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                               r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
    img = plt.imread(r'Examples\example_data\Wanda_init.png')
    with PdfPages('test_wandaplotimage.pdf') as pdf:
        counter = 1

        subplots_table = [PlotImage(img)]
        plot(model, subplots_table,
             'Title',
             'Case title',
             'Case description',
             '11201234',
             'Section name',
             f'Fig A.{counter}',
             company_image=None,
             fontsize=10)
        pdf.savefig()
        plt.close()


def test_wandaplot_table(mocker):
    mocker.patch('pywanda.WandaModel')
    model = pywanda.WandaModel(r'Examples\example_data\Sewage_transient.wdi',
                               r'c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\')
    df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                      columns=['Aaa', 'Bbb', 'Ccc'])
    with PdfPages('test_wandaplottable.pdf') as pdf:
        counter = 1

        subplots_table = [PlotTable(df, df.columns)]
        plot(model, subplots_table,
             'Title',
             'Case title',
             'Case description',
             '11201234',
             'Section name',
             f'Fig A.{counter}',
             company_image=None,
             fontsize=10)
        pdf.savefig()
        plt.close()


def test_wandaplot_route(mocker):
    pass


def test_wandaplot_time(mocker):
    pass


def test_wandaplot_syschar(mocker):
    pass
