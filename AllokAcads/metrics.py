from AllokAcads.models import Timetable

def turma_professor_metric(timetable):
    """
    Métrica de Turma-Professor (Class-Professor).
    Verifica se o professor atribuído à atividade da turma condiz com as preferências
    da turma (favorite_professors). Retorna um valor de 0 a 1.
    Se não houver preferências, a atividade não influencia a métrica.
    Se nenhuma atividade tiver preferências, retorna 1.0.
    """
    if not timetable:
        return 1.0
    
    allocations = timetable.table.prefetch_related(
        'activitie__tclass__favorite_professors__professor'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tclass = activity.tclass
            if not tclass:
                continue
            
            prefs = list(tclass.favorite_professors.all())
            if not prefs:
                continue
            
            potential = max(p.professor_weight for p in prefs)
            if potential <= 0:
                potential = 1.0
                
            achieved = 0.0
            tprofessor = activity.tprofessor
            if tprofessor:
                for p in prefs:
                    if p.professor_id == tprofessor.id:
                        achieved = p.professor_weight
                        break
                        
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def turma_horario_metric(timetable):
    """
    Métrica de Turma-Horário (Class-Schedule).
    Verifica se o horário em que a atividade da turma foi alocada condiz com os
    horários preferidos da turma (prefered_schedules). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tclass__prefered_schedules'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tclass = activity.tclass
            if not tclass:
                continue
                
            prefs = list(tclass.prefered_schedules.all())
            if not prefs:
                continue
                
            potential = 1.0
            achieved = 0.0
            for p in prefs:
                if p.line == allocation.line and p.column == allocation.column:
                    achieved = 1.0
                    break
                    
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def turma_sala_metric(timetable):
    """
    Métrica de Turma-Sala (Class-Room).
    Verifica se a sala atribuída à atividade da turma condiz com as preferências
    da turma (ideal_classrooms). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tclass__ideal_classrooms__classroom'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tclass = activity.tclass
            if not tclass:
                continue
                
            prefs = list(tclass.ideal_classrooms.all())
            if not prefs:
                continue
                
            potential = max(p.classroom_weight for p in prefs)
            if potential <= 0:
                potential = 1.0
                
            achieved = 0.0
            tclassroom = activity.tclassroom
            if tclassroom:
                for p in prefs:
                    if p.classroom_id == tclassroom.id:
                        achieved = p.classroom_weight
                        break
                        
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def professor_horario_metric(timetable):
    """
    Métrica de Professor-Horário (Professor-Schedule).
    Verifica se o horário em que o professor foi alocado condiz com as preferências
    do professor (prefered_schedules). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tprofessor__prefered_schedules'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tprofessor = activity.tprofessor
            if not tprofessor:
                continue
                
            prefs = list(tprofessor.prefered_schedules.all())
            if not prefs:
                continue
                
            potential = 1.0
            achieved = 0.0
            for p in prefs:
                if p.line == allocation.line and p.column == allocation.column:
                    achieved = 1.0
                    break
                    
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def professor_disciplina_metric(timetable):
    """
    Métrica de Professor-Disciplina (Professor-Subject).
    Verifica se a disciplina atribuída ao professor condiz com as preferências
    do professor (prefered_subjects). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tprofessor__prefered_subjects__subject'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tprofessor = activity.tprofessor
            if not tprofessor:
                continue
                
            prefs = list(tprofessor.prefered_subjects.all())
            if not prefs:
                continue
                
            potential = max(p.subject_weight for p in prefs)
            if potential <= 0:
                potential = 1.0
                
            achieved = 0.0
            tsubject = activity.tsubject
            if tsubject:
                for p in prefs:
                    if p.subject_id == tsubject.id:
                        achieved = p.subject_weight
                        break
                        
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def disciplina_sala_metric(timetable):
    """
    Métrica de Disciplina-Sala (Subject-Room).
    Verifica se a sala atribuída para a disciplina condiz com as preferências
    da disciplina (ideal_classrooms). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tsubject__ideal_classrooms__classroom'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tsubject = activity.tsubject
            if not tsubject:
                continue
                
            prefs = list(tsubject.ideal_classrooms.all())
            if not prefs:
                continue
                
            potential = max(p.classroom_weight for p in prefs)
            if potential <= 0:
                potential = 1.0
                
            achieved = 0.0
            tclassroom = activity.tclassroom
            if tclassroom:
                for p in prefs:
                    if p.classroom_id == tclassroom.id:
                        achieved = p.classroom_weight
                        break
                        
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential


def disciplina_professor_metric(timetable):
    """
    Métrica de Disciplina-Professor (Subject-Professor).
    Verifica se o professor atribuído à disciplina condiz com as preferências
    da disciplina (favorite_professors). Retorna um valor de 0 a 1.
    """
    if not timetable:
        return 1.0
        
    allocations = timetable.table.prefetch_related(
        'activitie__tsubject__favorite_professors__professor'
    )
    
    total_achieved = 0.0
    total_potential = 0.0
    
    for allocation in allocations:
        for activity in allocation.activitie.all():
            tsubject = activity.tsubject
            if not tsubject:
                continue
                
            prefs = list(tsubject.favorite_professors.all())
            if not prefs:
                continue
            
            potential = max(p.professor_weight for p in prefs)
            if potential <= 0:
                potential = 1.0
                
            achieved = 0.0
            tprofessor = activity.tprofessor
            if tprofessor:
                for p in prefs:
                    if p.professor_id == tprofessor.id:
                        achieved = p.professor_weight
                        break
                        
            total_achieved += achieved
            total_potential += potential
            
    if total_potential == 0:
        return 1.0
    return total_achieved / total_potential
