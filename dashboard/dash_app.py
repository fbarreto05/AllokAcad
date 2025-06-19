from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from django_plotly_dash import DjangoDash
from django.db.models import Sum

from .models import ProfessorStatistics
