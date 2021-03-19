import os
import plotly.graph_objects as go
import math
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


def make_fig(income=30000, nom_rate=0.03, contrib=0.03, match=0.03, leakage=0.4):

    match_amt = min(contrib, match)

    wealth = [0]
    for year in range(1, 41):
        assets_year = (
            (wealth[-1] * (1 + nom_rate))
            + (match_amt * income)
            + (contrib * income * (1 - leakage))
        )
        wealth.append(assets_year)

    trace = go.Bar(
        x=list(range(0, 41)),
        y=wealth,
        width=0.8,
        marker_color="#3C84A2",
        opacity=0.85,
        hovertemplate="Year %{x}<br>" + "New Savings: $%{y:,.0f}<extra></extra>",
    )

    axis_max = int(math.ceil(wealth[-1] / 100000)) * 100000

    layout = go.Layout(
        yaxis_title="New Savings",
        xaxis_title="Years Since First Investment",
        plot_bgcolor="white",
        font={"family": "Lato"},
        margin={"t": 50, "b": 30},
    )
    fig = go.Figure(data=trace, layout=layout)
    fig.update_yaxes(range=[0, axis_max])

    fig.update_layout(
        yaxis_tickprefix="$",
        yaxis_tickformat=",.",
    )

    return fig, wealth


app = dash.Dash(
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
                        "color": "#3C84A2",
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
            ]
        ),
        dbc.FormGroup(
            id="wages_container",
            children=[
                dcc.Markdown(
                    """
                    #### Earner Characteristics
                    """,
                    style={"margin-left": "5%", "margin-top": 20, "color": "#3C84A2"},
                ),
                dbc.FormGroup(
                    [
                        dbc.Label(
                            "Savings Rate (the ** symbol refers to the match rate you selected above)",
                            style={"margin-left": "5%", "font-style": "italic"},
                        ),
                        html.Div(
                            dcc.Slider(
                                id="savings",
                                value=0.03,
                                min=0,
                                max=0.1,
                                step=0.01,
                                marks={
                                    0: "0%",
                                    0.02: "2%",
                                    0.03: "**",
                                    0.04: "4%",
                                    0.06: "6%",
                                    0.08: "8%",
                                    0.1: "10%",
                                },
                                updatemode="drag",
                            ),
                            style={"width": "70%", "margin-left": "3%"},
                        ),
                        dcc.Markdown(
                            """
                    The savings rate is the percentage of annual income that an employee 
                    sets aside in their retirement savings fund. The government will only match 
                    up to your savings rate regardless of which match rate you 
                    choose. Therefore, to take full advantage of a government match, you must 
                    have a savings rate at least as high as the match rate. Evidence has 
                    shown that most low-income federal workers in TSP do just this, with a 
                    match rate of 5% and an average savings rate of 4.6%. 
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
                dbc.Label(
                    "Income", style={"margin-left": "5%", "font-style": "italic"}
                ),
                html.Div(
                    dcc.Slider(
                        id="wages",
                        value=30000,
                        min=0,
                        max=52000,
                        step=1000,
                        marks={0: "$0", 30000: "$30,000", 52000: "$52,000"},
                        updatemode="drag",
                    ),
                    style={"width": "70%", "margin-left": "3%"},
                ),
                dcc.Markdown(
                    """
                    As a federal savings match policy would target low-income workers, we cap the allowable
                    income at $52,000, approximately the median annual income for full-time workers as of Fall 2020.
                    """,
                    style={
                        "margin-left": "5%",
                        "margin-right": "5%",
                        "margin-top": 10,
                        "font-size": 14,
                    },
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
                        value=0.4,
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
        dbc.FormGroup(
            [
                dcc.Markdown(
                    """
                    #### Market Performance
                    """,
                    style={"margin-left": "5%", "margin-top": 20, "color": "#3C84A2"},
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
                    ## Interactive Tool: Building Wealth with a Federal Savings Match
                    """,
                            style={
                                "color": "#3C84A2",
                                "padding-left": "6%",
                                "padding-right": "5%",
                                "padding-top": "3%",
                                "padding-bottom": "2%",
                            },
                        ),
                        dcc.Markdown(
                            """
                    This interactive tool is intended to simulate the potential impact of 
                    access to a wealth-building program like TSP for low- and moderate-income 
                    Americans. Enter a matching rate, annual income, savings rate, early 
                    withdrawal, and anticipated average annual returns to explore possible 
                    retirement savings balances with such a program. 

                    ---
                    """,
                            style={
                                "padding-left": "6%",
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
                                    style={"color": "#3C84A2"},
                                ),
                                dbc.Label(
                                    "",
                                    id="summary",
                                    style={
                                        "font-style": "italic",
                                        "font-weight": "bold",
                                        "font-size": 16,
                                    },
                                ),
                                dcc.Graph(
                                    id="chart",
                                    config={"displayModeBar": False},
                                    style={"margin-bottom": "10%"},
                                ),
                            ],
                            style={"padding-left": "5%", "padding-right": "5%"},
                        ),
                    ]
                ),
            ],
            align="center",
            style={"padding-left": "10%", "padding-right": "10%"},
        ),
    ],
    fluid=True,
    style={"background-color": "#EAEAEA", "height": "100%"},
)


@app.callback(
    [
        Output("chart", "figure"),
        Output("summary", "children"),
        Output("savings", "marks"),
        Output("wages", "marks"),
    ],
    [
        Input("match", "value"),
        Input("rate", "value"),
        Input("wages", "value"),
        Input("savings", "value"),
        Input("leakage", "value"),
    ],
)
def update(match, rate, wages, savings, leakage):
    # call function that constructs figure

    fig, wealth = make_fig(wages, rate, savings, match, leakage)

    saving_amt = wages * savings
    wealth_40 = wealth[-1]

    summary = "After 40 years of participation in a federal savings match program, assets \
    grow to ${:0,.0f}, before taxes and fees.".format(
        wealth_40
    )

    wages_amt = "${:0,.0f}".format(wages)
    wages_marks = {0: "$0", wages: wages_amt, 52000: "$52,000"}

    if match == 0.03:
        saving_marks = {
            0: "0%",
            0.01: "",
            0.02: "2%",
            0.03: "**",
            0.04: "4%",
            0.05: "",
            0.06: "6%",
            0.07: "",
            0.08: "8%",
            0.09: "",
            0.1: "10%",
        }
    elif match == 0.04:
        saving_marks = {
            0: "0%",
            0.01: "",
            0.02: "2%",
            0.03: "",
            0.04: "4%**",
            0.05: "",
            0.06: "6%",
            0.07: "",
            0.08: "8%",
            0.09: "",
            0.1: "10%",
        }
    elif match == 0.05:
        saving_marks = {
            0: "0%",
            0.01: "",
            0.02: "2%",
            0.03: "",
            0.04: "4%",
            0.05: "**",
            0.06: "6%",
            0.07: "",
            0.08: "8%",
            0.09: "",
            0.1: "10%",
        }

    return (fig, summary, saving_marks, wages_marks)


server = app.server
# turn debug=False for production
if __name__ == "__main__":
    app.run_server(debug=False)
