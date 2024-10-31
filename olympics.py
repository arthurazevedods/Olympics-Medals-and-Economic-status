import kagglehub
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
# Download the dataset
path = kagglehub.dataset_download("mohamedyosef101/2024-olympics-medals-and-economic-status")
#datas from 
# https://www.kaggle.com/datasets/mohamedyosef101/2024-olympics-medals-and-economic-status/data
# https://data.worldbank.org/
# https://www.kaggle.com/datasets/berkayalan/paris-2024-olympics-medals
# https://www.iban.com/country-codes
print("Path to dataset files:", path)
df = pd.read_csv(path + "/olympics-economics.csv")
print(df.head())

# Initialize the app
app = Dash(__name__)

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app.layout = html.Div([
    html.H1("Comparativo dos Países nas Olímpiadas de 2024"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df['country_code'].unique()],
        value=['USA', 'CHN'],  # Default values
        multi=True  # Allow selecting multiple countries
    ),
    
    dcc.Graph(id='medals-gpd'),
    dcc.Graph(id='medals-bar-chart'),
    dcc.Graph(id='medals-population'),
    html.Div(id='country-details', className="country-infos"),
    generate_table(df)
])

@app.callback(
    [Output('medals-bar-chart', 'figure'),
     Output('country-details', 'children'),
     Output('medals-gpd', 'figure'),
     Output('medals-population','figure')],
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
    colors = ['#8c1eff', '#ff2975', 'green', 'purple','yellow', 'orange', 'pink']  # Exemplo de cores: USA azul, CHN vermelho
    # Adicionar barras para cada país e tipo de medalha com valores
    for i, country in enumerate(selected_countries):
        country_data = filtered_df[filtered_df['country_code'] == country]

        fig.add_trace(go.Bar(
            x=['Ouro', 'Prata', 'Bronze'],
            y=[country_data['gold'].values[0], country_data['silver'].values[0], country_data['bronze'].values[0]],
            name=country,
            marker_color=colors[i % len(colors)],  # Aplica as cores de maneira cíclica
            text=[f"{country}: {int(country_data['gold'].values[0])}", 
                  f"{country}: {int(country_data['silver'].values[0])}", 
                  f"{country}: {int(country_data['bronze'].values[0])}"],  # Adiciona os valores como texto nas barras
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
    fig2 = go.Figure()
    for country in selected_countries:
        country_data = filtered_df[filtered_df['country_code'] == country]
        fig2 = px.scatter(df, x='gdp', y='total', color='country',
                        hover_name='country', size='total',
                        labels={'gdp': 'PIB (em USD)', 'total': 'Total de Medalhas'},
                        title='PIB vs Total de Medalhas - Seleção de Países')
        
        # Design do primeiro gráfico
        fig2.update_layout(
            xaxis_title='PIB (em USD)',
            yaxis_title='Total de Medalhas',
            legend_title='País',
            font=dict(size=12),
            showlegend=True,
            hovermode='closest'
        )
        # Adicionar grid
        fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig3 = px.sunburst(
        df,
        path=['country_code','population','total'],
        values='population',
        color='country',
        hover_name='country',
        title='Relação entre População & Medalhas',
        width=1200,
        height=800,
    )

    return fig, details, fig2, fig3

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
