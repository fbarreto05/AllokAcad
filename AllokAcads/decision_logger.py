import os
import shutil

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'decision_logs')

def _ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def clear_logs():
    """Clears all decision logs."""
    if os.path.exists(LOGS_DIR):
        try:
            shutil.rmtree(LOGS_DIR)
        except Exception:
            pass

def _write_to_file(folder, filename, message):
    _ensure_dir(folder)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def log_atribuicao_sala(activity, classroom, is_success, reason):
    if not activity or not classroom:
        return

    # Check if the activity has a preference for this classroom
    has_class_pref = activity.tclass.ideal_classrooms.filter(classroom=classroom).exists()
    has_subject_pref = activity.tsubject.ideal_classrooms.filter(classroom=classroom).exists()
    has_pref = has_class_pref or has_subject_pref

    act_id = activity.id
    classroom_name = classroom.name
    classroom_id = classroom.id

    if has_pref:
        message = (
            f"[SALA] Tentativa de atribuição da sala '{classroom_name}' à atividade ID {act_id}: "
            f"{'Sucesso' if is_success else 'Falha'} - Justificativa: {reason}"
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
        _write_to_file(os.path.join(LOGS_DIR, 'salas'), f'sala_{classroom_id}.log', message)
    elif is_success:
        message = (
            f"[SALA] Atribuição da sala '{classroom_name}' à atividade ID {act_id}: Sucesso - "
            f"Justificativa: Decisão aleatória - a atividade não possui preferências para esta sala."
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
        _write_to_file(os.path.join(LOGS_DIR, 'salas'), f'sala_{classroom_id}.log', message)

def log_atribuicao_professor(activity, professor, is_success, reason):
    if not activity or not professor:
        return

    # Check if activity has preference for professor, or subject has preference for professor, or professor has preference for subject
    has_class_pref = activity.tclass.favorite_professors.filter(professor=professor).exists()
    has_subject_pref = activity.tsubject.favorite_professors.filter(professor=professor).exists()
    has_prof_pref = professor.prefered_subjects.filter(subject=activity.tsubject).exists()
    has_pref = has_class_pref or has_subject_pref or has_prof_pref

    act_id = activity.id
    prof_name = professor.user.name if (professor.user and professor.user.name) else f"Membro ID {professor.id}"
    prof_id = professor.id

    if has_pref:
        message = (
            f"[PROFESSOR] Tentativa de atribuição do professor '{prof_name}' à atividade ID {act_id}: "
            f"{'Sucesso' if is_success else 'Falha'} - Justificativa: {reason}"
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
        _write_to_file(os.path.join(LOGS_DIR, 'professores'), f'professor_{prof_id}.log', message)
    elif is_success:
        message = (
            f"[PROFESSOR] Atribuição do professor '{prof_name}' à atividade ID {act_id}: Sucesso - "
            f"Justificativa: Decisão aleatória - a atividade não possui preferências para este professor."
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
        _write_to_file(os.path.join(LOGS_DIR, 'professores'), f'professor_{prof_id}.log', message)

def log_alocacao_horario(activity, line, column, is_success, reason):
    if not activity:
        return

    # Check if class has preference for this schedule, or if professor (if any) has preference for this schedule
    has_class_pref = activity.tclass.prefered_schedules.filter(line=line, column=column).exists()
    has_prof_pref = False
    if activity.tprofessor:
        prof = activity.tprofessor
        ambient = activity.ambient_set.first()
        if ambient and ambient.available_schedules.count() == prof.prefered_schedules.count():
            has_prof_pref = False
        else:
            has_prof_pref = prof.prefered_schedules.filter(line=line, column=column).exists()
    has_pref = has_class_pref or has_prof_pref

    act_id = activity.id

    if has_pref:
        message = (
            f"[HORARIO] Tentativa de alocação no horário Dia {column}, Período {line} para atividade ID {act_id}: "
            f"{'Sucesso' if is_success else 'Falha'} - Justificativa: {reason}"
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
    elif is_success:
        message = (
            f"[HORARIO] Alocação no horário Dia {column}, Período {line} para atividade ID {act_id}: Sucesso - "
            f"Justificativa: Decisão aleatória - a atividade não possui preferências para este horário."
        )
        _write_to_file(os.path.join(LOGS_DIR, 'activities'), f'atividade_{act_id}.log', message)
