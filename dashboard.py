import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

lat_long_df = pd.read_csv('countries_lat_long.csv')
df = pd.read_csv("country_wise_latest.csv") 

df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('/', '_')
df = df.merge(lat_long_df, how='left', left_on='Country_Region', right_on='Country')

world_stats = {
    'Country_Region': 'World',
    'Confirmed': df['Confirmed'].sum(),
    'Deaths': df['Deaths'].sum(),
    'Recovered': df['Recovered'].sum(),
    'Active': df['Active'].sum(),
    'New_cases': df['New_cases'].sum(),
    'New_deaths': df['New_deaths'].sum(),
    'New_recovered': df['New_recovered'].sum()
}

df_world = pd.DataFrame([world_stats])
df = pd.concat([df, df_world], ignore_index=True)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "COVID-19 Dashboard"

app.layout = dbc.Container([
    html.H1(
    "🌍 Global COVID-19 Dashboard", 
    className="text-center text-white mb-4", 
    style={'fontWeight': 'bold'}
    ),
    html.H3(
        "Powered by: MHS Bytebits", 
        className="text-center text-white mb-4", 
        style={'fontWeight': 'bold'}
    ),

    dbc.Row([
        dbc.Col([
            html.Label("Select a Country:", className="text-light", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in df['Country_Region'].unique()],
                value='World',  
                multi=False,
                style={'color': 'black'}
            ),
        ], width=3),
    ], className='mb-4', justify='center'),

    dbc.Row([
        dbc.Col(dbc.Card([
            html.H4("Total Confirmed", className="text-center text-white", style={'fontWeight': 'bold'}),
            html.H2(id='confirmed-kpi', className="text-center text-primary", style={'fontWeight': 'bold'}),
        ], color="light"), width=3),
        dbc.Col(dbc.Card([
            html.H4("Total Deaths", className="text-center text-white", style={'fontWeight': 'bold'}),
            html.H2(id='deaths-kpi', className="text-center text-danger", style={'fontWeight': 'bold'}),
        ], color="light"), width=3),
        dbc.Col(dbc.Card([
            html.H4("Total Recovered", className="text-center text-white", style={'fontWeight': 'bold'}),
            html.H2(id='recovered-kpi', className="text-center text-success", style={'fontWeight': 'bold'}),
        ], color="light"), width=3),
        dbc.Col(dbc.Card([
            html.H4("Active Cases", className="text-center text-white", style={'fontWeight': 'bold'}),
            html.H2(id='active-kpi', className="text-center text-info", style={'fontWeight': 'bold'}),
        ], color="light"), width=3),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='confirmed-map'), width=7), 
        dbc.Col(dcc.Graph(id='distribution-pie'), width=5),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='daily-cases-bar'), width=12),
        
    ]),


], fluid=True, style={'backgroundColor': '#111111'})



@app.callback(
    Output('confirmed-kpi', 'children'),
    Output('deaths-kpi', 'children'),
    Output('recovered-kpi', 'children'),
    Output('active-kpi', 'children'),
    Output('daily-cases-bar', 'figure'),
    Output('distribution-pie', 'figure'),
    Output('confirmed-map', 'figure'),  # Add output for the map
    Input('country-dropdown', 'value')
)


def update_dashboard(country):
    dff = df[df['Country_Region'] == country].copy()

    if country == 'World':
        dff = df[df['Country_Region'] == 'World']

    confirmed = f"{dff['Confirmed'].values[0]:,}"
    deaths = f"{dff['Deaths'].values[0]:,}"
    recovered = f"{dff['Recovered'].values[0]:,}"
    active = f"{dff['Active'].values[0]:,}"

    x = ['Current']


    if country == 'World':
        fig_map = px.choropleth(
            df,
            locations="Country_Region",
            locationmode="country names",
            color="Confirmed",
            hover_name="Country_Region",
            color_continuous_scale="Turbo",
            labels={'Confirmed': 'Confirmed Cases'},
            title="Confirmed COVID-19 Cases Worldwide"
        )
    else:
        fig_map = px.choropleth(
            dff,
            locations="Country_Region",
            locationmode="country names",
            color="Confirmed",
            hover_name="Country_Region",
            color_continuous_scale="Turbo",
            title=f"Confirmed COVID-19 Cases in {country}"
        )

    if country == 'World':
        geo_settings = dict(
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor='#111111',
            bgcolor='#111111',
            projection_type='natural earth'
        )
    else:
        country_data = df[df['Country_Region'] == country]
        lat = country_data['Lat'].values[0]
        lon = country_data['Long'].values[0]

        geo_settings = dict(
            center=dict(lat=lat, lon=lon),
            projection_scale=3,  
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor='#111111',
            bgcolor='#111111',
            projection_type='natural earth'
        )

    fig_map.update_layout(
        geo=geo_settings,
        paper_bgcolor='#111111',
        plot_bgcolor='#111111',
        font_color='white',
        margin=dict(l=0, r=0, t=30, b=0),
        title_x=0.5,
    )


    fig_pie = px.pie(
        names=['Active', 'Recovered', 'Deaths'],
        values=[dff['Active'].values[0], dff['Recovered'].values[0], dff['Deaths'].values[0]],
        title='Case Distribution',
        template='plotly_dark'
    )
    fig_pie.update_layout(paper_bgcolor='#111111', font_color='white')
    
    
    fig_daily = px.bar(x=['New Cases', 'New Deaths', 'New Recovered'],
                       y=[dff['New_cases'].values[0], dff['New_deaths'].values[0], dff['New_recovered'].values[0]],
                       title="Daily Cases Snapshot",
                       template='plotly_dark', color_discrete_sequence=['orange', 'red', 'green'])
    fig_daily.update_layout(paper_bgcolor='#111111', font_color='white')
    
    
    return confirmed, deaths, recovered, active,  fig_daily, fig_pie, fig_map

if __name__ == '__main__':
    app.run_server(debug=True)

