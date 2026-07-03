from rko import RKO
from AllokAcads import rko_llm_constraints

class MockObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __repr__(self):
        name = getattr(self, 'name', 'Sem Nome')
        return f"<{self.__class__.__name__}: {name}>"

class MockQuerySet(list):
    def all(self):
        return self
    def count(self):
        return len(self)
    def exists(self):
        return len(self) > 0
    def first(self):
        return self[0] if self else None
    def filter(self, **kwargs):
        res = []
        for item in self:
            match = True
            for k, v in kwargs.items():
                parts = k.split("__")
                obj = item
                for part in parts[:-1]:
                    obj = getattr(obj, part, None)
                val = getattr(obj, parts[-1], None) if obj else None
                
                # Compara por ID se ambos forem MockObjects
                val_id = getattr(val, 'id', None)
                v_id = getattr(v, 'id', None)
                if val_id is not None and v_id is not None:
                    if val_id != v_id:
                        match = False
                        break
                else:
                    if val != v:
                        match = False
                        break
            if match:
                res.append(item)
        return MockQuerySet(res)

def to_mock_schedule(s):
    if not s: return None
    return MockObject(id=s.id, line=s.line, column=s.column)

def to_mock_user(u):
    if not u: return None
    return MockObject(id=u.id, name=u.name)

def to_mock_professor_preference(p):
    if not p: return None
    return MockObject(
        id=p.id,
        professor=MockObject(id=p.professor.id) if p.professor else None,
        professor_weight=p.professor_weight
    )

def to_mock_classroom_preference(c):
    if not c: return None
    return MockObject(
        id=c.id,
        classroom=MockObject(id=c.classroom.id) if c.classroom else None,
        classroom_weight=c.classroom_weight
    )

def to_mock_subject_preference(s):
    if not s: return None
    return MockObject(
        id=s.id,
        subject=MockObject(id=s.subject.id) if s.subject else None,
        subject_weight=s.subject_weight
    )

def to_mock_member(m):
    if not m: return None
    return MockObject(
        id=m.id,
        user=to_mock_user(m.user),
        is_professor=m.is_professor,
        prefered_schedules=MockQuerySet([to_mock_schedule(s) for s in m.prefered_schedules.all()]),
        prefered_subjects=MockQuerySet([to_mock_subject_preference(s) for s in m.prefered_subjects.all()]),
        num_uses=m.num_uses
    )

def to_mock_classroom(c):
    if not c: return None
    return MockObject(
        id=c.id,
        name=c.name,
        classroom_capacity=c.classroom_capacity,
        num_uses=c.num_uses
    )

def to_mock_class(tc):
    if not tc: return None
    return MockObject(
        id=tc.id,
        name=tc.name,
        prefered_schedules=MockQuerySet([to_mock_schedule(s) for s in tc.prefered_schedules.all()]),
        favorite_professors=MockQuerySet([to_mock_professor_preference(p) for p in tc.favorite_professors.all()]),
        ideal_classrooms=MockQuerySet([to_mock_classroom_preference(c) for c in tc.ideal_classrooms.all()]),
        number_of_students=tc.number_of_students
    )

def to_mock_subject(sub):
    if not sub: return None
    return MockObject(
        id=sub.id,
        name=sub.name,
        favorite_professors=MockQuerySet([to_mock_professor_preference(p) for p in sub.favorite_professors.all()]),
        ideal_classrooms=MockQuerySet([to_mock_classroom_preference(c) for c in sub.ideal_classrooms.all()])
    )

def to_mock_activity(a, prof_map, room_map):
    if not a: return None
    return MockObject(
        id=a.id,
        tclass=to_mock_class(a.tclass) if a.tclass else None,
        tclassroom=room_map.get(a.tclassroom.id) if a.tclassroom else None,
        tprofessor=prof_map.get(a.tprofessor.id) if a.tprofessor else None,
        tsubject=to_mock_subject(a.tsubject) if a.tsubject else None,
        classroom_weight=a.classroom_weight,
        professor_weight=a.professor_weight,
        activities_qtd=a.activities_qtd
    )


