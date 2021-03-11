import os
import plotly.graph_objects as go
import math
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


def make_fig(income=30000, nom_rate=0.03, contrib=0.05, match=0.03, leakage=0.4):

    match_amt = min(contrib, match)
    total_contrib = match_amt + contrib
    wealth = [0]
    for year in range(1, 41):
        assets_year = (wealth[-1] * (1 + nom_rate)) + (
            total_contrib * income * (1 - leakage)
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
        margin={"t": 50},
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
                    style={"margin-left": "5%", "margin-top": 10, "color": "#3C84A2"},
                ),
                dbc.Label(
                    "Matching Rate", style={"margin-left": "5%", "font-style": "italic"}
                ),
                html.Div(
                    dcc.Slider(
                        id="match",
                        value=0.03,
                        min=0,
                        max=0.05,
                        step=0.01,
                        marks={
                            i: "{:.0%}".format(i)
                            for i in [0, 0.01, 0.02, 0.03, 0.04, 0.05]
                        },
                        updatemode="drag",
                    ),
                    style={"width": "70%", "margin-left": "3%"},
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
                dbc.Label("Wages", style={"margin-left": "5%", "font-style": "italic"}),
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
                    "Savings Rate", style={"margin-left": "5%", "font-style": "italic"}
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
                    The savings rate is the percentage of annual income that an employee sets aside in their retirement
                    savings fund. To take full advantage of a government match, the employee
                    must contribute at least as much as the government offers to match. The match rate you selected
                    above is denoted by the ** symbol. 
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
                dbc.Label(
                    "Early Withdrawal",
                    style={"margin-left": "5%", "font-style": "italic"},
                ),
                html.Div(
                    dcc.Slider(
                        id="leakage",
                        value=0.4,
                        min=0,
                        max=0.5,
                        step=0.1,
                        marks={
                            i: "{:.0%}".format(i) for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5]
                        },
                        updatemode="drag",
                    ),
                    style={"width": "70%", "margin-left": "3%"},
                ),
                dcc.Markdown(
                    """
                    A key factor to consider as we simulate possible wealth creation scenarios is that individuals, 
                    especially lower-income individuals, tend to need to access the wealth accumulated in 
                    their retirement accounts as emergencies arise, so that the wealth “leaks” from the 
                    accounts over time at a rate of up to 40 percent.

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
                    #### Economic Conditions
                    """,
                    style={"margin-left": "5%", "margin-top": 20, "color": "#3C84A2"},
                ),
                dbc.Label(
                    "Annual Investment Returns",
                    style={"margin-left": "5%", "font-style": "italic"},
                ),
                dcc.RadioItems(
                    id="rate",
                    options=[
                        {"label": " High", "value": 0.07},
                        {"label": " Low", "value": 0.03},
                    ],
                    value=0.07,
                    labelStyle={"display": "inline-block", "margin-left": "5%"},
                ),
                dcc.Markdown(
                    """
                    The rate of return for retirement savings accounts can fluctuate based on factors such as
                    market conditions and asset allocation. In this simulation, we define a "high" annual rate of
                    return as 7% and a "low" annual rate of return as 3%. 

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
                    ## Building Wealth with a Federal Savings Match
                    """,
                            style={
                                "color": "#3C84A2",
                                "padding-left": "5%",
                                "padding-right": "5%",
                                "padding-top": "3%",
                                "padding-bottom": "3%",
                            },
                        ),
                        dcc.Markdown(
                            """
                    *What if low-income American workers had access to a wealth-building vehicle like the Federal
                    Employees' Thrift Savings Plan (TSP)?*


                    A major factor in America's accelerating wealth inequality is the lack of retirement savings by millions of Americans. 
                    For the bottom 50 percent of the wealth distribution, the median retirement savings account balance is $0.
                    One way to encourage low-income workers to save, and to facilitate faster savings growth, is to offer a savings
                    plan in which the employer chips in to the account. Federal, state, and local governments have been successful in providing efficient and adequate 
                    savings vehicles for their workers. For example, TSP, a contribution savings plan offered by the federal government, 
                    has successfully generated wealth for many federal employees and members of the military. This tool is intended to demonstrate 
                    the potential impact of a wealth-building vehicle like TSP for all low-income Americans.

                    ---
                    """,
                            style={
                                "padding-left": "5%",
                                "padding-right": "5%",
                                "padding-bottom": "3%",
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
                                        "color": "#3C84A2",
                                    },
                                ),
                                dcc.Graph(
                                    id="chart",
                                    config={"displayModeBar": False},
                                ),
                                dbc.Label(
                                    "Summary",
                                    style={"font-style": "italic"},
                                ),
                                html.Li(
                                    "",
                                    id="bullet_1",
                                    style={"margin-left": 20},
                                ),
                                html.Li(
                                    "",
                                    id="bullet_2",
                                    style={"margin-left": 20},
                                ),
                                dbc.Label(
                                    "Wealth Creation",
                                    style={"padding-top": 8, "font-style": "italic"},
                                ),
                                html.Li(
                                    "",
                                    id="bullet_3",
                                    style={"margin-left": 20},
                                ),
                            ],
                            style={"padding-left": "7%", "padding-bottom": "10%"},
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
        Output("bullet_1", "children"),
        Output("bullet_2", "children"),
        Output("bullet_3", "children"),
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
    wealth_tot = sum(wealth)

    bullet_1 = "{:.0%} Federal Savings Match".format(match)
    bullet_2 = "${:0,.0f} annual savings (before early withdrawal)".format(saving_amt)
    bullet_3 = "Over 40 years, ${:0,.0f} of new wealth will be created".format(
        wealth_tot
    )

    wages_amt = "${:0,.0f}".format(wages)
    wages_marks = {0: "$0", wages: wages_amt, 52000: "$52,000"}

    if match == 0:
        saving_marks = {
            0: "0%**",
            0.02: "2%",
            0.04: "4%",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }
    if match == 0.01:
        saving_marks = {
            0: "0%",
            0.01: "**",
            0.02: "2%",
            0.04: "4%",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }
    elif match == 0.02:
        saving_marks = {
            0: "0%",
            0.02: "2%**",
            0.04: "4%",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }
    elif match == 0.03:
        saving_marks = {
            0: "0%",
            0.02: "2%",
            0.03: "**",
            0.04: "4%",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }
    elif match == 0.04:
        saving_marks = {
            0: "0%",
            0.02: "2%",
            0.04: "4%**",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }
    elif match == 0.05:
        saving_marks = {
            0: "0%",
            0.02: "2%",
            0.04: "4%",
            0.05: "**",
            0.06: "6%",
            0.08: "8%",
            0.1: "10%",
        }

    return (fig, bullet_1, bullet_2, bullet_3, saving_marks, wages_marks)


server = app.server
# turn debug=False for production
if __name__ == "__main__":
    app.run_server()
