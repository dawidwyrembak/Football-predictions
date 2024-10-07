from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
from preprocess_table import preprocessing_data_table

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('app_2')

leagues = [
    preprocessing_data_table(1),
    preprocessing_data_table(2),
    preprocessing_data_table(3)
]

app.layout = html.Div([
    dcc.Tabs(
        id='tabs',
        value='0',
        children=[
            dcc.Tab(label='Premier League', value='0', className='custom-tab',
                    selected_className='custom-tab--selected'),
            dcc.Tab(label='Serie A', value='1', className='custom-tab',
                    selected_className='custom-tab--selected'),
            dcc.Tab(label='La Liga', value='2', className='custom-tab',
                    selected_className='custom-tab--selected'),
        ],
        colors={
            "border": "white",
            "primary": "grey",
            "background": "grey"
        }
    ),
    dash_table.DataTable(
        id='table',
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': '1px solid black'
        },
        cell_selectable=False,
        columns=[
            {"name": "", "id": "Place"},
            {"name": "Team", "id": "Team"},
            {"name": "Games", "id": "NumberOfMatches"},
            {"name": "Points", "id": "Points"},
            {"name": "Scored goals", "id": "GoalsScored"},
            {"name": "Conceded goals", "id": "GoalsConceded"}
        ],
        style_cell={
            'textAlign': 'center',
            'border': '1px solid grey',
            'fontSize': 15,
            'font-family': 'sans-serif'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Place'},
                'width': '20%',
            },
            {
                'if': {'column_id': 'Team'},
                'width': '40%'
            },
            {
                'if': {'column_id': 'NumberOfMatches'},
                'width': '10%'
            },
            {
                'if': {'column_id': 'Points'},
                'width': '10%'
            },
            {
                'if': {'column_id': 'GoalsScored'},
                'width': '10%'
            },
            {
                'if': {'column_id': 'GoalsConceded'},
                'width': '10%'
            }
        ]
    )
])

app.css.append_css({
    'external_url': external_stylesheets[0],
})


@app.callback(Output('table', 'data'),
              [Input('tabs', 'value')])
def update_table(v1):
    if v1 is None:
        raise PreventUpdate

    df = leagues[int(v1)]
    data = df.to_dict('records')

    return data


if __name__ == '__main__':
    app.run_server(debug=True)