class RKOAttributionEnvironment:
    """
    Ambiente RKO para otimizar a Atribuição (fase 1):
    Encontra a melhor associação de Professor e Sala para cada Atividade.
    """
    def __init__(self, ambient, activities):
        # Mapeia objetos originais do banco de dados para salvar de volta no decoder
        self._original_activities = list(activities)
        self.db_activities_map = {a.id: a for a in activities}
        self.db_professors_map = {p.id: p for p in ambient.members.filter(is_professor=True)}
        self.db_classrooms_map = {c.id: c for c in ambient.classrooms.all()}

        # Cria a versão "mock" limpa para o multiprocessing não engasgar
        self.ambient = MockObject(
            ambientid=ambient.ambientid,
            name=ambient.name,
            periods_in_a_day=ambient.periods_in_a_day,
            days_in_a_cicle=ambient.days_in_a_cicle,
            max_actv_in_cicle=ambient.max_actv_in_cicle,
            members=MockQuerySet([to_mock_member(m) for m in ambient.members.filter(is_professor=True) if m.user]),
            classrooms=MockQuerySet([to_mock_classroom(c) for c in ambient.classrooms.all()]),
            subjects=MockQuerySet([to_mock_subject(s) for s in ambient.subjects.all()]),
            classes=MockQuerySet([to_mock_class(c) for c in ambient.classes.all()]),
            activities=MockQuerySet([])
        )

        self.professores = list(self.ambient.members.all())
        self.salas = list(self.ambient.classrooms.all())

        prof_map = {p.id: p for p in self.professores}
        room_map = {r.id: r for r in self.salas}

        self.aulas = [to_mock_activity(a, prof_map, room_map) for a in activities]
        self.tam_solution = 2 * len(self.aulas)
        self.instance_name = f"Attribution_{ambient.ambientid}"
        self.LS_type = 'Best'
        self.dict_best = {self.instance_name: 0}
        
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

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove os objetos e conexões do Django da serialização para o worker process
        state['_original_activities'] = None
        state['db_activities_map'] = {}
        state['db_professors_map'] = {}
        state['db_classrooms_map'] = {}
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

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
            
            # Atualiza os objetos originais do banco de dados (Django models)
            db_act = self.db_activities_map.get(a.id)
            if db_act:
                db_act.tprofessor = self.db_professors_map.get(a.tprofessor.id) if a.tprofessor else None
                db_act.tclassroom = self.db_classrooms_map.get(a.tclassroom.id) if a.tclassroom else None
                
        if self._original_activities is not None:
            return self._original_activities
        return self.aulas

    def cost(self, aulas, final_solution=False):
        """
        Calcula o custo da atribuição. Penaliza capacidade excedida, sobrecarga
        de horários de professores e desrespeito a preferências.
        """
        custo = 0
        max_slots = (self.ambient.days_in_a_cicle or 5) * (self.ambient.periods_in_a_day or 4)
        max_cicle = self.ambient.max_actv_in_cicle or max_slots
        if max_cicle > max_slots:
            max_cicle = max_slots
        
        # 1. Verificar carga horária de professores
        prof_periods = {p.id: 0 for p in self.professores}
        for a in aulas:
            if a.tprofessor:
                prof_periods[a.tprofessor.id] += a.activities_qtd
                
        for p_id, periods in prof_periods.items():
            if periods > max_cicle:
                custo += 1000000 * (periods - max_cicle)

        # 1.1 Verificar carga horária de salas
        room_periods = {r.id: 0 for r in self.salas}
        for a in aulas:
            if a.tclassroom:
                room_periods[a.tclassroom.id] += a.activities_qtd

        for r_id, periods in room_periods.items():
            if periods > max_slots:
                custo += 1000000 * (periods - max_slots)
                
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
                
        return rko_llm_constraints.apply_attribution_constraints(
            custo,
            aulas,
            self.ambient.ambientid,
        )


