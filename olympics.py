import kagglehub
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Download latest version
path = kagglehub.dataset_download("mohamedyosef101/2024-olympics-medals-and-economic-status")

print("Path to dataset files:", path)
df = pd.read_csv(path + "/olympics-economics.csv")
print(df.head())

# Initialize the app
app = Dash()

app.layout = html.Div([
    html.H1("Olympic Countries Dataset"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df['country_code']],
        value='USA',  # Default value
        multi=False
    ),
    dcc.Graph(id='medals-bar-chart'),
    html.Div(id='country-details')
])

@app.callback(
    Output('medals-bar-chart', 'figure'),
    Output('country-details', 'children'),
    Input('country-dropdown', 'value')
)
def update_output(selected_country):
    # Filter the DataFrame for the selected country
    filtered_df = df[df['country_code'] == selected_country]

    # Create a bar chart for the selected country
    fig = px.bar(filtered_df, x=['gold', 'silver', 'bronze'], 
                  y='country_code', 
                  title=f'Medals won by {selected_country}',
                  labels={'x': 'Number of Medals', 'y': 'Country'},
                  color_discrete_sequence=['gold', 'silver', 'brown'])

    # Create a summary of the selected country
    details = html.Div([
        html.P(f"Country Code: {filtered_df['country_code'].values[0]}"),
        html.P(f"Gold Medals: {filtered_df['gold'].values[0]}"),
        html.P(f"Silver Medals: {filtered_df['silver'].values[0]}"),
        html.P(f"Bronze Medals: {filtered_df['bronze'].values[0]}"),
        html.P(f"Total Medals: {filtered_df['total'].values[0]}"),
        html.P(f"GDP: {filtered_df['gdp'].values[0]} (Year: {filtered_df['gdp_year'].values[0]})"),
        html.P(f"Population: {filtered_df['population'].values[0]}")
    ])

    return fig, details

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)