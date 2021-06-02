import os
import pandas as pd
import plotly.graph_objects as go
import math
import dash
import dash_table
from dash_table import FormatTemplate
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


CURR_PATH = os.path.abspath(os.path.dirname(__file__))


def read_data(f_name):
    path = os.path.join(CURR_PATH, "data/" + f_name)
    return pd.read_csv(path)


cost_df = read_data("cost.csv")
total_wealth_df = read_data("total_wealth.csv")
wealth_25_df = read_data("wealth_25.csv")
wealth_25_50_df = read_data("wealth_25_50.csv")


def _filter_data(df, match_rt, phaseout_start, phaseout_rt, takeup_rt, leakage, roi):

    new_df = df.loc[
        (df["match_rt"] == match_rt)
        & (df["phaseout_start"] == phaseout_start)
        & (df["phaseout_rt"] == phaseout_rt)
        & (df["takeup_rt"] == takeup_rt)
        & (df["leakage"] == leakage)
        & (df["roi"] == roi)
    ]

    return new_df


def _make_graph(df):

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=df.loc["Total Wealth Generated"].round(1),
            mode="lines",
            name="Wealth (bn)",
            # hoverinfo="skip",
            line=dict(color="#d69470", width=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.columns,
            y=df.loc["Budget Estimate"].round(1),
            mode="lines",
            name="Cost (bn)",
            # hoverinfo="skip",
            line=dict(color="#9972b8", width=4),
        )
    )

    fig.update_layout(
        yaxis_title="Billions USD",
        yaxis=dict(tickformat="${,.0f}"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        font_family="HelveticaNeue",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0.01),
    )

    return fig


def filter_data(
    match_rt=0.05,
    phaseout_start=0.5,
    phaseout_rt=0.05,
    takeup_rt=0.85,
    leakage=0.3,
    roi=0.03,
):

    cost_filter = _filter_data(
        cost_df, match_rt, phaseout_start, phaseout_rt, takeup_rt, leakage, roi
    )
    total_wealth_filter = _filter_data(
        total_wealth_df, match_rt, phaseout_start, phaseout_rt, takeup_rt, leakage, roi
    )
    wealth_25_filter = _filter_data(
        wealth_25_df, match_rt, phaseout_start, phaseout_rt, takeup_rt, leakage, roi
    )
    wealth_25_50_filter = _filter_data(
        wealth_25_50_df, match_rt, phaseout_start, phaseout_rt, takeup_rt, leakage, roi
    )

    sum_df = pd.concat(
        [cost_filter, wealth_25_filter, wealth_25_50_filter, total_wealth_filter]
    )

    sum_df.index = [
        "Budget Estimate",
        "Wealth Generated for <25p",
        "Wealth Generated for 25-50p",
        "Total Wealth Generated",
    ]
    sum_df = sum_df.drop(
        ["match_rt", "phaseout_start", "phaseout_rt", "takeup_rt", "leakage", "roi"],
        axis=1,
    )

    agg_df = sum_df.cumsum(axis=1).abs()
    agg_df = agg_df.drop(["Total"], axis=1)

    fig = _make_graph(agg_df)

    return sum_df.round(1).reset_index(), fig


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    url_base_pathname=os.environ.get("URL_BASE_PATHNAME", "/"),
)

