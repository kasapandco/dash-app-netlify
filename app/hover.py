import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State

cars_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/imports-85.csv')
# Build parcats dimensions
categorical_dimensions = ['body-style', 'drive-wheels', 'fuel-type']
dimensions = [dict(values=cars_df[label], label=label) for label in categorical_dimensions]
# Build colorscale.
color = np.zeros(len(cars_df), dtype='uint8')
colorscale = [[0, '#167b7e'], [1, '#4b3268']]


def build_figure():
    fig = go.Figure(
        data=[
            go.Scatter(x=cars_df.horsepower, y=cars_df['highway-mpg'],
                       marker={'color': 'gray'}, mode='markers', selected={'marker': {'color': 'firebrick'}},
                       unselected={'marker': {'opacity': 0.4}}),
            go.Parcats(
                domain={'y': [0, 0.4]}, dimensions=dimensions,
                line={'colorscale': colorscale, 'cmin': 0,
                      'cmax': 1, 'color': color, 'shape': 'hspline'})
        ])
    fig.update_layout(
        height=800,
        xaxis={'title': 'Horsepower'},
        yaxis={'title': 'MPG', 'domain': [0.6, 1]},
        dragmode='lasso',
        hovermode='closest',
        # plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        autosize=False,
        bargap=0.35,
        font={"family": "Questrial", "size": 10})
    return fig


app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div([dcc.Graph(figure=build_figure(), id="graph")])

server = app.server
app.config.suppress_callback_exceptions = True

@app.callback(Output("graph", "figure"), [Input("graph", "selectedData"), Input("graph", "clickData")],
              [State("graph", "figure")])
def update_color(selectedData, clickData, fig):
    selection = None
    # Update selection based on which event triggered the update.
    trigger = dash.callback_context.triggered[0]["prop_id"]
    if trigger == 'graph.clickData':
        selection = [point["pointNumber"] for point in clickData["points"]]
    if trigger == 'graph.selectedData':
        selection = [point["pointIndex"] for point in selectedData["points"]]
    # Update scatter selection
    fig["data"][0]["selectedpoints"] = selection
    # Update parcats colors
    new_color = np.zeros(len(cars_df), dtype='uint8')
    new_color[selection] = 1
    fig["data"][1]["line"]["color"] = new_color
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80, use_reloader=False)