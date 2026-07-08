import os
import re
from collections import Counter
from AllokAcads.models import Ambient, Activitie, Member, Classroom, Subject, Class
from AllokAcads.metrics import (
    turma_professor_metric, turma_horario_metric, turma_sala_metric,
    professor_horario_metric, professor_disciplina_metric,
    disciplina_sala_metric, disciplina_professor_metric
)
from AllokAcads.decision_logger import LOGS_DIR
from dashboard.models import ProfessorStatistics, SpaceStatistics
from django.db.models import Avg, Count, Sum


def get_all_metrics(ambient_id):
    """Calcula as 7 métricas de preferência para o ambiente."""
    try:
        ambient = Ambient.objects.get(id=ambient_id)
    except Ambient.DoesNotExist:
        return {}

    timetable = ambient.published_timetable
    if not timetable:
        return {}

    return {
        'turma_professor': round(turma_professor_metric(timetable) * 100, 1),
        'turma_horario': round(turma_horario_metric(timetable) * 100, 1),
        'turma_sala': round(turma_sala_metric(timetable) * 100, 1),
        'professor_horario': round(professor_horario_metric(timetable) * 100, 1),
        'professor_disciplina': round(professor_disciplina_metric(timetable) * 100, 1),
        'disciplina_sala': round(disciplina_sala_metric(timetable) * 100, 1),
        'disciplina_professor': round(disciplina_professor_metric(timetable) * 100, 1),
    }


def get_filtered_metrics(ambient_id, filter_type=None, filter_id=None):
    """Calcula métricas filtradas. Se sem filtro, retorna todas."""
    if not filter_type or not filter_id:
        return get_all_metrics(ambient_id)

    try:
        ambient = Ambient.objects.get(id=ambient_id)
    except Ambient.DoesNotExist:
        return {}

    timetable = ambient.published_timetable
    if not timetable:
        return {}

    # Para filtros, recalcular com base em atividades filtradas
    # As métricas já iteram sobre allocations, mas retornamos as globais
    # e destacamos as relevantes ao filtro
    return get_all_metrics(ambient_id)


def get_filter_options(ambient_id):
    """Retorna opções de filtro disponíveis para o ambiente."""
    try:
        ambient = Ambient.objects.get(id=ambient_id)
    except Ambient.DoesNotExist:
        return {'turmas': [], 'professores': [], 'salas': [], 'disciplinas': []}

    turmas = list(ambient.classes.values('id', 'name').order_by('name'))
    professores = list(
        ambient.members.filter(is_professor=True)
        .values('id', 'user__name')
        .order_by('user__name')
    )
    salas = list(ambient.classrooms.values('id', 'name').order_by('name'))
    disciplinas = list(ambient.subjects.values('id', 'name').order_by('name'))

    return {
        'turmas': turmas,
        'professores': [{'id': p['id'], 'name': p['user__name']} for p in professores],
        'salas': salas,
        'disciplinas': disciplinas,
    }


# --- Parsing de logs ---

FAILURE_CATEGORIES = {
    'Conflito de horário': [
        'Conflito de horários', 'Conflito de turma', 'Conflito de professor',
        'Conflito de sala', 'conflito de horário', 'schedule_conflict'
    ],
    'Capacidade excedida': [
        'Capacidade excedida', 'Capacidade insuficiente', 'capacity_exceeded'
    ],
    'Limite de aulas excedido': [
        'Limite de aulas excedido'
    ],
    'Diferença de pesos': [
        'Diferença de pesos', 'diferença de pesos', 'Peso inferior', 'pesos inferiores', 'weight_ok'
    ],
    'Derrota no desempate': [
        'Derrota no desempate', 'tiebreaker_loser', 'perdeu no desempate'
    ],
    'Preferência zerada': [
        'Preferência zerada', 'preference_zero', 'preferência zerada'
    ],
    'Prioridade bloqueada': [
        'preferência prioritária', 'priority_blocked', 'Prioridade bloqueada'
    ],
    'Backtracking': [
        'backtracking', 'Backtracking'
    ],
    'Slot inexistente': [
        'slot inexistente', 'Slot inexistente', 'fora da grade'
    ],
}


def _categorize_failure(line):
    """Categoriza uma linha de log de falha."""
    line_lower = line.lower()
    for category, keywords in FAILURE_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in line_lower:
                return category
    return 'Outros'


def parse_failure_reasons(ambient_id, filter_type=None, filter_id=None):
    """Lê os logs de falha e contabiliza por categoria."""
    logs_content = _read_logs(ambient_id, filter_type, filter_id)
    if not logs_content:
        return {}

    counter = Counter()
    for line in logs_content.split('\n'):
        if '[FALLBACK]' in line or '[FORMAÇÕES]' in line or '[REAJUSTE]' in line:
            continue
        if 'Falha' in line or 'falhou' in line.lower():
            category = _categorize_failure(line)
            counter[category] += 1

    return dict(counter.most_common(10))


