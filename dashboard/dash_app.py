from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from django_plotly_dash import DjangoDash
from django.db.models import Sum

from .models import ProfessorStatisticsDay

app1 = DjangoDash('HistogramaProfessores')
app1.layout = html.Div([
    dcc.Graph(id='histograma-distribuicao'),
    html.Div(id='timetable-id-storage-1', style={'display': 'none'})
])

@app1.callback(Output('histograma-distribuicao', 'figure'), [Input('timetable-id-storage-1', 'children')])
def update_histogram(timetable_id):
    if not timetable_id: return go.Figure()
    
    workloads = ProfessorStatisticsDay.objects.filter(timetable_id=timetable_id).values('professor').annotate(total_periods=Sum('number_of_periods'))
    if not workloads: return go.Figure()

    data = [item['total_periods'] for item in workloads]
    fig = go.Figure(data=[go.Histogram(x=data, marker_color='#007BFF', opacity=0.75)])
    fig.update_layout(title_text='Distribuição da Carga Horária', template='plotly_white', margin=dict(t=40, b=40, l=40, r=20))
    return fig