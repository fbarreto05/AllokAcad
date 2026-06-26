from rko import RKO

class RKOAttributionEnvironment:
    """
    Ambiente RKO para otimizar a Atribuição (fase 1):
    Encontra a melhor associação de Professor e Sala para cada Atividade.
    """
    def __init__(self, ambient, activities):
        self.ambient = ambient
        self.aulas = list(activities)
        self.professores = list(ambient.members.filter(is_professor=True))
        self.salas = list(ambient.classrooms.all())
        
        self.tam_solution = 2 * len(self.aulas)
        self.instance_name = f"Attribution_{ambient.ambientid}"
        self.LS_type = 'Best'
        self.dict_best = {self.instance_name: 0}
        
        # Parâmetros padrão das meta-heurísticas para o validador do RKO
        self.BRKGA_parameters = {
            'p': [100, 50],
            'pe': [0.20, 0.15],
            'pm': [0.05],
            'rhoe': [0.70]
        }
        self.VNS_parameters = {
            'kMax': [3],
            'betaMin': [0.05]
        }
        self.SA_parameters = {
            'SAmax': [50],
            'alphaSA': [0.95],
            'betaMin': [0.01],
            'betaMax': [0.05],
            'T0': [500]
        }

    def decoder(self, keys):
        """
        Mapeia chaves reais [0,1) para atribuições de professores e salas.
        """
        for i, a in enumerate(self.aulas):
            # Gene 2*i: Escolha do Professor
            p_idx = int(keys[2 * i] * len(self.professores))
            a.tprofessor = self.professores[p_idx]
            
            # Gene 2*i+1: Escolha da Sala
            r_idx = int(keys[2 * i + 1] * len(self.salas))
            a.tclassroom = self.salas[r_idx]
            
        return self.aulas

    def cost(self, aulas, final_solution=False):
        """
        Calcula o custo da atribuição. Penaliza capacidade excedida, sobrecarga
        de horários de professores e desrespeito a preferências.
        """
        custo = 0
        max_cicle = self.ambient.max_actv_in_cicle or 20
        
        # 1. Verificar carga horária de professores
        prof_periods = {p.id: 0 for p in self.professores}
        for a in aulas:
            if a.tprofessor:
                prof_periods[a.tprofessor.id] += a.activities_qtd
                
        for p_id, periods in prof_periods.items():
            if periods > max_cicle:
                custo += 1000000 * (periods - max_cicle)
                
        # 2. Verificar capacidade de salas e preferências
        for a in aulas:
            # Capacidade da sala
            if a.tclassroom and a.tclass:
                if a.tclassroom.classroom_capacity < a.tclass.number_of_students:
                    custo += 500000
                    
            # Preferências de Professor
            score_prof = 1
            if a.tclass and a.tprofessor:
                class_pref = a.tclass.favorite_professors.filter(professor=a.tprofessor).first()
                if class_pref:
                    score_prof += class_pref.professor_weight
                else:
                    score_prof += 5  # Valor padrão baixo para alternativa
                    
                subject_pref = a.tsubject.favorite_professors.filter(professor=a.tprofessor).first()
                if subject_pref:
                    score_prof += subject_pref.professor_weight
                else:
                    score_prof += 5
            
            if score_prof == 0:
                custo += 100000
            else:
                custo += max(0, 200 - score_prof)
                
            # Preferências de Sala
            score_room = 1
            if a.tclass and a.tclassroom:
                class_room_pref = a.tclass.ideal_classrooms.filter(classroom=a.tclassroom).first()
                if class_room_pref:
                    score_room += class_room_pref.classroom_weight
                else:
                    score_room += 5
                    
                subject_room_pref = a.tsubject.ideal_classrooms.filter(classroom=a.tclassroom).first()
                if subject_room_pref:
                    score_room += subject_room_pref.classroom_weight
                else:
                    score_room += 5
                    
            if score_room == 0:
                custo += 100000
            else:
                custo += max(0, 200 - score_room)
                
            # Preferência do Professor pela Disciplina
            if a.tprofessor and a.tsubject:
                prof_sub_pref = a.tprofessor.prefered_subjects.filter(subject=a.tsubject).first()
                score_sub = prof_sub_pref.subject_weight if prof_sub_pref else 1
                custo += max(0, 100 - score_sub)
                
        return custo


