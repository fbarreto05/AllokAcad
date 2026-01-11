from rest_framework import serializers
from .models import ProfessorStatistics

class ProfessorStatisticsSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ProfessorStatistics
        fields = '__all__'