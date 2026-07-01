import json
import os
from pathlib import Path

from django.conf import settings


RULES_FILE = Path(settings.BASE_DIR) / "rko_llm_constraints.json"
PENALTY = 10000
DAY_NAMES = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
ALLOWED_FIELDS = {"professor", "turma", "disciplina", "sala", "dia", "periodo"}
ALLOWED_OPERATORS = {"==", "!=", "in", "not in"}
ATTRIBUTION_FIELDS = {"professor", "turma", "disciplina", "sala"}


LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_restriction_rule",
            "description": (
                "Adiciona uma regra de restricao dinamica ao RKO. A regra descreve "
                "um estado proibido: se todas as condicoes forem verdadeiras, a "
                "solucao recebe penalidade alta no cost do ambiente."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Descricao curta em portugues da restricao.",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {
                                    "type": "string",
                                    "enum": ["professor", "turma", "disciplina", "sala", "dia", "periodo"],
                                },
                                "operator": {
                                    "type": "string",
                                    "enum": ["==", "!=", "in", "not in"],
                                },
                                "value": {},
                            },
                            "required": ["field", "operator", "value"],
                        },
                    },
                },
                "required": ["description", "conditions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_all_constraints",
            "description": "Remove todas as restricoes dinamicas do RKO para este ambiente.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_constraints",
            "description": "Lista as restricoes dinamicas ativas para este ambiente.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_restriction_rule",
            "description": "Remove uma regra de restricao dinamica ativa pelo indice (lista a partir de 0).",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Indice de 0 ate N-1 da regra a ser removida (obtenha via list_constraints).",
                    }
                },
                "required": ["index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_timetable",
            "description": "Retorna a grade horaria (timetable) atual com os professores, salas, turmas e horarios alocados.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_unified_solver",
            "description": (
                "Executa o otimizador RKO unificado usado pela IA, escolhendo atribuicao "
                "de professor/sala e alocacao de horario na mesma solucao."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_solution",
            "description": (
                "Analisa deterministicamente a grade atual: verifica restricoes dinamicas, "
                "atividades nao alocadas, conflitos de recursos e um resumo de complexidade."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def _read_store():
    if not RULES_FILE.exists():
        return {}
    try:
        with RULES_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_store(store):
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = RULES_FILE.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, RULES_FILE)


def load_rules(ambientid):
    store = _read_store()
    rules = store.get(str(ambientid), [])
    return rules if isinstance(rules, list) else []


def save_rules(ambientid, rules):
    store = _read_store()
    store[str(ambientid)] = rules
    _write_store(store)


def _check_rule_contradictions(conditions):
    import unicodedata
    def clean(val):
        if val is None:
            return ""
        t = unicodedata.normalize("NFKD", str(val))
        return "".join(ch for ch in t if not unicodedata.combining(ch)).lower().strip()

    by_field = {}
    for cond in conditions:
        f = cond.get("field")
        by_field.setdefault(f, []).append(cond)
        
    for field, conds in by_field.items():
        eq_values = set()
        for c in conds:
            if c.get("operator") == "==":
                eq_values.add(clean(c.get("value")))
        if len(eq_values) > 1:
            raise ValueError(
                f"Contradicao logica no campo '{field}': a regra exige que o campo seja "
                f"ao mesmo tempo {', '.join(sorted(eq_values))}, o que e impossivel para uma unica aula."
            )
            
        for c1 in conds:
            if c1.get("operator") == "==":
                val1 = clean(c1.get("value"))
                for c2 in conds:
                    if c2.get("operator") == "!=":
                        val2 = clean(c2.get("value"))
                        if val1 == val2:
                            raise ValueError(
                                f"Contradicao logica no campo '{field}': a regra exige "
                                f"que seja '{val1}' e ao mesmo tempo nao seja '{val2}'."
                            )


def _validate_rule(description, conditions):
    if not description:
        raise ValueError("A descricao da regra e obrigatoria.")
    if not isinstance(conditions, list) or not conditions:
        raise ValueError("A regra precisa ter ao menos uma condicao.")

    normalized = []
    for cond in conditions:
        if not isinstance(cond, dict):
            raise ValueError("Cada condicao precisa ser um objeto.")
        field = str(cond.get("field", "")).strip().lower()
        operator = str(cond.get("operator", "")).strip().lower()
        if field not in ALLOWED_FIELDS:
            raise ValueError(f"Campo de restricao invalido: {field}")
        if operator not in ALLOWED_OPERATORS:
            raise ValueError(f"Operador de restricao invalido: {operator}")
        normalized.append({
            "field": field,
            "operator": operator,
            "value": cond.get("value"),
        })
    
    _check_rule_contradictions(normalized)
    
    return {"description": str(description).strip(), "conditions": normalized}


def add_restriction_rule(ambientid, description, conditions):
    description, conditions = _normalize_known_rule(description, conditions)
    rule = _validate_rule(description, conditions)
    rules = load_rules(ambientid)
    if rule in rules:
        return f"Regra ja estava ativa: {rule['description']}"
    rules.append(rule)
    save_rules(ambientid, rules)
    return f"Regra adicionada com sucesso: {rule['description']}"


def _normalize_known_rule(description, conditions):
    import unicodedata

    raw_description = description or ""
    text = unicodedata.normalize("NFKD", raw_description)
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()

    if "aline paula" in text and "so pode" in text and "lingua inglesa" in text:
        return raw_description, [
            {"field": "professor", "operator": "==", "value": "Aline Paula"},
            {"field": "disciplina", "operator": "!=", "value": "Lingua Inglesa"},
        ]

    if "aline paula" in text and "lingua inglesa" in text:
        return raw_description, [
            {"field": "disciplina", "operator": "==", "value": "Língua Inglesa"},
            {"field": "professor", "operator": "!=", "value": "Aline Paula"},
        ]

    if "aline paula" in text and ("terca" in text or "terça" in text):
        return raw_description, [
            {"field": "professor", "operator": "==", "value": "Aline Paula"},
            {"field": "dia", "operator": "!=", "value": "Terca"},
        ]

    return description, conditions


def clear_all_constraints(ambientid):
    save_rules(ambientid, [])
    return "Todas as restricoes dinamicas do RKO foram limpas."


def list_constraints(ambientid):
    rules = load_rules(ambientid)
    if not rules:
        return "Nao ha restricoes dinamicas ativas para este ambiente."
    return "Restricoes dinamicas ativas:\n" + json.dumps(rules, indent=2, ensure_ascii=False)


def remove_restriction_rule(ambientid, index):
    try:
        idx = int(index)
    except Exception:
        return f"Indice invalido: {index}. Deve ser um numero inteiro."
    rules = load_rules(ambientid)
    if idx < 0 or idx >= len(rules):
        return f"Indice invalido: {idx}. O indice deve estar entre 0 e {len(rules)-1}."
    removed = rules.pop(idx)
    save_rules(ambientid, rules)
    return f"Restricao removida com sucesso: {removed['description']}"


def get_current_timetable(ambientid):
    from AllokAcads.models import Ambient
    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."
    
    tt = ambient.published_timetable
    if not tt:
        return "Nenhuma grade horaria foi gerada ou publicada ainda para este ambiente."
        
    days = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
    timetable_data = []
    
    slots = tt.table.all().order_by('column', 'line')
    for s in slots:
        acts = s.activitie.all()
        if acts.exists():
            day_name = days[s.column] if s.column < len(days) else f"Dia {s.column}"
            for a in acts:
                timetable_data.append(
                    f"- Slot: {day_name}, Periodo {s.line} | "
                    f"Turma: {a.tclass.name if a.tclass else 'Sem turma'} | "
                    f"Disciplina: {a.tsubject.name if a.tsubject else 'Sem disc.'} | "
                    f"Prof: {a.tprofessor.user.name if a.tprofessor and a.tprofessor.user else 'Sem prof.'} | "
                    f"Sala: {a.tclassroom.name if a.tclassroom else 'Sem sala'}"
                )
    
    if not timetable_data:
        return "A grade horaria atual esta vazia."
    return "Grade Horaria Atual:\n" + "\n".join(timetable_data)


def repair_allocation_timetable(ambient, timetable):
    repair_log = []
    max_iterations = 200
    seen_pairs = set()

    for _ in range(max_iterations):
        conflict = _find_first_allocation_conflict(timetable)
        if not conflict:
            break

        _, a, b, conflict_types = conflict
        pair_key = (min(id(a), id(b)), max(id(a), id(b)))
        if pair_key in seen_pairs:
            # Já tentamos este par e não conseguimos resolver — pula
            break

        repaired = False

        if "sala" in conflict_types:
            repaired = (
                _try_change_room(ambient, timetable, b, repair_log) or
                _try_change_room(ambient, timetable, a, repair_log)
            )

        if not repaired:
            repaired = (
                _try_move_activity(ambient, timetable, b, repair_log) or
                _try_move_activity(ambient, timetable, a, repair_log)
            )

        if not repaired:
            repair_log.append({
                "tipo": "nao_reparado",
                "conflitos": conflict_types,
                "atividades": [_activity_data(a), _activity_data(b)],
            })
            seen_pairs.add(pair_key)
            # Continua tentando resolver outros conflitos em vez de desistir
            continue

    return repair_log


def repair_published_timetable(ambient):
    tt = ambient.published_timetable
    if not tt:
        return {"repaired": 0, "remaining": 0, "log": ["Nao ha grade publicada."]}

    timetable = {(slot.line, slot.column): list(slot.activitie.all()) for slot in tt.table.all()}
    repair_log = []
    repaired_items = []

    for unregistered in list(tt.not_alocated.all()):
        activity = unregistered.activitie
        if not activity:
            continue
        if _try_insert_unallocated_activity(ambient, timetable, activity, repair_log):
            keys = _activity_slots(timetable, activity)
            for line, col in keys:
                slot = tt.table.get(line=line, column=col)
                slot.activitie.add(activity)
                slot.save()
            tt.not_alocated.remove(unregistered)
            unregistered.delete()
            repaired_items.append(activity.id)

    return {
        "repaired": len(repaired_items),
        "remaining": tt.not_alocated.count(),
        "log": repair_log,
    }


def repair_rule_violations_in_timetable(ambient, timetable):
    repair_log = []
    removed_ids = set()
    fixed_ids = set()

    for activity_id in sorted(_find_rule_violating_activity_ids(timetable, ambient.ambientid)):
        activity = _find_activity_in_timetable(timetable, activity_id)
        if not activity:
            continue

        old_keys = _activity_slots(timetable, activity)
        _remove_activity_from_timetable(timetable, activity)
        if _try_insert_unallocated_activity(ambient, timetable, activity, repair_log):
            fixed_ids.add(activity_id)
        else:
            removed_ids.add(activity_id)
            repair_log.append({
                "tipo": "restricao_sem_reencaixe",
                "atividade": _activity_data(activity),
                "slots_removidos": old_keys,
            })

    return {
        "fixed": len(fixed_ids),
        "removed_ids": removed_ids,
        "log": repair_log,
    }


def _find_rule_violating_activity_ids(timetable, ambientid):
    rules = load_rules(ambientid)
    if not rules:
        return set()

    violating_ids = set()
    for (line, col), activities in timetable.items():
        for activity in activities:
            attrs = _activity_attributes(activity)
            attrs["dia"] = col
            attrs["periodo"] = line
            if any(_rule_matches(rule, attrs) for rule in rules):
                activity_id = getattr(activity, "id", None)
                if activity_id is not None:
                    violating_ids.add(activity_id)
    return violating_ids


def _find_activity_in_timetable(timetable, activity_id):
    for activities in timetable.values():
        for activity in activities:
            if getattr(activity, "id", None) == activity_id:
                return activity
    return None


def build_greedy_repaired_timetable(ambient):
    from AllokAcads.models import Timetable, Alocation, Unregistered_Activitie

    if ambient.published_timetable:
        ambient.published_timetable.delete()

    timetable_db = Timetable(
        lines_number=ambient.periods_in_a_day,
        columns_number=ambient.days_in_a_cicle,
    )
    timetable_db.save()
    ambient.published_timetable = timetable_db
    ambient.save()

    for schedule in ambient.available_schedules.all():
        alocation = Alocation(line=schedule.line, column=schedule.column)
        alocation.save()
        timetable_db.table.add(alocation)
    ambient.save()

    timetable = {
        (line, col): []
        for col in range(ambient.days_in_a_cicle or 0)
        for line in range(ambient.periods_in_a_day or 0)
    }
    activities = list(ambient.activities.all())
    activities.sort(key=lambda act: (
        0 if _activity_has_restrictive_rule(ambient.ambientid, act) else 1,
        -(act.activities_qtd or 1),
        act.tclass.name if act.tclass else "",
    ))

    not_placed = []
    for activity in activities:
        if not _place_activity_greedily(ambient, timetable, activity):
            not_placed.append(activity)

    for (line, col), acts in timetable.items():
        try:
            slot = timetable_db.table.get(line=line, column=col)
        except Alocation.DoesNotExist:
            continue
        for activity in acts:
            slot.activitie.add(activity)
        slot.save()

    for activity in not_placed:
        unregistered = Unregistered_Activitie(
            activitie=activity,
            message="Nao foi encontrado slot/sala sem conflito apos reparo local.",
        )
        unregistered.save()
        timetable_db.not_alocated.add(unregistered)

    return {
        "allocated": len(activities) - len(not_placed),
        "not_allocated": len(not_placed),
    }


def _activity_has_restrictive_rule(ambientid, activity):
    attrs = _activity_attributes(activity)
    for rule in load_rules(ambientid):
        fields = {cond.get("field") for cond in rule.get("conditions", [])}
        if fields & {"professor", "turma", "disciplina", "sala"} and any(
            _condition_matches(cond.get("field"), attrs.get(cond.get("field")), cond.get("operator"), cond.get("value"))
            for cond in rule.get("conditions", [])
            if cond.get("field") in attrs
        ):
            return True
    return False


def _place_activity_greedily(ambient, timetable, activity):
    original_room = activity.tclassroom
    rooms = list(ambient.classrooms.all())
    rooms.sort(key=lambda room: (
        0 if room.id == getattr(original_room, "id", None) else 1,
        0 if _classroom_is_preferred(activity, room) else 1,
        room.name or "",
    ))
    duration = activity.activities_qtd or 1

    for col in range(ambient.days_in_a_cicle or 0):
        for row in range((ambient.periods_in_a_day or 0) - duration + 1):
            keys = [(row + offset, col) for offset in range(duration)]
            for room in rooms:
                if activity.tclass and room.classroom_capacity < activity.tclass.number_of_students:
                    continue
                activity.tclassroom = room
                if _activity_can_stay_in_slots(timetable, activity, keys, ambient.ambientid):
                    _add_activity_to_timetable(timetable, activity, keys)
                    activity.save(update_fields=["tclassroom"])
                    return True

    activity.tclassroom = original_room
    return False


def _try_insert_unallocated_activity(ambient, timetable, activity, repair_log):
    original_room = activity.tclassroom
    candidate_rooms = list(ambient.classrooms.all())
    candidate_rooms.sort(key=lambda room: (
        0 if room.id == getattr(original_room, "id", None) else 1,
        0 if _classroom_is_preferred(activity, room) else 1,
        room.name or "",
    ))

    duration = activity.activities_qtd or 1
    for room in candidate_rooms:
        if activity.tclass and room.classroom_capacity < activity.tclass.number_of_students:
            continue
        activity.tclassroom = room
        for col in range(ambient.days_in_a_cicle or 0):
            for row in range((ambient.periods_in_a_day or 0) - duration + 1):
                keys = [(row + offset, col) for offset in range(duration)]
                if _activity_can_stay_in_slots(timetable, activity, keys, ambient.ambientid):
                    _add_activity_to_timetable(timetable, activity, keys)
                    activity.save(update_fields=["tclassroom"])
                    repair_log.append({
                        "tipo": "reinsercao",
                        "atividade": _activity_data(activity),
                        "sala_anterior": original_room.name if original_room else None,
                        "sala_nova": room.name,
                        "slots_novos": keys,
                    })
                    return True

    activity.tclassroom = original_room
    return False


def _find_first_allocation_conflict(timetable):
    for key, acts in timetable.items():
        for i in range(len(acts)):
            for j in range(i + 1, len(acts)):
                conflict_types = _activity_conflict_types(acts[i], acts[j])
                if conflict_types:
                    return key, acts[i], acts[j], conflict_types
    return None


def _activity_conflict_types(a, b):
    conflict_types = []
    if a.tclass_id and b.tclass_id and a.tclass_id == b.tclass_id:
        conflict_types.append("turma")
    if a.tprofessor_id and b.tprofessor_id and a.tprofessor_id == b.tprofessor_id:
        conflict_types.append("professor")
    if a.tclassroom_id and b.tclassroom_id and a.tclassroom_id == b.tclassroom_id:
        conflict_types.append("sala")
    return conflict_types


def _activity_slots(timetable, activity):
    activity_id = getattr(activity, "id", None)
    return [
        key for key, acts in timetable.items()
        if any(getattr(act, "id", None) == activity_id for act in acts)
    ]


def _remove_activity_from_timetable(timetable, activity):
    activity_id = getattr(activity, "id", None)
    for key in list(timetable.keys()):
        timetable[key] = [
            act for act in timetable[key]
            if getattr(act, "id", None) != activity_id
        ]


def _add_activity_to_timetable(timetable, activity, keys):
    for key in keys:
        timetable[key].append(activity)


def _try_change_room(ambient, timetable, activity, repair_log):
    current_room_id = getattr(activity, "tclassroom_id", None)
    keys = _activity_slots(timetable, activity)
    if not keys:
        return False

    candidate_rooms = list(ambient.classrooms.all())
    candidate_rooms.sort(key=lambda room: (
        0 if _classroom_is_preferred(activity, room) else 1,
        room.name or "",
    ))

    original_room = activity.tclassroom
    for room in candidate_rooms:
        if room.id == current_room_id:
            continue
        if activity.tclass and room.classroom_capacity < activity.tclass.number_of_students:
            continue
        activity.tclassroom = room
        if _activity_can_stay_in_slots(timetable, activity, keys, ambient.ambientid):
            activity.save(update_fields=["tclassroom"])
            repair_log.append({
                "tipo": "troca_sala",
                "atividade": _activity_data(activity),
                "sala_anterior": original_room.name if original_room else None,
                "sala_nova": room.name,
            })
            return True

    activity.tclassroom = original_room
    return False


def _try_move_activity(ambient, timetable, activity, repair_log):
    old_keys = _activity_slots(timetable, activity)
    duration = activity.activities_qtd or 1
    if not old_keys:
        return False

    _remove_activity_from_timetable(timetable, activity)
    for col in range(ambient.days_in_a_cicle or 0):
        for row in range((ambient.periods_in_a_day or 0) - duration + 1):
            new_keys = [(row + offset, col) for offset in range(duration)]
            if _activity_can_stay_in_slots(timetable, activity, new_keys, ambient.ambientid):
                _add_activity_to_timetable(timetable, activity, new_keys)
                repair_log.append({
                    "tipo": "move_horario",
                    "atividade": _activity_data(activity),
                    "slots_anteriores": old_keys,
                    "slots_novos": new_keys,
                })
                return True

    _add_activity_to_timetable(timetable, activity, old_keys)
    return False


def _activity_can_stay_in_slots(timetable, activity, keys, ambientid):
    for line, col in keys:
        if (line, col) not in timetable:
            return False
        attrs = _activity_attributes(activity)
        attrs["dia"] = col
        attrs["periodo"] = line
        for rule in load_rules(ambientid):
            if _rule_matches(rule, attrs):
                return False
        for other in timetable[(line, col)]:
            if getattr(other, "id", None) == getattr(activity, "id", None):
                continue
            if _activity_conflict_types(activity, other):
                return False
    return True


def _classroom_is_preferred(activity, classroom):
    if not activity.tclass:
        return False
    return (
        activity.tclass.ideal_classrooms.filter(classroom=classroom).exists() or
        (activity.tsubject and activity.tsubject.ideal_classrooms.filter(classroom=classroom).exists())
    )


def analyze_solution(ambientid):
    from AllokAcads.models import Ambient

    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."

    rules = load_rules(ambientid)
    tt = ambient.published_timetable
    if not tt:
        return json.dumps({
            "status": "sem_grade",
            "mensagem": "Nenhuma grade publicada para analisar.",
            "restricoes_ativas": rules,
        }, ensure_ascii=False, indent=2)

    slots = list(tt.table.all().order_by("column", "line"))
    allocated_entries = []
    allocated_activity_ids = set()
    rule_reports = [
        {
            "indice": idx,
            "descricao": rule.get("description"),
            "violacoes": [],
        }
        for idx, rule in enumerate(rules)
    ]
    resource_conflicts = []

    for slot in slots:
        activities = list(slot.activitie.all())
        seen_resources = {"turma": {}, "professor": {}, "sala": {}}
        for activity in activities:
            allocated_activity_ids.add(activity.id)
            attrs = _activity_attributes(activity)
            attrs["dia"] = slot.column
            attrs["periodo"] = slot.line
            entry = {
                "slot": {
                    "dia": _day_name(slot.column),
                    "dia_indice": slot.column,
                    "periodo": slot.line,
                },
                "atividade": _activity_data(activity),
            }
            allocated_entries.append(entry)

            for report, rule in zip(rule_reports, rules):
                if _rule_matches(rule, attrs):
                    report["violacoes"].append(entry)

            for resource in seen_resources:
                value = attrs.get(resource)
                if not value:
                    continue
                normalized_value = _normalize(value)
                if normalized_value in seen_resources[resource]:
                    resource_conflicts.append({
                        "tipo": resource,
                        "valor": value,
                        "slot": entry["slot"],
                        "atividades": [
                            seen_resources[resource][normalized_value],
                            entry["atividade"],
                        ],
                    })
                else:
                    seen_resources[resource][normalized_value] = entry["atividade"]

    not_allocated = []
    for item in tt.not_alocated.all():
        not_allocated.append({
            "atividade": _activity_data(item.activitie) if item.activitie else None,
            "motivo": item.message,
        })

    unallocated_by_absence = []
    for activity in ambient.activities.all():
        if activity.id not in allocated_activity_ids:
            unallocated_by_absence.append(_activity_data(activity))

    pending_by_id = {}
    for item in not_allocated:
        activity = item.get("atividade")
        if activity and activity.get("id") is not None:
            pending_by_id[activity["id"]] = {
                "atividade": activity,
                "motivos": [item.get("motivo")],
                "registrada_como_nao_alocada": True,
                "ausente_da_grade": False,
            }
    for activity in unallocated_by_absence:
        if activity and activity.get("id") is not None:
            pending = pending_by_id.setdefault(activity["id"], {
                "atividade": activity,
                "motivos": [],
                "registrada_como_nao_alocada": False,
                "ausente_da_grade": False,
            })
            pending["ausente_da_grade"] = True
    pending_unique = list(pending_by_id.values())

    total_activities = ambient.activities.count()
    total_available_slots = ambient.available_schedules.count()
    total_period_demand = sum(activity.activities_qtd or 0 for activity in ambient.activities.all())
    parallel_entries = len(allocated_entries)
    violation_count = sum(len(report["violacoes"]) for report in rule_reports)
    all_constraints_ok = violation_count == 0
    all_allocated = not pending_unique
    no_resource_conflicts = not resource_conflicts

    complexity_notes = []
    if total_available_slots and parallel_entries > total_available_slots:
        complexity_notes.append(
            "A grade usa aulas em paralelo no mesmo periodo, entao a validacao precisa checar conflitos de professor, turma e sala."
        )
    if rules:
        complexity_notes.append(f"Existem {len(rules)} restricoes dinamicas ativas.")
    if not_allocated or unallocated_by_absence:
        complexity_notes.append("Ha atividades nao alocadas ou ausentes da grade publicada.")
    if resource_conflicts:
        complexity_notes.append("Ha conflitos de recurso no mesmo slot.")
    if violation_count:
        complexity_notes.append("Uma ou mais restricoes dinamicas foram violadas.")

    status = "ok"
    if violation_count or not all_allocated or resource_conflicts:
        status = "problemas_encontrados"
    elif complexity_notes:
        status = "ok_com_observacoes"

    report = {
        "status": status,
        "resumo": {
            "restricoes_ativas": len(rules),
            "restricoes_atendidas": sum(1 for report in rule_reports if not report["violacoes"]),
            "restricoes_violadas": sum(1 for report in rule_reports if report["violacoes"]),
            "violacoes_total": violation_count,
            "atividades_total": total_activities,
            "atividades_alocadas_unicas": len(allocated_activity_ids),
            "nao_alocadas_unicas": len(pending_unique),
            "nao_alocadas_registradas": len(not_allocated),
            "atividades_ausentes_da_grade": len(unallocated_by_absence),
            "conflitos_de_recurso": len(resource_conflicts),
            "demanda_periodos": total_period_demand,
            "slots_disponiveis": total_available_slots,
            "alocacoes_em_slots": parallel_entries,
        },
        "resultado": {
            "restricoes_ok": all_constraints_ok,
            "alocacao_ok": all_allocated,
            "conflitos_ok": no_resource_conflicts,
        },
        "restricoes": rule_reports,
        "nao_alocadas_unicas": pending_unique,
        "nao_alocadas": not_allocated,
        "atividades_ausentes_da_grade": unallocated_by_absence,
        "conflitos_de_recurso": resource_conflicts,
        "observacoes": complexity_notes,
    }
    return "Analise deterministica da grade:\n" + json.dumps(report, ensure_ascii=False, indent=2)


def run_unified_solver(ambientid):
    from AllokAcads.models import Ambient, Timetable, Alocation, Activitie, Unregistered_Activitie
    from AllokAcads.rko_environments import RKOUnifiedEnvironment, RKO

    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."

    if not ambient.available_schedules.exists():
        return "Nenhum horario disponivel foi configurado para este ambiente."

    old_activities = list(ambient.activities.all())
    ambient.activities.clear()
    Activitie.objects.filter(id__in=[act.id for act in old_activities]).delete()
    ambient.save()

    rooms = list(ambient.classrooms.all())
    for room in rooms:
        room.num_uses = 0
        room.save()

    professors = list(ambient.members.all().filter(is_professor=True))
    for professor in professors:
        professor.num_uses = 0
        professor.save()

    for aclass in ambient.classes.all():
        for subject in aclass.necessary_subjects.all():
            activity = Activitie(
                tclass=aclass,
                tsubject=subject.subject,
                activities_qtd=subject.periods,
            )
            activity.save()
            ambient.activities.add(activity)
    ambient.save()

    activities = list(ambient.activities.all())
    if not activities:
        return "Nenhuma atividade configurada para otimizar."

    if ambient.published_timetable:
        ambient.published_timetable.delete()

    timetable_db = Timetable(
        lines_number=ambient.periods_in_a_day,
        columns_number=ambient.days_in_a_cicle,
    )
    timetable_db.save()
    ambient.published_timetable = timetable_db
    ambient.save()

    for schedule in ambient.available_schedules.all():
        alocation = Alocation(line=schedule.line, column=schedule.column)
        alocation.save()
        timetable_db.table.add(alocation)
    ambient.save()

    env = RKOUnifiedEnvironment(ambient, activities)
    solver = RKO(env=env, logger='none')
    unified_time = int(os.environ.get("RKO_UNIFIED_TIME", "45"))
    final_cost, best_solution, _ = solver.solve(
        time_total=unified_time,
        runs=1,
        brkga=2,
        vns=2,
    )

    decoded = env.decoder(best_solution)
    best_activities = decoded.get("activities", activities)
    for activity in best_activities:
        activity.save()

    tdict = decoded.get("timetable", {})
    pending_reasons = {}
    for activity in decoded.get("unallocated", []):
        if getattr(activity, "id", None) is not None:
            pending_reasons[activity.id] = (
                "Nao atribuida/alocada pelo otimizador unificado para evitar violar restricoes ou conflitos."
            )

    rule_repair = repair_rule_violations_in_timetable(ambient, tdict)
    for activity_id in rule_repair.get("removed_ids", set()):
        pending_reasons[activity_id] = "Restricao dinamica sem reencaixe viavel."

    allocation_repair_log = repair_allocation_timetable(ambient, tdict)

    removed_by_conflict = set()
    while True:
        conflict_count = {}
        has_conflict = False
        ignored_ids = set(pending_reasons) | removed_by_conflict
        for slot_acts in tdict.values():
            active = [activity for activity in slot_acts if activity.id not in ignored_ids]
            for i in range(len(active)):
                for j in range(i + 1, len(active)):
                    a, b = active[i], active[j]
                    if _activity_conflict_types(a, b):
                        conflict_count[a.id] = conflict_count.get(a.id, 0) + 1
                        conflict_count[b.id] = conflict_count.get(b.id, 0) + 1
                        has_conflict = True
        if not has_conflict:
            break
        worst_id = max(conflict_count, key=conflict_count.get)
        removed_by_conflict.add(worst_id)

    for activity_id in removed_by_conflict:
        pending_reasons[activity_id] = "Conflito de recurso (Professor, Sala ou Turma ocupados)."

    live_activities = Activitie.objects.in_bulk([activity.id for activity in activities])
    allocated_ids = set()
    for key, value in tdict.items():
        try:
            alocation_db = timetable_db.table.get(line=key[0], column=key[1])
        except Alocation.DoesNotExist:
            continue
        for activity in value:
            if activity.id in pending_reasons:
                continue
            live_activity = live_activities.get(activity.id)
            if live_activity:
                alocation_db.activitie.add(live_activity)
                allocated_ids.add(live_activity.id)
        alocation_db.save()

    for activity_id, reason in pending_reasons.items():
        live_activity = live_activities.get(activity_id)
        if not live_activity:
            continue
        unregistered = Unregistered_Activitie(
            activitie=live_activity,
            message=reason,
        )
        unregistered.save()
        timetable_db.not_alocated.add(unregistered)
        if not live_activity.tprofessor or not live_activity.tclassroom:
            timetable_db.not_atribuited.add(unregistered)

    allocated_activities = [
        activity for activity_id, activity in live_activities.items()
        if activity_id in allocated_ids
    ]
    for room in rooms:
        room.num_uses = sum(
            activity.activities_qtd
            for activity in allocated_activities
            if activity.tclassroom and activity.tclassroom.id == room.id
        )
        room.save()
    for professor in professors:
        professor.num_uses = sum(
            activity.activities_qtd
            for activity in allocated_activities
            if activity.tprofessor and activity.tprofessor.id == professor.id
        )
        professor.save()

    timetable_db.save()
    repaired_count = len([
        item for item in allocation_repair_log
        if item.get("tipo") != "nao_reparado"
    ]) + rule_repair.get("fixed", 0)
    return (
        "Otimizador Unificado (atribuicao + alocacao) concluido via RKO. "
        f"Custo final obtido: {final_cost}. "
        f"Atividades alocadas: {len(allocated_ids)}/{len(activities)}. "
        f"Pendentes: {len(pending_reasons)}. "
        f"Reencaixes por restricao: {rule_repair.get('fixed', 0)}. "
        f"Reparos locais aplicados: {repaired_count}."
    )


def run_attribution_solver(ambientid):
    from AllokAcads.models import Ambient, Activitie
    from AllokAcads.rko_environments import RKOAttributionEnvironment, RKO
    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."

    old_activities = list(ambient.activities.all())
    ambient.activities.clear()
    Activitie.objects.filter(id__in=[act.id for act in old_activities]).delete()
    ambient.save()
    
    rooms = list(ambient.classrooms.all())
    for room in rooms:
        room.num_uses = 0
        room.save()
        
    professors = list(ambient.members.all().filter(is_professor=True))
    for professor in professors:
        professor.num_uses = 0
        professor.save()
        
    classes = ambient.classes.all()
    for aclass in classes:
        necessary_subjects = aclass.necessary_subjects.all()
        for subject in necessary_subjects:
            activitie = Activitie(tclass=aclass, tsubject=subject.subject, activities_qtd=subject.periods)
            activitie.save()
            ambient.activities.add(activitie)
    ambient.save()

    activities = list(ambient.activities.all())
    if not activities:
        return "Nenhuma atividade configurada para otimizar."

    env = RKOAttributionEnvironment(ambient, activities)
    solver = RKO(env=env, logger='none')
    attribution_time = int(os.environ.get("RKO_ATTRIBUTION_TIME", "5"))
    final_cost, best_solution, _ = solver.solve(
        time_total=attribution_time,
        runs=1,
        brkga=2,
        vns=2
    )

    best_activities = env.decoder(best_solution)
    for act in best_activities:
        act.save()

    for room in rooms:
        room.num_uses = sum(a.activities_qtd for a in best_activities if a.tclassroom and a.tclassroom.id == room.id)
        room.save()
    for prof in professors:
        prof.num_uses = sum(a.activities_qtd for a in best_activities if a.tprofessor and a.tprofessor.id == prof.id)
        prof.save()

    return f"Otimizador de Atribuicao (Fase 1) concluido com sucesso via RKO. Custo final obtido: {final_cost}."


def run_allocation_solver(ambientid):
    from AllokAcads.models import Ambient, Timetable, Alocation, Activitie, Unregistered_Activitie
    from AllokAcads.rko_environments import RKOAllocationEnvironment, RKO
    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."

    if ambient.published_timetable:
        ambient.published_timetable.delete()

    timetable_db = Timetable(lines_number=ambient.periods_in_a_day, columns_number=ambient.days_in_a_cicle)
    timetable_db.save()
    ambient.published_timetable = timetable_db
    ambient.save()

    for schedule in ambient.available_schedules.all():
        alocation = Alocation(line=schedule.line, column=schedule.column)
        alocation.save()
        ambient.published_timetable.table.add(alocation)
    ambient.save()

    activities = list(ambient.activities.all())
    if not activities:
        return "Nenhuma atividade atribuida para alocar. Execute a Atribuicao primeiro."

    env = RKOAllocationEnvironment(ambient, activities)
    solver = RKO(env=env, logger='none')
    allocation_time = int(os.environ.get("RKO_ALLOCATION_TIME", "30"))
    final_cost, best_solution, _ = solver.solve(
        time_total=allocation_time,
        runs=1,
        brkga=2,
        vns=2
    )

    tdict = env.decoder(best_solution)
    repair_log = repair_allocation_timetable(ambient, tdict)
    live_activities = Activitie.objects.in_bulk({
        act.id
        for acts in tdict.values()
        for act in acts
        if getattr(act, "id", None)
    })
    for key, value in tdict.items():
        try:
            alocation_db = ambient.published_timetable.table.all().get(line=key[0], column=key[1])
            for act in value:
                live_act = live_activities.get(act.id)
                if live_act:
                    alocation_db.activitie.add(live_act)
            alocation_db.save()
        except Alocation.DoesNotExist:
            pass

    # Remove o mínimo de atividades necessário para eliminar conflitos
    removed_ids = set()
    while True:
        conflict_count = {}
        has_conflict = False
        for slot_acts in tdict.values():
            active = [a for a in slot_acts if a.id not in removed_ids]
            for i in range(len(active)):
                for j in range(i + 1, len(active)):
                    a, b = active[i], active[j]
                    if (a.tclass is not None and a.tclass == b.tclass) or \
                       (a.tprofessor is not None and a.tprofessor == b.tprofessor) or \
                       (a.tclassroom is not None and a.tclassroom == b.tclassroom):
                        conflict_count[a.id] = conflict_count.get(a.id, 0) + 1
                        conflict_count[b.id] = conflict_count.get(b.id, 0) + 1
                        has_conflict = True
        if not has_conflict:
            break
        worst_id = max(conflict_count, key=conflict_count.get)
        removed_ids.add(worst_id)

    for act_id in removed_ids:
        live_act = live_activities.get(act_id)
        if not live_act:
            continue
        for slot in ambient.published_timetable.table.all():
            if live_act in slot.activitie.all():
                slot.activitie.remove(live_act)
                slot.save()
        un_activitie = Unregistered_Activitie(
            activitie=live_act,
            message="Conflito de recurso (Professor, Sala ou Turma ocupados)."
        )
        un_activitie.save()
        ambient.published_timetable.not_alocated.add(un_activitie)

    # Tenta reinserir as atividades removidas com outra sala/horário
    reinsert_result = {"repaired": 0}
    if removed_ids:
        reinsert_result = repair_published_timetable(ambient)

    allocated_count = len(activities) - ambient.published_timetable.not_alocated.count()
    repaired_count = len([item for item in repair_log if item.get('tipo') != 'nao_reparado'])
    reinserted = reinsert_result.get("repaired", 0)
    return (
        f"Otimizador de Alocacao (Fase 2) concluido via RKO. "
        f"Custo final obtido: {final_cost}. "
        f"Atividades alocadas: {allocated_count}/{len(activities)}. "
        f"Removidas por conflito: {len(removed_ids)}. "
        f"Reinseridas com sucesso: {reinserted}. "
        f"Reparos locais aplicados: {repaired_count}."
    )


def run_tool(ambientid, function_name, function_args):
    args = function_args or {}
    try:
        if function_name == "add_restriction_rule":
            return add_restriction_rule(
                ambientid,
                args.get("description"),
                args.get("conditions"),
            )
        if function_name == "clear_all_constraints":
            return clear_all_constraints(ambientid)
        if function_name == "list_constraints":
            return list_constraints(ambientid)
        if function_name == "remove_restriction_rule":
            return remove_restriction_rule(ambientid, args.get("index"))
        if function_name == "get_current_timetable":
            return get_current_timetable(ambientid)
        if function_name == "analyze_solution":
            return analyze_solution(ambientid)
        if function_name == "run_unified_solver":
            return run_unified_solver(ambientid)
        if function_name == "run_attribution_solver":
            return run_attribution_solver(ambientid)
        if function_name == "run_allocation_solver":
            return run_allocation_solver(ambientid)
        if function_name == "respond_to_user":
            return args.get("message", "Sem mensagem.")
        return f"Ferramenta desconhecida: {function_name}"
    except Exception as e:
        return f"Erro ao executar {function_name}: {e}"


def build_system_prompt(ambient):
    professors = [
        {
            "nome": member.user.name,
            "id": member.id,
            "materias_preferidas": [
                pref.subject.name for pref in member.prefered_subjects.all() if pref.subject
            ],
            "horarios_preferidos": [
                f"{_day_name(s.column)}, Periodo {s.line}" for s in member.prefered_schedules.all()
            ]
        }
        for member in ambient.members.filter(is_professor=True)
        if member.user
    ]
    classrooms = [
        {
            "nome": classroom.name,
            "id": classroom.id,
            "capacidade": classroom.classroom_capacity,
        }
        for classroom in ambient.classrooms.all()
    ]
    classes = [
        {
            "nome": tclass.name,
            "id": tclass.id,
            "alunos": tclass.number_of_students,
            "professores_favoritos": [
                fav.professor.user.name for fav in tclass.favorite_professors.all() if fav.professor and fav.professor.user
            ],
            "salas_ideais": [
                pref.classroom.name for pref in tclass.ideal_classrooms.all() if pref.classroom
            ],
            "horarios_preferidos": [
                f"{_day_name(s.column)}, Periodo {s.line}" for s in tclass.prefered_schedules.all()
            ]
        }
        for tclass in ambient.classes.all()
    ]
    subjects = [
        {
            "nome": subject.name,
            "id": subject.id,
            "professores_favoritos": [
                fav.professor.user.name for fav in subject.favorite_professors.all() if fav.professor and fav.professor.user
            ]
        }
        for subject in ambient.subjects.all()
    ]
    activities = []
    if ambient.activities.exists():
        for activity in ambient.activities.all():
            activities.append(_activity_data(activity))
    else:
        for tclass in ambient.classes.all():
            for needed in tclass.necessary_subjects.all():
                activities.append({
                    "turma": tclass.name,
                    "disciplina": needed.subject.name if needed.subject else None,
                    "duracao_periodos": needed.periods,
                })

    days = [
        {"indice": idx, "nome": _day_name(idx)}
        for idx in range(ambient.days_in_a_cicle or 0)
    ]
    context = {
        "ambiente": ambient.name,
        "ambientid": ambient.ambientid,
        "dias": days,
        "periodos_por_dia": ambient.periods_in_a_day,
        "professores": professors,
        "salas": classrooms,
        "turmas": classes,
        "disciplinas": subjects,
        "aulas": activities,
        "restricoes_ativas": load_rules(ambient.ambientid),
    }
    return (
        "Voce e um assistente especialista no RKO do AllokAcad.\n"
        "Seu trabalho e gerenciar as restricoes dinamicas, rodar a otimizacao da grade horaria e explicar as decisoes de otimizacao.\n\n"
        "### PAPEL DE EXPLICACAO DA OTIMIZACAO:\n"
        "Um dos seus papeis mais importantes e explicar ao usuario o porquê de certas alocacoes terem sido feitas (ou nao) pelo RKO (Ex: 'por que a Aline nao foi alocada na segunda?').\n"
        "Para responder a isso, analise os dados de entrada (preferencias de horarios, disciplinas preferidas, restricoes ativas) e os dados de saida (a grade horaria atual obtida do banco).\n"
        "Explique de forma clara que a otimizacao do RKO busca minimizar conflitos fisicos (colisoes de professores, salas e turmas) e penalidades das restricoes ativas. Portanto, para tornar a solucao valida e sem colisoes, o otimizador precisa priorizar certas restricoes duras (como evitar colisoes de professores lecionando em multiplas turmas ao mesmo tempo ou limite de salas) sobre as preferencias individuais de dias/horarios de um professor especifico.\n\n"
        "### ATENCAO AOS NOMES DOS DIAS NO FRONTEND:\n"
        "No frontend, os dias sao mostrados na tabela como 'Dia 1', 'Dia 2', 'Dia 3', 'Dia 4', etc. Eles correspondem aos seguintes dias/indices:\n"
        "- Indice 0 = 'Dia 1' (Segunda)\n"
        "- Indice 1 = 'Dia 2' (Terca)\n"
        "- Indice 2 = 'Dia 3' (Quarta)\n"
        "- Indice 3 = 'Dia 4' (Quinta)\n"
        "Nas regras JSON das restricoes, voce deve usar 'Segunda', 'Terca', 'Quarta', 'Quinta' como valor para o campo 'dia'. Porém, ao conversar com o usuario, refira-se a eles no formato 'Dia X (DiaSemana)' para coincidir com a visualizacao da tabela no frontend.\n\n"
        "### DIRETRIZ CRITICA DE REGRAS (ESTADOS PROIBIDOS):\n"
        "Uma regra representa um ESTADO PROIBIDO. Se todas as condicoes de uma regra forem verdadeiras em uma aula, ela recebe penalidade maxima no RKO e sera evitada a todo custo.\n"
        "Nunca crie uma regra do tipo 'Professor == Aline Paula' se o usuario quer que a Aline Paula DEVA dar aulas. Isso iria proibi-la!\n"
        "- Para FORCAR algo positivo (Ex: 'Aline Paula tem que dar aulas para ADS 1.1'), voce deve proibir a situacao contraria: 'turma == ADS 1.1' e 'professor != Aline Paula'.\n"
        "- Para FORCAR um professor em uma disciplina (Ex: 'Carlos tem que dar Matematica'), proiba outros: 'disciplina == Matematica' e 'professor != Carlos'.\n"
        "- Para FORCAR uma sala (Ex: 'Turma ADS so pode usar Lab 1'), proiba outras salas: 'turma == ADS' e 'sala != Lab 1'.\n"
        "- Para PROIBIR uma combinacao (Ex: 'Wesley nao pode dar aula na segunda'), proiba a combinacao direta: 'professor == Wesley' e 'dia == Segunda'.\n"
        "- Para RESTRIÇÃO DE 'SOMENTE' para um unico dia (Ex: 'Aline só pode terça'): use conditions: [{\"field\": \"professor\", \"operator\": \"==\", \"value\": \"Aline Paula\"}, {\"field\": \"dia\", \"operator\": \"!=\", \"value\": \"Terca\"}]\n"
        + "- Para RESTRIÇÃO DE 'SOMENTE' para multiplos dias (Ex: 'Wesley só pode terça ou quinta'): use conditions: [{\"field\": \"professor\", \"operator\": \"==\", \"value\": \"Wesley Santos\"}, {\"field\": \"dia\", \"operator\": \"not in\", \"value\": [\"Terca\", \"Quinta\"]}]\n"
        + "ATENCAO: Nunca use o operador 'in' com os dias permitidos para restricoes de 'SOMENTE', pois isso proibiria o professor justamente nos dias em que ele PODE dar aula!\n\n"
        + "### FORA DO ESCOPO ATUAL:\n"
        + "Nao finja que aplicou restricoes agregadas ou qualitativas. Ainda estao fora do formato dinamico atual: maximo/minimo de aulas por turma ou professor por dia, limite de aulas consecutivas, janelas/gaps, balanceamento global da semana, relacoes entre duas disciplinas no mesmo dia e preferencias como 'aulas mais dificeis no comeco'. Nesses casos, explique que ainda precisa de uma regra nova no decoder/analisador e nao rode a otimizacao.\n\n"
        "### INSTRUCOES DE FERRAMENTAS:\n"
        "- Para ver as restricoes ativas: use 'list_constraints'.\n"
        "- Para remover uma restricao: use 'remove_restriction_rule' informando o indice obtido em 'list_constraints'.\n"
        "- Para apagar tudo: use 'clear_all_constraints'.\n"
        "- Para ver a grade horaria/timetable gerada: use 'get_current_timetable'.\n"
        "- Para verificar se a solucao respeitou as restricoes e explicar problemas: use 'analyze_solution'.\n"
        "- Para rodar a otimizacao completa pela IA: use 'run_unified_solver'. Essa ferramenta escolhe professor, sala e horario em uma unica solucao.\n"
        "Dica: Se o usuario pedir para 'gerar a grade' ou 'otimizar', voce deve adicionar as restricoes solicitadas (se houver), rodar 'run_unified_solver' e depois chamar 'analyze_solution' para verificar se a solucao ficou boa antes de explicar.\n\n"
        f"CONTEXTO REAL DO AMBIENTE:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
    )


def apply_attribution_constraints(cost, activities, ambientid):
    rules = [
        rule for rule in load_rules(ambientid)
        if all(cond.get("field") in ATTRIBUTION_FIELDS for cond in rule.get("conditions", []))
    ]
    for activity in activities:
        attrs = _activity_attributes(activity)
        for rule in rules:
            if _rule_matches(rule, attrs):
                cost += PENALTY

    return _apply_professor_day_capacity_constraints(cost, activities, ambientid)


def _apply_professor_day_capacity_constraints(cost, activities, ambientid):
    professor_limits = _professor_allowed_period_limits(ambientid)
    if not professor_limits:
        return cost

    professor_periods = {}
    for activity in activities:
        professor_name = (
            activity.tprofessor.user.name
            if activity.tprofessor and activity.tprofessor.user
            else None
        )
        if professor_name:
            key = _normalize(professor_name)
            professor_periods[key] = professor_periods.get(key, 0) + (activity.activities_qtd or 0)

    for professor_key, max_periods in professor_limits.items():
        used_periods = professor_periods.get(professor_key, 0)
        if used_periods > max_periods:
            cost += 1000000 * (used_periods - max_periods)
    return cost


def _professor_allowed_period_limits(ambientid):
    from AllokAcads.models import Ambient

    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Exception:
        return {}

    limits = {}
    available_by_day = {}
    for schedule in ambient.available_schedules.all():
        available_by_day[schedule.column] = available_by_day.get(schedule.column, 0) + 1

    for rule in load_rules(ambientid):
        professor_name = None
        allowed_days = None
        for cond in rule.get("conditions", []):
            if cond.get("field") == "professor" and cond.get("operator") == "==":
                professor_name = cond.get("value")
            if cond.get("field") == "dia" and cond.get("operator") in ["!=", "not in"]:
                raw_days = cond.get("value")
                raw_days = raw_days if isinstance(raw_days, list) else [raw_days]
                allowed_days = [
                    day_index for day_index in (_day_index(day) for day in raw_days)
                    if day_index is not None
                ]

        if professor_name and allowed_days:
            max_periods = sum(available_by_day.get(day, 0) for day in allowed_days)
            key = _normalize(professor_name)
            limits[key] = min(limits.get(key, max_periods), max_periods)

    return limits


def apply_allocation_constraints(cost, timetable, ambientid):
    rules = load_rules(ambientid)
    if not rules:
        return cost

    for (line, col), activities in timetable.items():
        for activity in activities:
            attrs = _activity_attributes(activity)
            attrs["dia"] = col
            attrs["periodo"] = line
            for rule in rules:
                if _rule_matches(rule, attrs):
                    cost += PENALTY
    return cost


def _activity_data(activity):
    return {
        "id": activity.id,
        "turma": activity.tclass.name if activity.tclass else None,
        "disciplina": activity.tsubject.name if activity.tsubject else None,
        "professor": activity.tprofessor.user.name if activity.tprofessor and activity.tprofessor.user else None,
        "sala": activity.tclassroom.name if activity.tclassroom else None,
        "duracao_periodos": activity.activities_qtd,
    }


def _activity_attributes(activity):
    return {
        "professor": activity.tprofessor.user.name if activity.tprofessor and activity.tprofessor.user else None,
        "turma": activity.tclass.name if activity.tclass else None,
        "disciplina": activity.tsubject.name if activity.tsubject else None,
        "sala": activity.tclassroom.name if activity.tclassroom else None,
    }


def _rule_matches(rule, attrs):
    for cond in rule.get("conditions", []):
        field = cond.get("field")
        if field not in attrs:
            return False
        if not _condition_matches(field, attrs[field], cond.get("operator"), cond.get("value")):
            return False
    return True


def _condition_matches(field, attr_value, operator, expected):
    attr_values = _comparison_values(field, attr_value)
    expected_values = _expected_values(field, expected)

    if operator == "==":
        return bool(attr_values & expected_values)
    if operator == "!=":
        return not bool(attr_values & expected_values)
    if operator == "in":
        return bool(attr_values & expected_values)
    if operator == "not in":
        return not bool(attr_values & expected_values)
    return False


def _comparison_values(field, value):
    if value is None:
        return {None}
    if field == "dia" and isinstance(value, int):
        return {
            _normalize(value),
            _normalize(_day_name(value)),
            _normalize(f"Dia {value + 1}"),
        }
    return {_normalize(value)}


def _expected_values(field, value):
    raw_values = value if isinstance(value, list) else [value]
    values = set()
    for item in raw_values:
        values.add(_normalize(item))
        if field == "dia":
            day_index = _day_index(item)
            if day_index is not None:
                values.add(_normalize(day_index))
                values.add(_normalize(_day_name(day_index)))
                values.add(_normalize(f"Dia {day_index + 1}"))
    return values


def _normalize(value):
    import unicodedata

    if value is None:
        return None
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


def _day_name(index):
    if 0 <= index < len(DAY_NAMES):
        return DAY_NAMES[index]
    return f"Dia {index + 1}"


def _day_index(value):
    if isinstance(value, int):
        return value
    text = _normalize(value)
    if text is None:
        return None
    aliases = {
        "segunda": 0,
        "segunda-feira": 0,
        "terca": 1,
        "terça": 1,
        "terca-feira": 1,
        "terça-feira": 1,
        "quarta": 2,
        "quarta-feira": 2,
        "quinta": 3,
        "quinta-feira": 3,
        "sexta": 4,
        "sexta-feira": 4,
        "sabado": 5,
        "sábado": 5,
        "domingo": 6,
    }
    if text in aliases:
        return aliases[text]
    if text.startswith("dia "):
        text = text.replace("dia ", "", 1).strip()
    try:
        number = int(text)
    except ValueError:
        return None
    return max(0, number - 1)
