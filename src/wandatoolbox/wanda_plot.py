from datetime import datetime
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

from .util import get_route_data, get_syschar


def plot_7box(figure, title, case_title, case_description, proj_number, section_name, fig_name, company_name="Deltares",
              software_version="Wanda 4.6", company_image=None,
              fontsize=12):
    """
    Creates box around and in the plot window. Also fills in some info about the calculation.
    Based on the 7-box WL-layout.
    """

    # Define locations of vertical and horizontal lines
    xo = 0.04
    yo = 0.03
    textbox_height = 0.75

    v0 = 0.0 + xo
    v1 = 0.62 + xo
    v2 = 0.81
    v3 = 1.0 - xo

    h0 = 0.0 + yo
    h1 = 1.2 * textbox_height / 29.7 + yo
    h2 = 2.4 * textbox_height / 29.7 + yo
    h3 = 3.6 * textbox_height / 29.7 + yo

    ax = plt.axes([0, 0, 1, 1], facecolor=(1, 1, 1, 0))

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    l1 = ax.axhline(y=h3, xmin=v0, xmax=v3, linewidth=1.5, color='k')
    l2 = ax.axvline(x=v1, ymin=h0, ymax=h3, linewidth=1.5, color='k')
    l3 = ax.axhline(y=h1, xmin=v0, xmax=v3, linewidth=1.5, color='k')
    l4 = ax.axvline(x=v2, ymin=h0, ymax=h1, linewidth=1.5, color='k')
    l5 = ax.axvline(x=v2, ymin=h2, ymax=h3, linewidth=1.5, color='k')
    l6 = ax.axhline(y=h2, xmin=v1, xmax=v3, linewidth=1.5, color='k')

    #     bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #     width, height = bbox.width * fig.dpi, bbox.height * fig.dpi
    #     linewidth = 2
    rect = Rectangle((xo, yo), 1 - (2 * xo), 1 - (2 * yo), fill=False, linewidth=1.5)
    ax.add_patch(rect)

    # Case title and description
    text1 = "\n".join((title, case_title, case_description))
    figure.text(v0 + 0.01, (h3 - (h3 - h1) / 2.), text1,
                verticalalignment='center', horizontalalignment='left',
                color='black', fontsize=fontsize)

    # Section name/number
    figure.text((v1 + (v2 - v1) / 2.), h2 + (h3 - h2) / 2., section_name,
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    # Project number
    figure.text((v1 + (v2 - v1) / 2.), (h0 + (h1 - h0) / 2.), proj_number,
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    # Company name
    figure.text((v0 + (v1 - v0) / 2.), (h0 + (h1 - h0) / 2.), company_name,
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    # Create datestamp
    today = datetime.date(datetime.now())
    figure.text((v2 + (v3 - v2) / 2.), h2 + (h3 - h2) / 2., today.strftime('%d-%m-%Y'),
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    # Figure name
    today = datetime.date(datetime.now())
    figure.text((v2 + (v3 - v2) / 2.), (h0 + (h1 - h0) / 2.), fig_name,
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    # Print WANDA version
    figure.text((v1 + (v3 - v1) / 2.), h1 + (h2 - h1) / 2., software_version,
                verticalalignment='center', horizontalalignment='center',
                color='black', fontsize=fontsize)

    img = company_image
    if company_image is None:
        import os
        module_dir, module_filename = os.path.split(__file__)
        image_path = os.path.join(module_dir, "image_data", "Deltares_logo.png")
        img = plt.imread(image_path)
    imgax = figure.add_axes([v1, h0, v3 - v1, h3 - h0], zorder=-10)
    imgax.imshow(img, alpha=0.3, interpolation='none')
    imgax.axis('off')


class PlotObject:
    """
    PlotObject, base class for different types of plots
    """
    def __init__(self, title, xlabel, ylabel, xmin=None, xmax=None, xscale=1.0, ymin=None, ymax=None, yscale=1.0):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xmin = xmin
        self.xmax = xmax
        self.xscale = xscale
        self.ymin = ymin
        self.ymax = ymax
        self.yscale = yscale

    def _plot_finish(self, ax):
        # Make tight on x-axis
        ax.autoscale(tight=True, axis='x')

        # Scale the data and axes
        for line in ax.get_lines():
            x_data, y_data = line.get_data()
            line.set_data(x_data / self.xscale, y_data / self.yscale)

        xmin, xmax = np.array(ax.get_xlim()) / self.xscale
        ymin, ymax = np.array(ax.get_ylim()) / self.yscale

        xmin = self.xmin if self.xmin is not None else xmin
        xmax = self.xmax if self.xmax is not None else xmax
        ymin = self.ymin if self.ymin is not None else ymin
        ymax = self.ymax if self.ymax is not None else ymax

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        # Add labels, grid, and other formatting
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.title)
        ax.grid(True, linestyle='--', alpha=0.7)

        # Plot the legend below the axes, and below the x-axis label.
        # We do this by shrinking the axes a little on the bottom.
        ax.legend()
        box = ax.get_position()
        height_shrink = 0.05
        ax.set_position([box.x0, box.y0 + height_shrink,
                         box.width, box.height - height_shrink])
        # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -1 * height_shrink / box.height),
        #           fancybox=True, shadow=True, ncol=5, frameon=True)

    def plot(self, model, ax):
        raise NotImplementedError


class PlotRoute(PlotObject):
    """
    creates a route plot or location-graph for a given route in a wanda model (route is specified by keyword. Only
    supports a single property, but allows plotting of pipeline profile in same figure
    """

    def __init__(self, pipes, annotations, prop, times, *args, plot_elevation=False, **kwargs):
        if (len(pipes) != len(annotations)):
            raise ValueError('Pipes list and Annotations list must have the same length')
        self.pipes = pipes
        self.annotations = annotations
        self.prop = prop
        self.times = times
        self.plot_elevation = plot_elevation
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        s_location, elevation, data = get_route_data(model, self.pipes, self.annotations, self.prop, self.times)

        color_ind = 0
        for t, v in data.items():
            # Min/max keep their name, but floats get a 's' unit appended

            if t == 0:
                label = f'{self.prop}' if not isinstance(t, str) else t
            else:
                label = f'{t} s' if not isinstance(t, str) else t

            if label == "max":
                ax.plot(s_location, v, label=label, linestyle='--', c='r', zorder=-1)
            elif label == "min":
                ax.plot(s_location, v, label=label, linestyle='--', c='k', zorder=-1)
            else:
                ax.plot(s_location, v, label=label, c=f'C{color_ind}')
                color_ind += 1

        if self.plot_elevation:
            ax.plot(s_location, elevation, label='Elevation', c='g', linewidth=2, alpha=0.3, zorder=-2)

        self._plot_finish(ax)


class PlotSyschar(PlotObject):
    """Creates system characteristics graphs for given wanda model, flow scenarios and flow range. It automatically
        calculates the system characteristic for a given model and flow scenarios.
    """

    def __init__(self, component_name, max_flowrate, description, discharge_dataframe, supplier_column, scenario_names,
                 number_of_points, *args, **kwargs):
        """Creates system characteristics graphs for given wanda model, flow scenarios and flow range. It automatically
        calculates the system characteristic for a given model and flow scenarios.
        :param component_name: Name of the component the calculate the system characteristic for
        :param max_flowrate: Maximum flowrate
        :param description: Text description of this component
        :param discharge_dataframe: Pandas dataframe with discharges of other suppliers in the model
        :param supplier_column: Column name that contains the names of the Wanda components that represent the suppliers
        :param scenario_names: List of scenario names (names of columns in discharge_dataframe
        :param number_of_points: Number of steps for the system characteristic calculation. Default = 10
        :param args: remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        :param kwargs:
        """
        self.component_name = component_name
        self.max_flowrate = max_flowrate
        self.discharge_dataframe = discharge_dataframe
        self.supplier_column = supplier_column
        self.scenario_names = scenario_names
        self.n_points = number_of_points
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        color_ind = 0
        # suppliers = self.discharge_dataframe[self.supplier_column].tolist()
        flows = {}
        head_series = {}
        for scenario in self.scenario_names:
            print(f'Generating plot for {self.component_name}, max Q={self.max_flowrate * 3600 * 24:{2}.{6}} m3/day')
            discharges, heads = get_syschar(model, self.discharge_dataframe, self.component_name, self.max_flowrate,
                                            scenario, self.n_points)
            flows[scenario] = [q * 3600 * 24 for q in discharges]  # display discharge in m3/day
            head_series[scenario] = heads

        for scenario, heads in head_series.items():
            ax.plot(flows[scenario], heads, label=scenario, marker='o', linestyle='--', c=f'C{color_ind}', zorder=-1)
            color_ind += 1
        self._plot_finish(ax)


class PlotTimeseries(PlotObject):
    """
    Creates a timeseries plot for a given property, only supports a single axis.
    """

    def __init__(self, collection=List[Tuple[str, str, str]], *args, **kwargs):
        self.collection = collection
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        x = model.get_time_steps()

        for comp, prop, label in self.collection:
            try:
                prop = model.get_component(comp).get_property(prop)
            except ValueError:
                prop = model.get_node(comp).get_property(prop)
            ax.plot(x, prop.get_series(), label=label)

        self._plot_finish(ax)


class PlotText(PlotObject):
    """
    Creates a textbox on the page. Formatting is up to the user
    """
    def __init__(self, text, *args, **kwargs):
        self.text = text
        super().__init__(title='', xlabel='', ylabel='', *args, **kwargs)

    def plot(self, model, ax):
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.set_axis_off()
        if(ax.get_legend()):
            ax.get_legend().remove()
        ax.text(-0.1, 1.0, self.text, transform=ax.transAxes, size=8, fontsize=9,
                verticalalignment='top', bbox=props)
        self._plot_finish(ax)


class PlotTable(PlotObject):
    """
    Creates a table on the subplot/page.
    input is a Pandas dataframe
    """
    def __init__(self, dataframe, columns, *args, **kwargs):
        """Creates a table on the subplot/page.

        :param dataframe: Pandas dataframe containing the data
        :param columns: list of column names to display in the table
        """
        self.df = dataframe
        self.columns = columns
        super().__init__(title='', xlabel='', ylabel='', *args, **kwargs)

    def plot(self, model, ax):
        table = self.df[self.columns]
        header = table.columns
        table = np.asarray(table)
        ax.set_axis_off()
        if (ax.get_legend()):
            ax.get_legend().remove()
        colors = []
        for x in header:
            colors.append('grey')
        tab = ax.table(cellText=table, colLabels=header, colColours=colors, cellLoc='center', loc='center')
        tab.auto_set_column_width(True)
        tab.auto_set_font_size(True)
        self._plot_finish(ax)


class PlotImage(PlotObject):
    """
    Adds an image on the subplot/page
    """
    def __init__(self, image, *args, **kwargs):
        """Adds an image on the subplot/page

        :param image: numpy.array containing the image,  for example from matplotlib.pyplot.imread()
        """
        self.img = image
        super().__init__(title='', xlabel='', ylabel='', *args, **kwargs)

    def plot(self, model, ax):
        if (ax.get_legend()):
            ax.get_legend().remove()
        ax.set_axis_off()
        ax.imshow(self.img)
        self._plot_finish(ax)


def plot(model, plot_objects, *args, **kwargs):
    """Renders pages from the given set of subplots."""
    fig = plt.figure(figsize=(8.27, 11.69))
    plt.subplots_adjust(left=0.15, right=0.89, top=0.92, bottom=0.16, hspace=0.2 + (len(plot_objects) - 2) * 0.05)

    axes = fig.subplots(len(plot_objects), 1)

    if not hasattr(axes, '__iter__'):
        assert len(plot_objects) == 1
        axes = [axes]

    for ax, po in zip(axes, plot_objects):
        po.plot(model, ax)

    plot_7box(fig, *args, **kwargs)
