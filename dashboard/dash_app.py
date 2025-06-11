import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from AllokAcads.models import Ambient
from .models import ProfessorStatisticsDay


app = DjangoDash('dashboard')

app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'},
    children=[
        html.H1('Gráfico - 1', style={'textAlign': 'center'}),

        html.Hr(),

        html.H3('Filtro por Ambiente'),
        dcc.Dropdown(
            id='ambient-filter',
            options=[{'label': ambient.name, 'value': ambient.id} for ambient in Ambient.objects.all()],
            placeholder="Selecione um Ambiente...",
            style={'marginBottom': '20px'}
        ),
        dcc.Graph(id='stats-chart')
    ]
)
@app.callback(
    Output('stats-chart', 'figure'),
    [Input('ambient-filter', 'value')]
)
def update_chart(selected_ambient_id):
    if not selected_ambient_id:
        return px.bar(title='Por favor, selecione um ambiente para visualizar os dados.')

    stats_queryset = ProfessorStatisticsDay.objects.filter(
        ambient_id=selected_ambient_id
    ).order_by('profesor__user__name', 'day').values(
        'profesor__user__name',
        'day',
        'hours_on_campus',
        'classes_hours'
    )

    if not stats_queryset:
        return px.bar(title=f'Não há dados de estatísticas para o ambiente selecionado.')

    df = pd.DataFrame(list(stats_queryset))
    
    df.rename(columns={
        'profesor__user__name': 'Professor',
        'hours_on_campus': 'Horas no Campus',
        'classes_hours': 'Horas em Aula'
    }, inplace=True)

    df_avg = df.groupby('Professor')[['Horas no Campus', 'Horas em Aula']].mean().reset_index()

    fig = px.bar(
        df_avg,
        x='Professor',
        y=['Horas no Campus', 'Horas em Aula'],
        barmode='group', 
        title=f'Média de Horas Diárias por Professor',
        labels={'value': 'Média de Horas', 'variable': 'Métrica'},
        template='plotly_white'
    )
    
    fig.update_layout(
        xaxis_title='Professor',
        yaxis_title='Média de Horas por Dia',
        legend_title='Métricas'
    )

    return fig