from django.shortcuts import render
from .services import calculateProfessor, calculateSpace
from django.http import JsonResponse
from django.shortcuts import redirect
from AllokAcads.models import User
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
from .preferences_service import (
    get_all_metrics, get_filtered_metrics, get_filter_options,
    parse_failure_reasons, get_logs_summary, get_operational_metrics
)


def professor_dashboard_view(request): 
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
        
        if user:   
            user_ambients = calculateProfessor.get_user_ambient_list(user)
        else:
            user_ambients = []
        
        for ambient in user_ambients:
            calculateProfessor.update_statistics_semester(ambient.id)
        
        if user_ambients:
            first_ambient = user_ambients[0]
        
        else:
            first_ambient = None
        
        if first_ambient:
            ambient_semeters = calculateProfessor.get_semester_list(ambient_id = first_ambient.id)
            average_class_interval = calculateProfessor.average_periods_interval(ambient_id = first_ambient.id)
            average_classes = calculateProfessor.average_periods(ambient_id = first_ambient.id)
            number_of_professors = calculateProfessor.number_professors(ambient_id = first_ambient.id)
            timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = first_ambient.id)
            bar_graph_data = calculateProfessor.get_total_professor_classes(ambient_id = first_ambient.id)
            polar_graph_data = calculateProfessor.get_classes_by_day(ambient_id = first_ambient.id)
            scatter_graph_data = calculateProfessor.get_professor_efficiency_and_classes_list(ambient_id = first_ambient.id)
            line_graph_data = calculateProfessor.get_professor_metrics_evolution(ambient_id = first_ambient.id)
        
        else:
            ambient_semeters = []
            average_class_interval = None
            average_classes = None
            number_of_professors = None
            timetable_quality = None
            first_ambient = None
            bar_graph_data = []
            polar_graph_data = []
            scatter_graph_data = []
            line_graph_data = []
            
            
        context = {
            'average_class_interval': average_class_interval, 
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
            'ambients': user_ambients,
            'semesters': ambient_semeters,
            'selected_ambient': first_ambient,
            'user': user,
            'bar_graph_data': bar_graph_data,
            'polar_graph_data': polar_graph_data, 
            'scatter_graph_data': scatter_graph_data, 
            'line_graph_data': line_graph_data,
        }
        return render(request, 'dashboard/professor.html', context)
    else:
        return redirect('/')

def update_professor_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    semeter_id = request.GET.get('semester', None)
    
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
    else:
        user = None
        
    if user:
        user_ambients = calculateProfessor.get_user_ambient_list(user)
    else:
        user_ambients = []
        
    selected_ambient = None
    
    if ambient_id:
        for ambient in user_ambients:
            if str(ambient.id) == str(ambient_id):
                selected_ambient = ambient
                break
    
    calculateProfessor.update_statistics_semester(ambient_id=selected_ambient.id)
    average_class_interval = calculateProfessor.average_periods_interval(ambient_id = selected_ambient.id)
    average_classes = calculateProfessor.average_periods(ambient_id = selected_ambient.id)
    number_of_professors = calculateProfessor.number_professors(ambient_id = selected_ambient.id)
    timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = selected_ambient.id)
    bar_graph_data = calculateProfessor.get_total_professor_classes(ambient_id = selected_ambient.id)
    polar_graph_data = calculateProfessor.get_classes_by_day(ambient_id = selected_ambient.id)
    scatter_graph_data = calculateProfessor.get_professor_efficiency_and_classes_list(ambient_id = selected_ambient.id)
    line_graph_data = calculateProfessor.get_professor_metrics_evolution(ambient_id = selected_ambient.id)
    
    data = {
        'indicators': {
            'average_class_interval': average_class_interval, 
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
        },
        'bar_graph_data': bar_graph_data,
        'polar_graph_data': polar_graph_data,  
        'scatter_graph_data': scatter_graph_data,
        'line_graph_data': line_graph_data,
    }
    return JsonResponse(data)

