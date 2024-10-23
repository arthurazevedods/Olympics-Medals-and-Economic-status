import kagglehub
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

# Download the dataset
path = kagglehub.dataset_download("mohamedyosef101/2024-olympics-medals-and-economic-status")

print("Path to dataset files:", path)
df = pd.read_csv(path + "/olympics-economics.csv")
print(df.head())

# Initialize the app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Olympic Countries Comparison"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df['country_code'].unique()],
        value=['USA', 'CHN'],  # Default values
        multi=True  # Allow selecting multiple countries
    ),
    dcc.Graph(id='medals-bar-chart'),
    html.Div(id='country-details')
])

@app.callback(
    [Output('medals-bar-chart', 'figure'),
     Output('country-details', 'children')],
    [Input('country-dropdown', 'value')]
)
def update_output(selected_countries):
    if len(selected_countries) < 2:
        return {}, "Por favor, selecione dois países para comparar."

    # Filter the DataFrame for the selected countries
    filtered_df = df[df['country_code'].isin(selected_countries)]

    # Create a bar chart using graph_objects
    fig = go.Figure()

    # Cores específicas para cada país
    colors = ['blue', 'red', 'green', 'purple','yellow', 'orange', 'pink']  # Exemplo de cores: USA azul, CHN vermelho
    # Adicionar barras para cada país e tipo de medalha com valores
    for i, country in enumerate(selected_countries):
        country_data = filtered_df[filtered_df['country_code'] == country]

        fig.add_trace(go.Bar(
            x=['Gold', 'Silver', 'Bronze'],
            y=[country_data['gold'].values[0], country_data['silver'].values[0], country_data['bronze'].values[0]],
            name=country,
            marker_color=colors[i % len(colors)],  # Aplica as cores de maneira cíclica
            text=[f"{country}: {int(country_data['gold'].values[0])}", 
                  f"{country}: {int(country_data['gold'].values[0])}", 
                  f"{country}: {int(country_data['gold'].values[0])}"],  # Adiciona os valores como texto nas barras
            textposition='auto'  # Posiciona os textos automaticamente (dentro das barras)
        ))

    # Criação do título dinâmico com todos os países selecionados
    title = 'Comparação de Medalhas: ' + ' vs '.join(selected_countries)

    # Customizando o layout do gráfico
    fig.update_layout(
        title=title,
        xaxis_title='Tipo de Medalha',
        yaxis_title='Número de Medalhas',
        barmode='group',  # Gráfico de barras agrupadas
        legend_title_text='País'  # Adiciona legenda para facilitar a distinção
    )

    
    details = []
    for country in selected_countries:
        country_data = filtered_df[filtered_df['country_code'] == country]
        details.append(html.Div([
            html.H3(f"Detalhes do país: {country}"),
            html.P(f"Sigla do País: {country_data['country_code'].values[0]}"),
            html.P(f"Medalhas de Ouro: {country_data['gold'].values[0]}"),
            html.P(f"Medalhas de Prata: {country_data['silver'].values[0]}"),
            html.P(f"Medalhas de Bronze: {country_data['bronze'].values[0]}"),
            html.P(f"Total de Medalhas: {country_data['total'].values[0]}"),
            html.P(f"PIB: {country_data['gdp'].values[0]} (Ano: {country_data['gdp_year'].values[0]})"),
            html.P(f"População: {country_data['population'].values[0]}")
        ]))

    return fig, details

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
