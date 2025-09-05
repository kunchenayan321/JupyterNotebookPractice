# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # TASK 1: Add a dropdown list to enable Launch Site selection
dcc.Dropdown(
    id='site-dropdown',
    options=[{'label': 'All Sites', 'value': 'ALL'}] +
            [{'label': site, 'value': site}
             for site in sorted(spacex_df['Launch Site'].unique())],
    value='ALL',                              # default shows all sites
    placeholder='Select a Launch Site here',  # helper text
    searchable=True
),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                               dcc.RangeSlider(
                                id='payload-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                value=[min_payload, max_payload]
),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',           # sums 1s (successes) by site
            names='Launch Site',
            title='Total Success Launches by Site'
        )
        return fig

    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    fig = px.pie(
        filtered_df,
        names='class',               # shows 0 vs 1 counts for the site
        title=f'Success vs. Failure for site {entered_site}'
    )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range

    # Filter by payload range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # If a specific site is chosen, filter by that site
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]

    title = ('Correlation between Payload and Launch Outcome'
             if entered_site == 'ALL'
             else f'Payload vs Outcome for {entered_site}')

    # Scatter: x = payload, y = class (0/1), color by booster category
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome (1=Success, 0=Fail)'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