def space_dashboard_view(request):
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
        
        if user:   
            user_ambients = calculateProfessor.get_user_ambient_list(user)
        
        else:
            user_ambients = []
        
        for ambient in user_ambients:
            calculateSpace.update_statistics_semester(ambient.id)
        
        if user_ambients:
            first_ambient = user_ambients[0]
        
        else:
            first_ambient = None
            
       
        if first_ambient:
            ambient_semeters = calculateProfessor.get_semester_list(ambient_id = first_ambient.id)
            total_spaces = calculateSpace.get_total_periods_spaces(ambient_id = first_ambient.id)
            occupied_spaces = calculateSpace.get_occupied_spaces(ambient_id = first_ambient.id)
            occupation_rate = calculateSpace.get_occupation_rate(ambient_id = first_ambient.id)
            space_efficiency = calculateSpace.get_space_efficiency(ambient_id = first_ambient.id)
            bar_graph_data = calculateSpace.get_total_space_classes(ambient_id = first_ambient.id)
            polar_graph_data = calculateSpace.get_spaces_classes_by_day(ambient_id = first_ambient.id)
            scatter_graph_data = calculateSpace.get_space_efficiency_and_classes_list(ambient_id = first_ambient.id)
            line_graph_data = calculateSpace.get_space_metrics_evolution(ambient_id = first_ambient.id)
            
        else:
            ambient_semeters = []
            total_spaces = None
            occupied_spaces = None
            occupation_rate = None
            space_efficiency = None
            first_ambient = None
            
        context = {
            'total_periods': total_spaces,
            'occupied_spaces': occupied_spaces,     
            'occupation_rate': occupation_rate,
            'space_efficiency': space_efficiency,
            'user': user,
            'ambients': user_ambients,
            'selected_ambient': first_ambient,
            'semesters': ambient_semeters,
            'bar_graph_data': bar_graph_data,
            'polar_graph_data': polar_graph_data,
            'scatter_graph_data': scatter_graph_data,
            'line_graph_data_': line_graph_data,
        }
        return render(request, 'dashboard/space.html', context)
    else:
        return redirect('/')

def update_space_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
    else:
        user = None
        
    if user:
        user_ambients = calculateProfessor.get_user_ambient_list(user)
    else:
        user_ambients = []
        
    selected_ambient = None
    
    if ambient_id:
        for ambient in user_ambients:
            if str(ambient.id) == str(ambient_id):
                selected_ambient = ambient
                break
            
    calculateSpace.update_statistics_semester(ambient_id = selected_ambient.id)
    total_spaces = calculateSpace.get_total_spaces(ambient_id = selected_ambient.id)
    occupied_spaces = calculateSpace.get_occupied_spaces(ambient_id = selected_ambient.id)
    occupation_rate = calculateSpace.get_occupation_rate(ambient_id = selected_ambient.id)
    space_efficiency = calculateSpace.get_space_efficiency(ambient_id = selected_ambient.id)
    bar_graph_data = calculateSpace.get_total_space_classes(ambient_id = selected_ambient.id)
    polar_graph_data = calculateSpace.get_spaces_classes_by_day(ambient_id = selected_ambient.id)
    scatter_graph_data = calculateSpace.get_space_efficiency_and_classes_list(ambient_id = selected_ambient.id)
    line_graph_data = calculateSpace.get_space_metrics_evolution(ambient_id = selected_ambient.id)

    data = {
        'indicators': { 
            'total_periods': total_spaces,
            'occupied_spaces': occupied_spaces,     
            'occupation_rate': occupation_rate,
            'space_efficiency': space_efficiency,
        },
        'bar_graph_data': bar_graph_data,
        'polar_graph_data': polar_graph_data,
        'scatter_graph_data': scatter_graph_data,
        'line_graph_data': line_graph_data,
    }    
    
  
    return JsonResponse(data)


def preferences_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('/')
        
    user = User.objects.filter(userid=request.user.username).first()
    user_ambients = calculateProfessor.get_user_ambient_list(user) if user else []
    
    first_ambient = user_ambients[0] if user_ambients else None
    
    context = {
        'user': user,
        'ambients': user_ambients,
        'selected_ambient': first_ambient,
    }
    
    if first_ambient:
        metrics = get_all_metrics(first_ambient.id)
        filter_options = get_filter_options(first_ambient.id)
        failure_reasons = parse_failure_reasons(first_ambient.id)
        operational_metrics = get_operational_metrics(first_ambient.id)
        
        context.update({
            'metrics': metrics,
            'filter_options': filter_options,
            'failure_reasons': failure_reasons,
            'operational_metrics': operational_metrics,
        })
        
    return render(request, 'dashboard/preferences.html', context)


def update_preferences_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not_authenticated"}, status=401)
        
    ambient_id = request.GET.get('ambient')
    filter_type = request.GET.get('filter_type')
    filter_id = request.GET.get('filter_id')
    
    if not ambient_id:
        return JsonResponse({"error": "ambient_id_required"}, status=400)
        
    metrics = get_filtered_metrics(ambient_id, filter_type, filter_id)
    failure_reasons = parse_failure_reasons(ambient_id, filter_type, filter_id)
    
    return JsonResponse({
        'metrics': metrics,
        'failure_reasons': failure_reasons
    })


