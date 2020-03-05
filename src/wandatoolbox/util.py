import numpy as np
import pywanda as pw


def get_min_max_pipe(pipes, property_name, scale_fac=1.0):
    """ Just a small convenience method to get both extremes at once, and scale the
    values immediately (e.g. for pressure, we scale with 1E5 typically to go
    from Pa to barg) """

    tr_min_data = np.hstack([np.array(p.get_property(property_name).get_extr_min_pipe()) for p in pipes])
    tr_max_data = np.hstack([np.array(p.get_property(property_name).get_extr_max_pipe()) for p in pipes])

    tr_min = np.min(tr_min_data)
    tr_max = np.max(tr_max_data)

    ret_max = tr_max / scale_fac
    ret_min = tr_min / scale_fac

    if ret_min < -0.99:
        ret_min = -0.99

    return ret_max, ret_min


def get_min_max_pipe_relative(pipes, property_name):
    """Just a small convenience method to get both extremes at once, and scale the
    values immediately (e.g. for pressure, we scale with 1E5 typically to go
    from Pa to barg)"""

    tr_min_data = np.hstack([np.array(p.get_property(property_name).get_extr_min_pipe()) for p in pipes])
    tr_max_data = np.hstack([np.array(p.get_property(property_name).get_extr_max_pipe()) for p in pipes])

    tr_min = np.min(tr_min_data)
    tr_max = np.max(tr_max_data)

    ss_data = np.hstack([np.array(p.get_property(property_name).get_series_pipe())[:, 0] for p in pipes])
    ss_min = np.maximum(np.min(ss_data), -0.99)
    ss_max = np.max(ss_data)

    return (tr_max + 1) / ss_max, (tr_min + 1) / (ss_min + 1),


def get_route_data(model, pipes, annotations, prop, times):
    """First we get the s-locations and elevations of every grid point in the output
    Note that we also interpolate the elevations to the grid points, such that we
    can use a single source of x-axis data."""

    s_locations = []
    elevations = []

    pipes = pipes.copy()
    for i, p in enumerate(pipes):
        if isinstance(p, str):
            pipes[i] = model.get_component(p)

    for p in pipes:
        profile_data_s_h = np.array(p.get_property('Profile').get_table().get_float_data()[:3]).transpose()[:, -1:0:-1]

        s_dist_pipe = np.linspace(profile_data_s_h[0, 0], profile_data_s_h[-1, 0], p.get_num_elements() + 1)

        if (annotations[pipes.index(p)] == -1):
            elevations.append(np.flipud(np.interp(s_dist_pipe, profile_data_s_h[:, 0], profile_data_s_h[:, 1])))
        else:
            elevations.append(np.interp(s_dist_pipe, profile_data_s_h[:, 0], profile_data_s_h[:, 1]))

        offset = s_locations[-1][-1] if s_locations else 0.0
        s_locations.append(s_dist_pipe + offset)

    s_location = np.hstack(s_locations)
    elevation = np.hstack(elevations)

    dt = np.average(np.diff(model.get_time_steps()))
    if np.isnan(dt):
        dt = 1.0

    # check annotation and reverse data if necessary
    data_list = []
    for p in pipes:
        direction = annotations[pipes.index(p)]
        data_array = np.array(p.get_property(prop).get_series_pipe())
        if (direction == -1):
            data_list.append(np.flipud(data_array))
        else:
            data_list.append(data_array)
    data = np.vstack(data_list)

    output_location_series = {}
    for t in times:
        if isinstance(t, str) and t.lower().startswith('max'):
            output_location_series[t] = np.max(data, axis=1)
        elif isinstance(t, str) and t.lower().startswith('min'):
            output_location_series[t] = np.min(data, axis=1)
        else:
            ind = int(round(t / dt))
            output_location_series[t] = data[:, ind].ravel()

    return s_location, elevation, output_location_series


def get_syschar(model, dataframe, component_name, max_flowrate, scenario, number_of_points=10,
                discharge_parameter='Discharge at t = 0 [s]',
                result_parameter='Head 1'):
    """Calculate the system characteristic for a specific supplier in a model
    :param model: Wanda model to be used for the system characteristic
    :param dataframe: Pandas dataframe with columns for the names and flowrates of the other suppliers in the network
    :param component_name: Component who's parameter is varied for the system characteristics
    :param max_flowrate: Maximum flow rate for the system characteristic
    :param scenario: Name of the column of the dataframe with the discharges
    :param number_of_points: Number of steps in the system characteristic
    :param discharge_parameter: the parameter in the model used for setting the discharge (default = 'Discharge at t = 0 [s]')
    :param result_parameter: The parameter that is used for the output (default = 'Head 1')
    :return: model_inputs[], model_outputs[]
    """
    if len(dataframe.index) > 0:
        for i, row in dataframe.iterrows():
            targetname = 'BOUNDQ ' + row['name']
            discharge_setting = row[scenario]
            comp = model.get_component(targetname)
            prop = comp.get_property(discharge_parameter)
            prop.set_scalar(discharge_setting)

    model.save_model_input()
    target_comp = model.get_component(component_name)
    target_prop = target_comp.get_property(discharge_parameter)
    result_prop = target_comp.get_property(result_parameter)
    model_inputs = np.linspace(0, max_flowrate, number_of_points).tolist()
    model_outputs = []
    print(f"Computing result for {component_name}...", end="", flush=True)
    for flow in model_inputs:
        target_prop.set_scalar(flow)
        model.save_model_input()
        print(f" {flow:{2}.{6}}", end="", flush=True)
        model.run_steady()
        model.reload_output()
        model_outputs.append(result_prop.get_scalar_float())
    print(' Done.')
    if len(model_inputs) != len(model_outputs):
        raise Exception('Length of lists should be equal')
    return model_inputs, model_outputs