class RKOAllocationEnvironment:
    """
    Ambiente RKO para otimizar a Alocação (fase 2):
    Encontra os melhores horários (dia e período) para as atividades pré-atribuídas.
    """
    def __init__(self, ambient, activities):
        # Mapeia objetos originais do banco de dados para salvar de volta no decoder
        self._original_activities = list(activities)
        self.db_activities_map = {a.id: a for a in activities}

        # Cria a versão "mock" limpa para o multiprocessing não engasgar
        self.ambient = MockObject(
            ambientid=ambient.ambientid,
            name=ambient.name,
            periods_in_a_day=ambient.periods_in_a_day,
            days_in_a_cicle=ambient.days_in_a_cicle,
            max_actv_in_cicle=ambient.max_actv_in_cicle,
            members=MockQuerySet([to_mock_member(m) for m in ambient.members.filter(is_professor=True) if m.user]),
            classrooms=MockQuerySet([to_mock_classroom(c) for c in ambient.classrooms.all()]),
            subjects=MockQuerySet([to_mock_subject(s) for s in ambient.subjects.all()]),
            classes=MockQuerySet([to_mock_class(c) for c in ambient.classes.all()]),
            activities=MockQuerySet([])
        )

        self.professores = list(self.ambient.members.all())
        self.salas = list(self.ambient.classrooms.all())

        prof_map = {p.id: p for p in self.professores}
        room_map = {r.id: r for r in self.salas}

        self.aulas = [to_mock_activity(a, prof_map, room_map) for a in activities]
        self.periods = ambient.periods_in_a_day or 4
        self.days = ambient.days_in_a_cicle or 5
        self.tam_solution = len(self.aulas)
        self.instance_name = f"Allocation_{ambient.ambientid}"
        self.LS_type = 'Best'
        self.dict_best = {self.instance_name: 0}
        
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

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove os objetos e conexões do Django da serialização para o worker process
        state['_original_activities'] = None
        state['db_activities_map'] = {}
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def decoder(self, keys):
        """
        Mapeia chaves reais [0,1) para a grade horária (linha, coluna) retornando objetos do banco.
        """
        timetable = {(l, c): [] for l in range(self.periods) for c in range(self.days)}
        for i, a in enumerate(self.aulas):
            positions = self._valid_positions[i]
            idx = int(keys[i] * len(positions))
            idx = min(idx, len(positions) - 1)
            row, col = positions[idx]
            
            act_obj = self.db_activities_map.get(a.id)
            if act_obj is None:
                act_obj = a
            for p in range(a.activities_qtd):
                timetable[(row + p, col)].append(act_obj)
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
                
            # Mesma turma/professor/sala no slot -> checa conflitos
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
                        
        return rko_llm_constraints.apply_allocation_constraints(
            custo,
            timetable,
            self.ambient.ambientid,
        )


