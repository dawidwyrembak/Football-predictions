from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from preprocess_plots import preprocessing_data_dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('app_1')

leagues = [
    preprocessing_data_dash(1),
    preprocessing_data_dash(2),
    preprocessing_data_dash(3)
]

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='dpdwn1',
            options=[
                {'label': 'Premier League', 'value': '0'},
                {'label': 'Serie A', 'value': '1'},
                {'label': 'La Liga', 'value': '2'}
            ],
            value='0',
            clearable=False
        ),
        dcc.Dropdown(
            id='dpdwn2',
            options=[
                {'label': '2018/2019', 'value': '2018/2019'},
                {'label': '2019/2020', 'value': '2019/2020'},
                {'label': '2020/2021', 'value': '2020/2021'}
            ],
            value='2020/2021',
            clearable=False
        ),
        dcc.Dropdown(
            id='dpdwn3',
            placeholder="Select team...",
            multi=True
        ),
        dcc.Graph(
            id='graph_1',
            config={
                'displayModeBar': False
            }
        )
    ], className="row"),
    html.Div([
        html.Div(
            dcc.Graph(
                id='graph_2',
                config={
                    'displayModeBar': False
                }
            ),
            style={'width': '50%', 'display': 'inline-block'}),
        html.Div(
            dcc.Graph(
                id='graph_3',
                config={
                    'displayModeBar': False
                }
            ),
            style={'width': '50%', 'display': 'inline-block'})
    ], className="row"),
    html.Div([
        dcc.Graph(
            id='graph_4',
            config={
                'displayModeBar': False
            }
        )
    ], className="row"),
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css',
})


@app.callback(
    Output('dpdwn3', 'options'),
    [Input('dpdwn1', 'value'), Input('dpdwn2', 'value')])
def set_teams(league, season):
    df = leagues[int(league)]
    df = df[df['Season'] == str(season)]

    return [{'label': i, 'value': i} for i in df['Team'].drop_duplicates()]


@app.callback(
    Output('graph_1', 'figure'),
    [Input('dpdwn1', 'value'), Input('dpdwn2', 'value'), Input('dpdwn3', 'value')])
