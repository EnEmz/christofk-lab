import dash
from dash import html, dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Create the initial figure
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 3, 2])])
fig.update_layout(
    annotations=[{
        'x': 2,
        'y': 3,
        'xref': 'x',
        'yref': 'y',
        'text': 'Draggable Annotation',
        'showarrow': True,
        'arrowhead': 7,
        'ax': 0,
        'ay': -40
    }]
)

app.layout = html.Div([
    dcc.Graph(id='my-graph', figure=fig)
])

# Callback to handle annotation dragging
@app.callback(
    Output('my-graph', 'figure'),
    [Input('my-graph', 'relayoutData')],
    [dash.dependencies.State('my-graph', 'figure')]
)
def update_annotation(relayoutData, figure):
    if relayoutData and 'annotations[0].x' in relayoutData and 'annotations[0].y' in relayoutData:
        figure['layout']['annotations'][0]['x'] = relayoutData['annotations[0].x']
        figure['layout']['annotations'][0]['y'] = relayoutData['annotations[0].y']
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)