class RKOUnifiedEnvironment:
    """
    Ambiente RKO unificado para a IA: escolhe professor, sala e horario na
    mesma solucao.
    """
    def __init__(self, ambient, activities):
        self._original_activities = list(activities)
        self.db_activities_map = {a.id: a for a in activities}
        self.db_professors_map = {p.id: p for p in ambient.members.filter(is_professor=True)}
        self.db_classrooms_map = {c.id: c for c in ambient.classrooms.all()}

        self.ambient = MockObject(
            ambientid=ambient.ambientid,
            name=ambient.name,
            periods_in_a_day=ambient.periods_in_a_day,
            days_in_a_cicle=ambient.days_in_a_cicle,
            max_actv_in_cicle=ambient.max_actv_in_cicle,
            members=MockQuerySet([to_mock_member(m) for m in ambient.members.filter(is_professor=True) if m.user]),
            classrooms=MockQuerySet([to_mock_classroom(c) for c in ambient.classrooms.all()]),
            subjects=MockQuerySet([to_mock_subject(s) for s in ambient.subjects.all()]),
            classes=MockQuerySet([to_mock_class(c) for c in ambient.classes.all()]),
            available_schedules=MockQuerySet([to_mock_schedule(s) for s in ambient.available_schedules.all()]),
            activities=MockQuerySet([])
        )

        self.professores = list(self.ambient.members.all())
        self.salas = list(self.ambient.classrooms.all())

        prof_map = {p.id: p for p in self.professores}
        room_map = {r.id: r for r in self.salas}

        self.aulas = [to_mock_activity(a, prof_map, room_map) for a in activities]
        self.periods = ambient.periods_in_a_day or 4
        self.days = ambient.days_in_a_cicle or 5
        self.tam_solution = 3 * len(self.aulas)
        self.instance_name = f"Unified_{ambient.ambientid}"
        self.LS_type = 'Best'
        self.dict_best = {self.instance_name: 0}

        self.BRKGA_parameters = {
            'p': [120, 60],
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

        self._available_keys = {
            (s.line, s.column) for s in self.ambient.available_schedules.all()
            if s is not None
        }
        if not self._available_keys:
            self._available_keys = {
                (line, col)
                for col in range(self.days)
                for line in range(self.periods)
            }
        self._professor_allowed_period_limits = self._build_professor_allowed_period_limits()

        self._class_pref = {}
        self._prof_pref = {}
        for a in self.aulas:
            if a.tclass:
                self._class_pref[a.tclass.id] = set(
                    (s.line, s.column) for s in a.tclass.prefered_schedules.all()
                )

        self._valid_positions = []
        for a in self.aulas:
            duration = a.activities_qtd or 1
            positions = []
            for col in range(self.days):
                for row in range(self.periods - duration + 1):
                    keys = [(row + offset, col) for offset in range(duration)]
                    if all(key in self._available_keys for key in keys):
                        positions.append((row, col))
            self._valid_positions.append(positions)

    def _build_professor_allowed_period_limits(self):
        limits = {}
        available_by_day = {}
        for _, col in self._available_keys:
            available_by_day[col] = available_by_day.get(col, 0) + 1

        for rule in rko_llm_constraints.load_rules(self.ambient.ambientid):
            professor_name = None
            allowed_days = None
            for cond in rule.get("conditions", []):
                if cond.get("field") == "professor" and cond.get("operator") == "==":
                    professor_name = cond.get("value")
                if cond.get("field") == "dia" and cond.get("operator") in ["!=", "not in"]:
                    raw_days = cond.get("value")
                    raw_days = raw_days if isinstance(raw_days, list) else [raw_days]
                    allowed_days = [
                        day_index for day_index in (
                            rko_llm_constraints._day_index(day) for day in raw_days
                        )
                        if day_index is not None
                    ]

            if professor_name and allowed_days:
                max_periods = sum(available_by_day.get(day, 0) for day in allowed_days)
                key = rko_llm_constraints._normalize(professor_name)
                limits[key] = min(limits.get(key, max_periods), max_periods)

        return limits

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_original_activities'] = None
        state['db_activities_map'] = {}
        state['db_professors_map'] = {}
        state['db_classrooms_map'] = {}
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def decoder(self, keys):
        timetable = {key: [] for key in self._available_keys}
        unallocated = []
        all_activities = []

        for i, a in enumerate(self.aulas):
            prof = None
            room = None
            if self.professores:
                p_idx = min(int(keys[3 * i] * len(self.professores)), len(self.professores) - 1)
                prof = self.professores[p_idx]
            if self.salas:
                r_idx = min(int(keys[3 * i + 1] * len(self.salas)), len(self.salas) - 1)
                room = self.salas[r_idx]

            positions = self._valid_positions[i]
            if positions:
                pos_idx = min(int(keys[3 * i + 2] * len(positions)), len(positions) - 1)
                selected_position = positions[pos_idx]
            else:
                selected_position = None

            db_act = self.db_activities_map.get(a.id)
            act_obj = db_act if db_act is not None else a
            all_activities.append(act_obj)

            if not prof or not room or selected_position is None:
                a.tprofessor = None
                a.tclassroom = None
                if db_act:
                    db_act.tprofessor = None
                    db_act.tclassroom = None
                unallocated.append(act_obj)
                continue

            a.tprofessor = prof
            a.tclassroom = room
            if db_act:
                db_act.tprofessor = self.db_professors_map.get(prof.id)
                db_act.tclassroom = self.db_classrooms_map.get(room.id)

            row, col = selected_position
            duration = a.activities_qtd or 1
            for offset in range(duration):
                timetable.setdefault((row + offset, col), []).append(act_obj)

        return {
            "timetable": timetable,
            "unallocated": unallocated,
            "activities": self._original_activities if self._original_activities is not None else all_activities,
        }

    def cost(self, decoded, final_solution=False):
        P_CONFLITO = 100000
        P_FORA_TURMA = 10
        P_FORA_PROF = 10
        P_NAO_ALOCADO_POR_PERIODO = 5000
        P_CAPACIDADE = 500000
        custo = 0

        timetable = decoded.get("timetable", decoded) if isinstance(decoded, dict) else decoded
        unallocated = decoded.get("unallocated", []) if isinstance(decoded, dict) else []

        scheduled_by_id = {}
        for acts in timetable.values():
            for activity in acts:
                activity_id = getattr(activity, "id", id(activity))
                scheduled_by_id[activity_id] = activity

        scheduled_activities = list(scheduled_by_id.values())
        for activity in unallocated:
            custo += P_NAO_ALOCADO_POR_PERIODO * (activity.activities_qtd or 1)

        max_slots = len(self._available_keys) or ((self.days or 5) * (self.periods or 4))
        max_cicle = self.ambient.max_actv_in_cicle or max_slots
        if max_cicle > max_slots:
            max_cicle = max_slots

        prof_periods = {p.id: 0 for p in self.professores}
        room_periods = {r.id: 0 for r in self.salas}
        for activity in scheduled_activities:
            duration = activity.activities_qtd or 1
            if activity.tprofessor:
                prof_periods[activity.tprofessor.id] = prof_periods.get(activity.tprofessor.id, 0) + duration
            if activity.tclassroom:
                room_periods[activity.tclassroom.id] = room_periods.get(activity.tclassroom.id, 0) + duration

            if activity.tclassroom and activity.tclass:
                if activity.tclassroom.classroom_capacity < activity.tclass.number_of_students:
                    custo += P_CAPACIDADE

            score_prof = 1
            if activity.tclass and activity.tprofessor:
                class_pref = activity.tclass.favorite_professors.filter(professor=activity.tprofessor).first()
                score_prof += class_pref.professor_weight if class_pref else 5

                subject_pref = activity.tsubject.favorite_professors.filter(professor=activity.tprofessor).first()
                score_prof += subject_pref.professor_weight if subject_pref else 5
            custo += 100000 if score_prof == 0 else max(0, 200 - score_prof)

            score_room = 1
            if activity.tclass and activity.tclassroom:
                class_room_pref = activity.tclass.ideal_classrooms.filter(classroom=activity.tclassroom).first()
                score_room += class_room_pref.classroom_weight if class_room_pref else 5

                subject_room_pref = activity.tsubject.ideal_classrooms.filter(classroom=activity.tclassroom).first()
                score_room += subject_room_pref.classroom_weight if subject_room_pref else 5
            custo += 100000 if score_room == 0 else max(0, 200 - score_room)

            if activity.tprofessor and activity.tsubject:
                prof_sub_pref = activity.tprofessor.prefered_subjects.filter(subject=activity.tsubject).first()
                score_sub = prof_sub_pref.subject_weight if prof_sub_pref else 1
                custo += max(0, 100 - score_sub)

        for periods in prof_periods.values():
            if periods > max_cicle:
                custo += 1000000 * (periods - max_cicle)

        for periods in room_periods.values():
            if periods > max_slots:
                custo += 1000000 * (periods - max_slots)

        for (line, col), acts in timetable.items():
            for j, a in enumerate(acts):
                if a.tclass and (line, col) not in self._class_pref.get(a.tclass.id, set()):
                    custo += P_FORA_TURMA
                if a.tprofessor:
                    pref = self._prof_pref.setdefault(
                        a.tprofessor.id,
                        set((s.line, s.column) for s in a.tprofessor.prefered_schedules.all())
                    )
                    if (line, col) not in pref:
                        custo += P_FORA_PROF

                for k in range(j + 1, len(acts)):
                    b = acts[k]
                    if a.tclass and b.tclass and a.tclass.id == b.tclass.id:
                        custo += P_CONFLITO
                    if a.tprofessor and b.tprofessor and a.tprofessor.id == b.tprofessor.id:
                        custo += P_CONFLITO
                    if a.tclassroom and b.tclassroom and a.tclassroom.id == b.tclassroom.id:
                        custo += P_CONFLITO

        custo = rko_llm_constraints.apply_attribution_constraints(
            custo,
            scheduled_activities,
            self.ambient.ambientid,
            self._professor_allowed_period_limits,
        )
        return rko_llm_constraints.apply_allocation_constraints(
            custo,
            timetable,
            self.ambient.ambientid,
        )