class RKOAllocationEnvironment:
    """
    Ambiente RKO para otimizar a Alocação (fase 2):
    Encontra os melhores horários (dia e período) para as atividades pré-atribuídas.
    """
    def __init__(self, ambient, activities):
        self.ambient = ambient
        self.aulas = list(activities)
        self.professores = list(ambient.members.filter(is_professor=True))
        self.salas = list(ambient.classrooms.all())
        self.schedules = list(ambient.available_schedules.all())
        
        self.periods = ambient.periods_in_a_day or 4
        self.days = ambient.days_in_a_cicle or 5
        self.tam_solution = len(self.aulas)
        self.instance_name = f"Allocation_{ambient.ambientid}"
        self.LS_type = 'Best'
        self.dict_best = {self.instance_name: 0}
        
        # Parâmetros padrão das meta-heurísticas
        self.BRKGA_parameters = {
            'p': [100, 50],
            'pe': [0.20, 0.15],
            'pm': [0.05],
            'rhoe': [0.70]
        }
        self.VNS_parameters = {
            'kMax': [3],
            'betaMin': [0.05]
        }
        self.SA_parameters = {
            'SAmax': [50],
            'alphaSA': [0.95],
            'betaMin': [0.01],
            'betaMax': [0.05],
            'T0': [500]
        }
        
        # Pré-computa posições de horários preferidos
        self._class_pref = {}
        self._prof_pref = {}
        for a in self.aulas:
            if a.tclass:
                self._class_pref[a.tclass.id] = set(
                    (s.line, s.column) for s in a.tclass.prefered_schedules.all()
                )
            if a.tprofessor:
                self._prof_pref[a.tprofessor.id] = set(
                    (s.line, s.column) for s in a.tprofessor.prefered_schedules.all()
                )
                
        # Pré-computa posições válidas na grade para cada atividade
        self._valid_positions = []
        for a in self.aulas:
            d = a.activities_qtd or 1
            positions = []
            for col in range(self.days):
                for row in range(self.periods - d + 1):
                    positions.append((row, col))
            self._valid_positions.append(positions)

    def decoder(self, keys):
        """
        Mapeia chaves reais [0,1) para a grade horária (linha, coluna).
        """
        timetable = {(l, c): [] for l in range(self.periods) for c in range(self.days)}
        for i, a in enumerate(self.aulas):
            positions = self._valid_positions[i]
            idx = int(keys[i] * len(positions))
            idx = min(idx, len(positions) - 1)
            row, col = positions[idx]
            for p in range(a.activities_qtd):
                timetable[(row + p, col)].append(a)
        return timetable

    def cost(self, timetable, final_solution=False):
        """
        Mapeia penalidades de colisão física e violações de preferências de horários.
        """
        P_CONFLITO = 100000
        P_FORA_TURMA = 10
        P_FORA_PROF = 10
        custo = 0
        
        for (line, col), acts in timetable.items():
            n = len(acts)
            if n <= 1:
                if n == 1:
                    a = acts[0]
                    if a.tclass and (line, col) not in self._class_pref.get(a.tclass.id, set()):
                        custo += P_FORA_TURMA
                    if a.tprofessor and (line, col) not in self._prof_pref.get(a.tprofessor.id, set()):
                        custo += P_FORA_PROF
                continue
                
            # Mais de 1 atividade no slot -> checa conflitos
            for j in range(n):
                a = acts[j]
                if a.tclass and (line, col) not in self._class_pref.get(a.tclass.id, set()):
                    custo += P_FORA_TURMA
                if a.tprofessor and (line, col) not in self._prof_pref.get(a.tprofessor.id, set()):
                    custo += P_FORA_PROF
                    
                for k in range(j + 1, n):
                    b = acts[k]
                    # Mesma turma
                    if a.tclass and b.tclass and a.tclass.id == b.tclass.id:
                        custo += P_CONFLITO
                    # Mesmo professor
                    if a.tprofessor and b.tprofessor and a.tprofessor.id == b.tprofessor.id:
                        custo += P_CONFLITO
                    # Mesma sala
                    if a.tclassroom and b.tclassroom and a.tclassroom.id == b.tclassroom.id:
                        custo += P_CONFLITO
                        
        return custo