def update_graph1(v1, v2, v3):
    if v3 is None:
        raise PreventUpdate

    df = leagues[int(v1)]
    df = df[df['Season'] == str(v2)]
    df = df[df.Team.isin(list(v3))]

    if df.empty:
        return px.scatter(template='plotly_white')

    teams = df['Team'].sort_values(ascending=True)

    figure = px.scatter(df,
                        x=df.NumberOfMatches,
                        y=df.Points,
                        color=df.Team,
                        title="Points in season",
                        labels={
                            "NumberOfMatches": "Number of game",
                            "Points": "Points",
                            "Team": "Team"
                        },
                        category_orders={
                            "Team": [t for t in teams]
                        },
                        template='plotly_white',
                        color_discrete_sequence=px.colors.sequential.Rainbow
                        )

    figure.update_traces(
        mode='markers',
        marker=dict(
            line_width=1,
            opacity=0.75,
            size=12
        )
    )

    figure.update_layout(
        title=dict(
            text="Points in season",
            y=0.9,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        xaxis=dict(
            showline=True,
            showticklabels=True,
            dtick=5,
            ticks='outside',
        ),
        margin=dict(
            l=140,
            r=40,
            b=50,
            t=80
        ),
        legend=dict(
            font_size=10,
            yanchor='top',
        ),
        legend_traceorder="grouped",
        hovermode='closest',
    )
    return figure


@app.callback(
    Output('graph_2', 'figure'),
    [Input('dpdwn1', 'value'), Input('dpdwn2', 'value'), Input('dpdwn3', 'value')])
def update_graph2(v1, v2, v3):
    if v3 is None:
        raise PreventUpdate

    df = leagues[int(v1)]
    df = df[df['Season'] == str(v2)]
    df = df[df.Team.isin(list(v3))]

    if df.empty:
        return px.scatter(template='plotly_white')

    teams = df['Team'].sort_values(ascending=True)

    figure = px.scatter(df,
                        x=df.NumberOfMatches,
                        y=df.GoalsScored,
                        color=df.Team,
                        title="Number of scored goals in season",
                        labels={
                            "NumberOfMatches": "Number of game",
                            "GoalsScored": "Scored Goals",
                            "Team": "Team"
                        },
                        category_orders={
                            "Team": [t for t in teams]
                        },
                        template='plotly_white',
                        color_discrete_sequence=px.colors.sequential.Rainbow
                        )

    figure.update_traces(
        mode='markers',
        marker=dict(
            line_width=1,
            opacity=0.75,
            size=9
        )
    )

    figure.update_layout(
        title=dict(
            text="Scored goals",
            y=0.9,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        xaxis=dict(
            showline=True,
            showticklabels=True,
            dtick=5,
            ticks='outside',
        ),
        margin=dict(
            l=140,
            r=40,
            b=50,
            t=80
        ),
        legend=dict(
            font_size=10,
            yanchor='top',
        ),
        legend_traceorder="grouped",
        hovermode='closest'
    )
    return figure


@app.callback(
    Output('graph_3', 'figure'),
    [Input('dpdwn1', 'value'), Input('dpdwn2', 'value'), Input('dpdwn3', 'value')])
def update_graph3(v1, v2, v3):
    if v3 is None:
        raise PreventUpdate

    df = leagues[int(v1)]
    df = df[df['Season'] == str(v2)]
    df = df[df.Team.isin(list(v3))]

    if df.empty:
        return px.scatter(template='plotly_white')

    teams = df['Team'].sort_values(ascending=True)

    figure = px.scatter(df,
                        x=df.NumberOfMatches,
                        y=df.GoalsConceded,
                        color=df.Team,
                        title="Number of conceded goals in season",
                        labels={
                            "NumberOfMatches": "Number of game",
                            "GoalsConceded": "Conceded goals",
                            "Team": "Team"
                        },
                        category_orders={
                            "Team": [t for t in teams]
                        },
                        template='plotly_white',
                        color_discrete_sequence=px.colors.sequential.Rainbow
                        )

    figure.update_traces(
        mode='markers',
        marker=dict(
            line_width=1,
            opacity=0.75,
            size=9
        )
    )

    figure.update_layout(
        title=dict(
            text="Conceded goals",
            y=0.9,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        xaxis=dict(
            showline=True,
            showticklabels=True,
            dtick=5,
            ticks='outside',
        ),
        margin=dict(
            l=140,
            r=40,
            b=50,
            t=80
        ),
        legend=dict(
            font_size=10,
            yanchor='top',
        ),
        legend_traceorder="normal",
        hovermode='closest'
    )
    return figure


@app.callback(
    Output('graph_4', 'figure'),
    [Input('dpdwn1', 'value'), Input('dpdwn2', 'value'), Input('dpdwn3', 'value')])
def update_graph4(v1, v2, v3):
    if v3 is None:
        raise PreventUpdate

    df = leagues[int(v1)]
    df = df[df['Season'] == str(v2)]
    df = df[df.Team.isin(list(v3))]

    if df.empty:
        return px.pie(template='plotly_white')

    df1 = df[['Team', 'ShotsScored']].groupby(df['Team']).max()
    df2 = df[['Team', 'ShotsConceded']].groupby(df['Team']).max()

    df1 = df1.sort_index()
    df2 = df2.sort_index()

    figure = make_subplots(
        rows=1,
        cols=2,
        specs=[[
            {'type': 'domain'},
            {'type': 'domain'}
        ]]
    )

    figure.add_trace(
        go.Pie(
            labels=df1.index,
            values=df1.ShotsScored,
            name="Shots scored",
            marker_colors=px.colors.sequential.Rainbow, sort=False),
        1,
        1
    )

    figure.add_trace(
        go.Pie(
            labels=df2.index,
            values=df2.ShotsConceded,
            name="Shots Conceded",
            marker_colors=px.colors.sequential.Rainbow,
            sort=False),
        1,
        2
    )

    figure.update_layout(
        title=dict(
            text="% of shots between teams",
            y=0.9,
            x=0.5,
            xanchor='center',
            yanchor='top')
    )

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
