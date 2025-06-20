from django_plotly_dash import DjangoDash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from .services import calculateProfessor

app = DjangoDash('GraficoDeBarras')
dados_dicionario = calculateProfessor.get_professor_average_periods_list()

df = pd.DataFrame(dados_dicionario)

fig = px.bar(
    df, 
    x='name', 
    y='periods_list', 
    title='Média de Períodos por Professor',
    labels={
        "name": "Professor", 
        "periods_list": "Média de Períodos" 
    }
)

fig.update_traces(texttemplate='%{y:.2f}', textposition='outside') 

app.layout = html.Div([
    dcc.Graph(
        id='grafico-media-periodos',
        figure=fig
    )
])