@csrf_exempt
def generate_insights_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not_authenticated", "response": "Usuário não autenticado."}, status=401)
        
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        ambient_id = data.get('ambient_id')
        filter_type = data.get('filter_type')
        filter_id = data.get('filter_id')
        
        if not ambient_id:
            return JsonResponse({"error": "ambient_id_required", "response": "ID do ambiente não fornecido."}, status=400)
            
        metrics = get_filtered_metrics(ambient_id, filter_type, filter_id)
        operational_metrics = get_operational_metrics(ambient_id)
        logs_summary = get_logs_summary(ambient_id, filter_type, filter_id)
        failure_reasons = parse_failure_reasons(ambient_id, filter_type, filter_id)
        
        if filter_type and filter_id:
            entity_name = "o recurso"
            try:
                if filter_type == 'professor':
                    entity_name = f"professor(a) {Member.objects.get(id=filter_id).user.name}"
                elif filter_type == 'sala':
                    entity_name = f"sala {Classroom.objects.get(id=filter_id).name}"
                elif filter_type == 'turma':
                    entity_name = f"turma {Class.objects.get(id=filter_id).name}"
            except Exception:
                pass

            prompt = f"""
Você é um analista especialista em alocação de horários.
Analise os logs específicos d{entity_name} abaixo e explique de forma verbal, clara e amigável por que determinadas atividades não lhe foram atribuídas.

**1. Resumo dos Motivos de Falha**
{json.dumps(failure_reasons, indent=2, ensure_ascii=False)}

**2. Amostra de Logs de Decisão**
{logs_summary}

**Sua análise deve obrigatoriamente:**
1. Focar exclusivamente n{entity_name}.
2. Explicar em linguagem natural os principais motivos que levaram às falhas de atribuição.
3. Traduzir os logs para uma linguagem humana. Por exemplo, se houver casos de "Diferença de pesos", "Capacidade excedida" ou "Limite de aulas excedido", explique o que isso significa na prática.
4. Sugerir o que a coordenação pode fazer para que as preferências ou horários d{entity_name} sejam melhor aproveitados nas próximas atribuições.
Use Markdown para formatar a resposta. Não precisa incluir um título principal.
"""
        else:
            prompt = f"""
Você é um analista de dados especialista em alocação de horários e recursos universitários.
Analise os dados abaixo e forneça um insight claro e objetivo sobre a qualidade da alocação atual.
Destaque o que está bom, o que está ruim e sugira melhorias.
Use Markdown para formatar a resposta. Não precisa incluir um título principal.

**1. Métricas de Qualidade de Preferências (0 a 100%)**
- Turma/Professor: {metrics.get('turma_professor')}%
- Turma/Horário: {metrics.get('turma_horario')}%
- Turma/Sala: {metrics.get('turma_sala')}%
- Professor/Horário: {metrics.get('professor_horario')}%
- Professor/Disciplina: {metrics.get('professor_disciplina')}%
- Disciplina/Sala: {metrics.get('disciplina_sala')}%
- Disciplina/Professor: {metrics.get('disciplina_professor')}%

**2. Métricas Operacionais**
- Taxa Média de Ocupação das Salas: {operational_metrics.get('avg_room_occupation')}%
- Eficiência Média dos Professores (aulas/tempo no campus): {operational_metrics.get('avg_efficiency')}%
- Intervalo Médio entre Aulas (janelas): {operational_metrics.get('avg_interval')} aulas
- Aulas por dia (média por professor): {operational_metrics.get('avg_periods_per_day')}
- Total de Professores: {operational_metrics.get('total_professors')} para {operational_metrics.get('total_activities')} atividades
- Total de Salas: {operational_metrics.get('total_classrooms')}
- Atividades sem professor: {operational_metrics.get('activities_no_professor')}
- Atividades sem sala: {operational_metrics.get('activities_no_classroom')}

**3. Resumo dos Motivos de Falha na Alocação (Logs)**
{json.dumps(failure_reasons, indent=2, ensure_ascii=False)}

**4. Amostra de Logs de Decisão**
{logs_summary}

**Sua análise deve obrigatoriamente abordar:**
1. Quais preferências estão sendo bem atendidas e quais são os maiores gargalos? (Ex: Conflitos de horário são muito comuns?)
2. Há ocupações desnecessárias de salas? (Taxa de ocupação está muito alta ou muito baixa?)
3. As aulas dos professores poderiam ser mais consecutivas para evitar janelas longas? Como está a eficiência e o intervalo? Eles estão tendo tempo de descanso ou estão sobrecarregados?
4. O número de professores e salas parece adequado para a demanda (quantidade de atividades)? Se há atividades sem recursos, o que causou isso?
5. Sugestões práticas de otimização (ex: contratar mais professores para disciplina X, mudar horários da turma Y).
"""
        
        api_key = os.environ.get("OPENROUTER_API_KEY", "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")
        model = os.environ.get("OPENROUTER_MODEL", "cohere/north-mini-code:free")

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15
            )
        except requests.exceptions.Timeout:
            return JsonResponse({"error": "timeout", "response": "A Inteligência Artificial demorou muito para responder. Tente novamente."}, status=504)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "connection_error", "response": f"Erro de conexão com a IA: {str(e)}"}, status=502)

        result = response.json()
        if "error" in result:
            error_msg = result["error"].get("message", "Erro desconhecido")
            return JsonResponse({"error": "api_error", "response": f"Erro na API do OpenRouter: {error_msg}"}, status=500)

        content = result["choices"][0]["message"]["content"]
        return JsonResponse({"response": content})
        
    except Exception as e:
        print("Erro ao gerar insights:", e)
        return JsonResponse({"error": "server_error", "response": f"Erro ao processar solicitação: {str(e)}"}, status=500)
