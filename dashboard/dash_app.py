from django_plotly_dash import DjangoDash
from dash import dcc, html
import plotly.express as px
import pandas as pd

app = DjangoDash("GraficoDeBarras")

def generate(initial_arguments = None):
        if not initial_arguments:
            return html.Div('Erro: O aplicativo Dash foi carregado sem os dados necessários.')
        
        data = initial_arguments.get('dash_data_graph_bar', {}).get('data')

        if not data: 
            return html.Div('Não há dados')
        
        df = pd.DataFrame(data)
        
        fig = px.bar(
            df, 
            x = 'name',
            y = 'periods_list',
            title = 'Média de Períodos por Professor',
            labels={
                "name": "Professor",
                "periods_list": "Média de Períodos",
            }
        )
        
        return html.Div([
            dcc.Graph(figure = fig)
        ])

app.layout = generate