widgets = dbc.Col(
    [
        dbc.FormGroup(
            [
                dcc.Markdown(
                    """
                    #### Policy Design
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "color": "#75A074",
                    },
                ),
                dbc.Label(
                    "Matching Rate", style={"margin-left": "5%", "font-style": "italic"}
                ),
                html.Div(
                    dcc.RadioItems(
                        id="match",
                        options=[
                            {"label": "\t3%", "value": 0.03},
                            {"label": "\t4%", "value": 0.04},
                            {"label": "\t5%", "value": 0.05},
                        ],
                        value=0.03,
                        labelStyle={"display": "inline-block", "margin-left": "5%"},
                    ),
                ),
                dcc.Markdown(
                    """
                    In an employer matching program, an employer matches an employee's contributions
                    to their retirement plan, up to a percentage of the employee's annual income. In the case
                    of TSP, the federal government automatically matches between 3 and 5 percent of employees' pay.

                    ---
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "margin-top": 10,
                        "font-size": 14,
                    },
                ),
                dbc.Label(
                    "Benefit Phaseout",
                    style={"margin-left": "5%", "font-style": "italic"},
                ),
                html.Div(
                    dcc.RadioItems(
                        id="phaseout",
                        options=[
                            {"label": " Slow Phaseout", "value": 1},
                            {"label": " Fast Phaseout", "value": 2},
                        ],
                        value=1,
                        labelStyle={"display": "inline-block", "margin-left": "5%"},
                    ),
                ),
                dcc.Markdown(
                    """
                    **Slow Phaseout**. The match amount is capped for those earning more than 
                    **one half** of median earnings (in 2020, the median was approximately $52,000).
                    For every thousand dollars in income over this threshold, the 
                    match amount decreases by **three percent**.

                    **Fast Phaseout**. The match amount is capped for those earning more than **two thirds** of 
                    median earnings (in 2020, the median was approximately $52,000).
                    For every thousand dollars in income over this threshold, the 
                    match amount decreases by **five percent**.



                    ---
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "margin-top": 10,
                        "font-size": 14,
                    },
                ),
            ]
        ),
        dbc.FormGroup(
            children=[
                dcc.Markdown(
                    """
                    #### Earner Characteristics
                    """,
                    style={"margin-left": "5%", "margin-top": 20, "color": "#75A074"},
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label(
                    "Early Withdrawal",
                    style={"margin-left": "5%", "font-style": "italic"},
                ),
                html.Div(
                    dcc.Slider(
                        id="leakage",
                        value=0.3,
                        min=0,
                        max=0.4,
                        step=0.1,
                        marks={i: "{:.0%}".format(i) for i in [0, 0.1, 0.2, 0.3, 0.4]},
                        updatemode="drag",
                    ),
                    style={"width": "70%", "margin-left": "3%"},
                ),
                dcc.Markdown(
                    """
                    A key factor to consider as we simulate possible wealth creation scenarios 
                    is that lower-income individuals may need to access the wealth accumulated 
                    in their retirement accounts as emergencies arise, so that the wealth “leaks” 
                    from the accounts over time at a rate of up to 40 percent. Importantly, 
                    participants can only access their own contributions (not the government 
                    matched contributions) prior to retirement. 

                    ---
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "margin-top": 10,
                        "font-size": 14,
                    },
                ),
            ]
        ),
        dbc.Label("Takeup Rate", style={"margin-left": "5%", "font-style": "italic"}),
        html.Div(
            dcc.RadioItems(
                id="takeup",
                options=[
                    {"label": "\t70%", "value": 0.7},
                    {"label": "\t85%", "value": 0.85},
                    {"label": "\t100%", "value": 1},
                ],
                value=0.85,
                labelStyle={"display": "inline-block", "margin-left": "5%"},
            ),
        ),
        dcc.Markdown(
            """
                    Eligible earners are not automatically enrolled in the federal savings
                    match program. Some eligible earners may choose not to enroll due to
                    a lack of knowledge of the program or an inability to save. 

                    ---
                    """,
            style={
                "margin-left": "5%",
                "margin-right": "5%",
                "margin-top": 10,
                "font-size": 14,
            },
        ),
        dbc.FormGroup(
            [
                dcc.Markdown(
                    """
                    #### Market Performance
                    """,
                    style={"margin-left": "5%", "margin-top": 20, "color": "#75A074"},
                ),
                dbc.Label(
                    "Average Annual Investment Returns",
                    style={"margin-left": "5%", "font-style": "italic"},
                ),
                dcc.RadioItems(
                    id="rate",
                    options=[
                        {"label": " 3%", "value": 0.03},
                        {"label": " 5%", "value": 0.05},
                        {"label": " 7%", "value": 0.07},
                    ],
                    value=0.03,
                    labelStyle={"display": "inline-block", "margin-left": "5%"},
                ),
                dcc.Markdown(
                    """
                    The rate of return for retirement savings accounts can fluctuate 
                    based on factors such as market conditions and asset allocation. 
                    Financial advisors often tell their clients to expect an average 
                    rate of return between 5-7%. As such, in this simulation we define 
                    3% a low, baseline rate of return, 5% as the low-end of realistic 
                    returns, and 7% as the high-end of realistic returns. 

                    ---
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        # "padding-bottom": "3%",
                        "margin-top": 10,
                        "font-size": 14,
                    },
                ),
            ]
        ),
    ]
)


app.layout = dbc.Container(
    [
        dbc.Col(
            [
                dbc.Card(
                    [
                        dcc.Markdown(
                            """
                    ## Interactive Tool: The Costs and Benefits of a Federal Savings Match
                    """,
                            style={
                                "color": "#75A074",
                                "margin-left": "5%",
                                "padding-right": "5%",
                                "padding-top": "3%",
                                "padding-bottom": "2%",
                            },
                        ),
                        dcc.Markdown(
                            """
                    This interactive tool is intended to simulate the potential federal budgetary 
                    and wealth generation impacts of a wealth-building program like TSP for 
                    low- and moderate-income Americans. Enter a matching rate, benefit phaseout scenario, 
                    takeup rate, early withdrawal rate, and anticipated average annual returns to 
                    explore possible federal budgetary impacts and aggregate wealth creation of such a program.

                    ---
                    """,
                            style={
                                "margin-left": "5%",
                                "padding-right": "5%",
                            },
                        ),
                        widgets,
                        dbc.Container(
                            [
                                dcc.Markdown(
                                    """
                                    #### Results
                                    """,
                                    style={
                                        "color": "#75A074",
                                        "margin-left": "5%",
                                        "padding-right": "5%",
                                    },
                                ),
                                dbc.Label(
                                    "Annual Effects",
                                    style={"margin-left": "5%", "font-style": "italic"},
                                ),
                                html.Div(
                                    [
                                        dash_table.DataTable(
                                            id="sum_table",
                                            style_as_list_view=True,
                                            style_cell={
                                                "font-size": "12px",
                                                "font-family": "HelveticaNeue",
                                                "whiteSpace": "normal",
                                                "height": "auto"
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "rgb(248, 248, 248)",
                                                }
                                            ],
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                            style_table={
                                                "overflowX": "auto"
                                            },
                                        )
                                    ],
                                    style={"margin-left": "5%", "padding-right": "5%"},
                                ),
                                dcc.Markdown(
                                    """
                    ---
                    """,
                                style={"margin-left": "5%", "margin-right": "5%", "margin-top": 30},),
                                dbc.Label(
                                    "Cumulative Effects",
                                    style={
                                        "margin-left": "5%",
                                        "margin-top": 20,
                                        "font-style": "italic",
                                    },
                                ),
                                html.Div([dcc.Graph(id="fig")]),
                            ]
                        ),
                    ],
                    # style={"margin-left": "5%", "padding-right": "5%"},
                ),
            ],
        ),
    ],
    # style={"padding-left": "10%", "padding-right": "10%"},
)

#     ],
#     fluid=True,
#     style={"background-color": "#EAEAEA", "height": "100%"},
# )


@app.callback(
    [
        Output("sum_table", "data"),
        Output("sum_table", "columns"),
        Output("fig", "figure"),
    ],
    [
        Input("match", "value"),
        Input("phaseout", "value"),
        Input("leakage", "value"),
        Input("takeup", "value"),
        Input("rate", "value"),
    ],
)
def update(match, phaseout, leakage, takeup, rate):
    # call function that constructs figure

    if phaseout == 1:
        phaseout_start = 0.5
        phaseout_rt = 0.03

    elif phaseout == 2:
        phaseout_start = 0.67
        phaseout_rt = 0.05

    sum_table, agg_fig = filter_data(
        match_rt=match,
        phaseout_start=phaseout_start,
        phaseout_rt=phaseout_rt,
        takeup_rt=takeup,
        leakage=leakage,
        roi=rate,
    )

    sum_table = sum_table.rename(columns={"index": ""})

    columns = [{"name": str(i), "id": str(i)} for i in sum_table.columns]

    data_table = sum_table.to_dict("records")

    return data_table, columns, agg_fig


server = app.server
# turn debug=False for production
if __name__ == "__main__":
    app.run_server(debug=False)