def _read_logs(ambient_id, filter_type=None, filter_id=None):
    """Lê os logs relevantes baseado no filtro."""
    if not os.path.exists(LOGS_DIR):
        return ""

    lines = []

    if filter_type and filter_id:
        # Lê log específico da entidade
        type_map = {
            'professor': ('professores', f'professor_{filter_id}.log'),
            'sala': ('salas', f'sala_{filter_id}.log'),
            'turma': ('activities', None),  # Turma filtra por atividades
            'disciplina': ('activities', None),
        }

        if filter_type in type_map:
            folder, filename = type_map[filter_type]
            if filename:
                filepath = os.path.join(LOGS_DIR, folder, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
            else:
                ambient = Ambient.objects.get(id=ambient_id)
                if filter_type == 'turma':
                    valid_activities = ambient.activities.filter(tclass_id=filter_id).values_list('id', flat=True)
                else:
                    valid_activities = ambient.activities.filter(tsubject_id=filter_id).values_list('id', flat=True)
                
                valid_filenames = set(f"atividade_{aid}.log" for aid in valid_activities)
                
                # Para turma/disciplina, lê apenas os logs das atividades pertencentes
                act_dir = os.path.join(LOGS_DIR, 'activities')
                if os.path.exists(act_dir):
                    for fname in os.listdir(act_dir):
                        if fname in valid_filenames:
                            filepath = os.path.join(act_dir, fname)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines.extend(f.readlines())
    else:
        # Lê todos os logs
        for subfolder in ['activities', 'salas', 'professores']:
            subfolder_path = os.path.join(LOGS_DIR, subfolder)
            if os.path.exists(subfolder_path):
                for fname in os.listdir(subfolder_path):
                    filepath = os.path.join(subfolder_path, fname)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines.extend(f.readlines())

    return '\n'.join(lines)


def get_logs_summary(ambient_id, filter_type=None, filter_id=None, max_chars=4000):
    """Retorna um resumo dos logs para enviar à LLM."""
    content = _read_logs(ambient_id, filter_type, filter_id)
    if not content:
        return "Nenhum log de decisão disponível."

    # Prioriza linhas de falha (mais informativas)
    all_lines = content.split('\n')
    failure_lines = [l for l in all_lines if 'Falha' in l or 'falhou' in l.lower()]
    success_lines = [l for l in all_lines if 'Sucesso' in l]

    summary_parts = []
    summary_parts.append(f"Total de decisões registradas: {len(all_lines)}")
    summary_parts.append(f"Falhas: {len(failure_lines)}")
    summary_parts.append(f"Sucessos: {len(success_lines)}")
    summary_parts.append("")

    # Adiciona amostra de falhas
    summary_parts.append("--- Amostra de decisões de falha ---")
    for line in failure_lines[:30]:
        summary_parts.append(line.strip())

    # Adiciona amostra de sucessos
    summary_parts.append("")
    summary_parts.append("--- Amostra de decisões de sucesso ---")
    for line in success_lines[:15]:
        summary_parts.append(line.strip())

    result = '\n'.join(summary_parts)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n... (truncado)"
    return result


def get_operational_metrics(ambient_id):
    """Coleta métricas operacionais do ambiente para análise da LLM."""
    try:
        ambient = Ambient.objects.get(id=ambient_id)
    except Ambient.DoesNotExist:
        return {}

    # Contagens de recursos
    total_professors = ambient.members.filter(is_professor=True).count()
    total_classrooms = ambient.classrooms.count()
    total_activities = ambient.activities.count()
    total_subjects = ambient.subjects.count()
    total_classes = ambient.classes.count()

    # Atividades sem atribuição
    activities_no_professor = ambient.activities.filter(tprofessor=None).count()
    activities_no_classroom = ambient.activities.filter(tclassroom=None).count()

    # Estatísticas de professor
    prof_stats = ProfessorStatistics.objects.filter(ambient=ambient)
    avg_interval = prof_stats.aggregate(avg=Avg('periods_interval'))['avg']
    avg_efficiency = prof_stats.aggregate(avg=Avg('day_efficiency'))['avg']
    avg_periods = prof_stats.aggregate(avg=Avg('number_of_periods'))['avg']

    # Uso de professores
    professors = ambient.members.filter(is_professor=True)
    prof_usage = []
    for prof in professors:
        name = prof.user.name if prof.user else f"ID {prof.id}"
        prof_usage.append({
            'name': name,
            'num_uses': prof.num_uses,
        })
    prof_usage.sort(key=lambda x: x['num_uses'], reverse=True)

    # Uso de salas
    classrooms = ambient.classrooms.all()
    room_usage = []
    for room in classrooms:
        room_usage.append({
            'name': room.name,
            'num_uses': room.num_uses,
            'capacity': room.classroom_capacity,
        })
    room_usage.sort(key=lambda x: x['num_uses'], reverse=True)

    # Ocupação de salas
    space_stats = SpaceStatistics.objects.filter(ambient=ambient)
    avg_occupation = space_stats.aggregate(avg=Avg('use_time_rate'))['avg']

    return {
        'total_professors': total_professors,
        'total_classrooms': total_classrooms,
        'total_activities': total_activities,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        'activities_no_professor': activities_no_professor,
        'activities_no_classroom': activities_no_classroom,
        'avg_interval': round(avg_interval, 2) if avg_interval else 0,
        'avg_efficiency': round(avg_efficiency * 100, 1) if avg_efficiency else 0,
        'avg_periods_per_day': round(avg_periods, 1) if avg_periods else 0,
        'avg_room_occupation': round(avg_occupation * 100, 1) if avg_occupation else 0,
        'max_activities_per_cycle': ambient.max_actv_in_cicle if hasattr(ambient, 'max_actv_in_cicle') else 'N/A',
        'professor_usage_top5': prof_usage[:5],
        'professor_usage_bottom5': prof_usage[-5:] if len(prof_usage) > 5 else prof_usage,
        'room_usage_top5': room_usage[:5],
        'room_usage_bottom5': room_usage[-5:] if len(room_usage) > 5 else room_usage,
    }
