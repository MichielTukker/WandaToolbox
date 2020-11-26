import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.express as px
import pywanda
from dash.exceptions import PreventUpdate


app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
#wanda_model = r'D:\wandatst\test_case1.wdi'
wanda_bin = r'd:\repos\wandaboom\Wanda4\Trunk\Bin64\Release\\'
if 'wanda_model' not in globals():
    wanda_model = None



def get_options(input_list):
    dict_list = []
    for i in range(len(input_list)):
        dict_list.append({'label': input_list[i], 'value': input_list[i]})
    return dict_list


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-control',
                             children=[
                                 html.H2('Cost overview'),
                                 html.Div(
                                     children=[dcc.Input(id="wandacase",
                                                          type='text'),
                                               html.Button('Load WANDA case', id='load_case', n_clicks=0),
                                               dcc.Dropdown(id='wanda_component'),
                                               dcc.Dropdown(id='wanda_property')
                                               ]
                                     )
                                ]
                             ),
                    html.Div(className='eight columns',
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=False)
                             ])
                              ])
        ]

)


@app.callback(Output('wanda_component','options'),
              [Input('load_case', 'n_clicks')],
              State('wandacase', 'value'))
def load_wanda_case(n_clicks, wanda_case):
    if wanda_case is None:
        raise PreventUpdate
    print(wanda_case)
    global wanda_model
    wanda_model = pywanda.WandaModel(wanda_case, wanda_bin)
    wanda_model.reload_output()
    options = get_options(wanda_model.get_all_components_str())
    return options


@app.callback(Output('wanda_property', 'options'),
              [Input('wanda_component', 'value')])
def get_properties(selected_item):
    global wanda_model
    if wanda_model is None:
        raise PreventUpdate
    comp = wanda_model.get_component(selected_item)
    props = comp.get_all_properties()
    prop_list = []
    for prop in props:
        if prop.is_input():
            continue
        prop_list.append(prop.get_description())
    return get_options(prop_list)


@app.callback(Output('timeseries', 'figure'),
              [Input('wanda_property', 'value'),
              State('wanda_component', 'value')])
def update_graph(prop, comp):
    if prop is None or comp is None:
        raise PreventUpdate
    wanda_property = wanda_model.get_component(comp).get_property(prop)

    series = [x * wanda_property.get_unit_factor() for x in wanda_property.get_series()]
    dim = wanda_model.get_current_dim(wanda_property.get_unit_dim())
    series_name = prop + ' (' + dim + ')'
    time = 'Time' + ' (' + wanda_model.get_current_dim('time') + ')'
    data_dict = {time: wanda_model.get_time_steps(),
                 series_name: series
                 }
    df = pd.DataFrame(data_dict, columns=[time, series_name])
    fig = px.line(df, x=time, y=series_name, title=comp + ' ' + prop)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
