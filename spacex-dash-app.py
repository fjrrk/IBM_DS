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

# Dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_sites = [{'label':site, 'value':site} for site in launch_sites]
option_list = [{'label':'All Sites', 'value':'All'}]
option_list.extend(launch_sites)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                              options=option_list,
                                              placeholder='Select Launch Site',
                                              searchable=True,
                                              style={'font-size': 30}
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', 
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
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):

    if entered_site == 'All':
        tmpdf = spacex_df.groupby("Launch Site")
        tmpdf = tmpdf['class'].sum()#*100/tmpdf['class'].count()
        tmpdf = tmpdf.reset_index()

        fig = px.pie(tmpdf, 
                    values='class', 
                    names='Launch Site', 
                    title='Proportion of Successful Landings by Launch Site'
                    )

        return fig
    
    else:
        tmpdf = spacex_df[spacex_df['Launch Site']==entered_site]
        tmpdf = tmpdf.groupby('class')['class'].count()
        tmpdf.name = 'outcomes'
        tmpdf = tmpdf.reset_index()

        # return the outcomes piechart for a selected site
        fig = px.pie(tmpdf, 
                    values='outcomes', 
                    names='class', 
                    title=f"Proportion of Successful Landings for {entered_site}"
                    )
        
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])
def get_scatter_plot(entered_site, payload):

    if entered_site=='All':
        tmpdf = spacex_df[(spacex_df["Payload Mass (kg)"]>=payload[0]) & (spacex_df["Payload Mass (kg)"]<=payload[1])]
        fig = px.scatter(tmpdf, x="Payload Mass (kg)", y="class", color="Booster Version Category", title="Correlation Between Landing Success and Payload for All Sites")
        
        return fig

    else:
        tmpdf = spacex_df[(spacex_df['Launch Site']==entered_site) & (spacex_df["Payload Mass (kg)"]>=payload[0]) & (spacex_df["Payload Mass (kg)"]<=payload[1])]
        fig = px.scatter(tmpdf, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=f"Correlation Between Landing Success and Payload for {entered_site}")
        
        return fig


# Run the app
if __name__ == '__main__':
    app.run()
