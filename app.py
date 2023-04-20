import dash
import duckdb
import pandas as pd
import plotly.express as px
from dash import dcc, Output, Input
from dash import html


def read_data_from_db():
    con = duckdb.connect('characters.duckdb')
    df = pd.read_sql("SELECT * FROM characters", con)
    con.close()
    return df


external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "World of Warcraft Analytics"

server = app.server

data = read_data_from_db()

classes = data["character_class"].sort_values().unique()
guilds = data["guild"].str.cat(data["realm"], sep=" - ").sort_values().unique()


def create_level_histogram(character_data):
    return px.histogram(character_data,
                        x="level",
                        nbins=60,
                        title="Character Level Distribution")


def create_class_pie_chart(character_data):
    class_breakdown = character_data['character_class'].value_counts().reset_index()
    class_breakdown.columns = ['character_class', 'count']
    return px.pie(class_breakdown,
                  values='count', names='character_class',
                  hole=0.3,
                  title='Class Breakdown')


def create_spec_pie_chart(character_data):
    spec_breakdown = character_data['active_spec'].value_counts().reset_index()
    spec_breakdown.columns = ['active_spec', 'count']
    fig_spec_pie = px.pie(spec_breakdown,
                          names='active_spec',
                          values='count',
                          hole=0.3,
                          title='Active Specialization Breakdown')
    return fig_spec_pie


def create_total_characters(character_data):
    return {
        "data": [
            {
                "type": "indicator",
                "mode": "number",
                "value": len(character_data),
                "number": {"font": {"size": 75}},
                "title": {"text": "Total Characters"},
            }
        ]
    }


def create_average_item_level(character_data):
    average_item_level_filtered = character_data["average_item_level"].mean()

    return {
        "data": [
            {
                "type": "indicator",
                "mode": "number",
                "value": average_item_level_filtered,
                "number": {"font": {"size": 75}},
                "title": {"text": "Average Item Level"},
            }
        ]
    }


@app.callback(
    Output("level_histogram", "figure"),
    Output("class_pie", "figure"),
    Output("total_characters", "figure"),
    Output("average_item_level", "figure"),
    Input("class-filter", "value"),
    Input("guild-filter", "value"),
    Input("level-70-filter", "value"),
)
def update_charts(character_class: str | None, guild: str | None, level_70_filter):
    filtered_data = data

    if guild:
        guild_name, realm_name = guild.split(" - ")
        filtered_data = data.query(
            "guild == @guild_name and realm == @realm_name"
        )

    if character_class is not None:
        filtered_data = filtered_data.query("character_class == @character_class")

    if "filter" in level_70_filter:
        filtered_data = filtered_data.query("level == 70")

    total_characters_indicator = create_total_characters(filtered_data)
    average_item_level_indicator = create_average_item_level(filtered_data)
    level_histogram = create_level_histogram(filtered_data)

    if character_class:
        class_pie_chart = create_spec_pie_chart(filtered_data)
    else:
        class_pie_chart = create_class_pie_chart(filtered_data)

    return level_histogram, class_pie_chart, total_characters_indicator, average_item_level_indicator


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🧙⚔️🧙‍♀️", className="header-emoji"),
                html.H1(
                    children="World of Warcraft", className="header-title"
                ),
                html.P(
                    children=(
                        "Analyze the World of Warcraft characters"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Classes", className="menu-title"),
                        dcc.Dropdown(
                            id="class-filter",
                            options=[
                                {"label": character_class, "value": character_class}
                                for character_class in classes
                            ],
                            clearable=True,
                            className="dropdown",
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Guilds", className="menu-title"),
                        dcc.Dropdown(
                            id="guild-filter",
                            options=[
                                {"label": guild, "value": guild}
                                for guild in guilds
                            ],
                            clearable=True,
                            className="dropdown",
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Level 70 Only", className="menu-title"),
                        dcc.Checklist(
                            id="level-70-filter",
                            options=[
                                {"label": "Filter Level 70", "value": "filter"}
                            ],
                            value=[],
                            className="checkbox",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id="total_characters")
                    ],
                    className="graph-container"
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="average_item_level")
                    ],
                    className="graph-container"
                ),
            ],
            className="row"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id="level_histogram")
                    ],
                    className="graph-container"
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="class_pie")
                    ],
                    className="graph-container"
                ),
            ],
            className="row"
        ),
    ])

if __name__ == "__main__":
    app.run_server(debug=False)
