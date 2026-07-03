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
FIELD_LABELS = {
    "professor": "professor",
    "turma": "turma",
    "disciplina": "disciplina",
    "sala": "sala",
    "dia": "dia",
    "periodo": "periodo",
}
FIXED_RESTRICTION_TOOLS = {
    "add_required_value_constraint",
    "add_forbidden_combination_constraint",
    "add_global_allowed_values_constraint",
    "restrict_professor_days",
    "restrict_professor_subjects",
    "restrict_professor_rooms",
    "restrict_professor_periods",
    "restrict_class_days",
    "restrict_class_rooms",
    "restrict_class_periods",
    "restrict_subject_days",
    "restrict_subject_rooms",
    "restrict_subject_periods",
    "restrict_room_days",
    "restrict_room_periods",
    "require_subject_professor",
    "require_subject_room",
    "require_class_room",
    "forbid_professor_subject",
    "forbid_professor_day",
    "forbid_class_day",
    "forbid_subject_day",
}
RESTRICTION_WRITE_TOOLS = FIXED_RESTRICTION_TOOLS | {
    "add_restriction_rule",
    "add_custom_restriction_rule",
}


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

    conditions = _normalize_only_allowed_day_rule(description, conditions)

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


def _normalize_only_allowed_day_rule(description, conditions):
    text = _normalize(description) or ""
    means_only_allowed = any(term in text for term in ["so pode", "somente", "apenas"])
    if not means_only_allowed or "nao pode" in text:
        return conditions

    normalized = []
    for cond in conditions:
        if not isinstance(cond, dict):
            normalized.append(cond)
            continue
        fixed = cond.copy()
        field = str(fixed.get("field", "")).strip().lower()
        operator = str(fixed.get("operator", "")).strip().lower()
        if field == "dia":
            if operator == "in":
                fixed["operator"] = "not in"
            elif operator == "==":
                fixed["operator"] = "!="
        normalized.append(fixed)
    return normalized


def add_restriction_rule(ambientid, description, conditions, normalize=True):
    if normalize:
        description, conditions = _normalize_known_rule(ambientid, description, conditions)
    rule = _validate_rule(description, conditions)
    return _save_rule(ambientid, rule)


def _save_rule(ambientid, rule):
    rules = load_rules(ambientid)
    new_signature = _rule_signature(rule)
    for existing in rules:
        if _rule_signature(existing) == new_signature:
            return f"Regra ja estava ativa: {existing.get('description', rule['description'])}"
    rules.append(rule)
    save_rules(ambientid, rules)
    return f"Regra adicionada com sucesso: {rule['description']}"


def _rule_signature(rule):
    conditions = rule.get("conditions") if isinstance(rule, dict) else []
    parts = []
    for cond in conditions or []:
        if not isinstance(cond, dict):
            continue
        value = cond.get("value")
        if isinstance(value, list):
            value_key = tuple(sorted(str(_normalize(item)) for item in value))
        else:
            value_key = (str(_normalize(value)),)
        parts.append((
            str(cond.get("field", "")).strip().lower(),
            str(cond.get("operator", "")).strip().lower(),
            value_key,
        ))
    return tuple(sorted(parts))


def add_required_value_constraint(ambientid, args):
    source_field = _normalize_field(_get_arg(args, "source_field", "entity_field", "when_field"))
    source_value = _get_arg(args, "source_value", "source_values", "entity_value", "entity_values", "when_value")
    target_field = _normalize_field(_get_arg(args, "target_field", "required_field", "allowed_field"))
    allowed_values = _get_arg(args, "allowed_values", "allowed_value", "required_values", "required_value")
    description = _get_arg(args, "description")

    if not source_field or not target_field:
        raise ValueError("source_field/entity_field e target_field/required_field sao obrigatorios.")
    if source_field == target_field:
        raise ValueError("source_field e target_field precisam ser diferentes.")
    if source_value is None or allowed_values is None:
        raise ValueError("source_value/entity_value e allowed_values/required_value sao obrigatorios.")

    source_values = _resolve_field_values(ambientid, source_field, source_value)
    target_values = _resolve_field_values(ambientid, target_field, allowed_values)
    conditions = [
        _condition_for_values(source_field, "match", source_values),
        _condition_for_values(target_field, "exclude", target_values),
    ]
    description = description or _default_required_description(source_field, source_values, target_field, target_values)
    return add_restriction_rule(ambientid, description, conditions, normalize=False)


def add_global_allowed_values_constraint(ambientid, args):
    field = _normalize_field(_get_arg(args, "field", "target_field", "allowed_field"))
    allowed_values = _get_arg(args, "allowed_values", "allowed_value", "values")
    description = _get_arg(args, "description")
    if not field or allowed_values is None:
        raise ValueError("field e allowed_values sao obrigatorios.")

    values = _resolve_field_values(ambientid, field, allowed_values)
    conditions = [_condition_for_values(field, "exclude", values)]
    description = description or f"Todas as aulas so podem ter {FIELD_LABELS[field]} em {_format_values(values)}"
    return add_restriction_rule(ambientid, description, conditions, normalize=False)


def add_forbidden_combination_constraint(ambientid, args):
    matches = _get_arg(args, "matches", "conditions", "forbidden")
    description = _get_arg(args, "description")
    if not isinstance(matches, list) or not matches:
        raise ValueError("matches precisa ser uma lista de campos/valores proibidos.")

    conditions = []
    for match in matches:
        if not isinstance(match, dict):
            raise ValueError("Cada item de matches precisa ser um objeto.")
        field = _normalize_field(match.get("field"))
        value = match.get("value", match.get("values"))
        if not field or value is None:
            raise ValueError("Cada match precisa ter field e value.")
        values = _resolve_field_values(ambientid, field, value)
        conditions.append(_condition_for_values(field, "match", values))

    description = description or "Proibido: " + " e ".join(
        f"{FIELD_LABELS[cond['field']]} {_format_values(cond['value'])}"
        for cond in conditions
    )
    return add_restriction_rule(ambientid, description, conditions, normalize=False)


def run_fixed_restriction_tool(ambientid, function_name, args):
    args = args or {}
    if function_name == "add_required_value_constraint":
        return add_required_value_constraint(ambientid, args)
    if function_name == "add_forbidden_combination_constraint":
        return add_forbidden_combination_constraint(ambientid, args)
    if function_name == "add_global_allowed_values_constraint":
        return add_global_allowed_values_constraint(ambientid, args)

    if function_name == "restrict_professor_days":
        return _wrapped_required(
            ambientid, "professor", _get_arg(args, "professor"),
            "dia", _get_arg(args, "allowed_days", "dias", "days"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_professor_subjects":
        return _wrapped_required(
            ambientid, "professor", _get_arg(args, "professor"),
            "disciplina", _get_arg(args, "allowed_subjects", "disciplinas", "subjects"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_professor_rooms":
        return _wrapped_required(
            ambientid, "professor", _get_arg(args, "professor"),
            "sala", _get_arg(args, "allowed_rooms", "salas", "rooms"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_professor_periods":
        return _wrapped_required(
            ambientid, "professor", _get_arg(args, "professor"),
            "periodo", _get_arg(args, "allowed_periods", "periodos", "periods"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_class_days":
        return _wrapped_required(
            ambientid, "turma", _get_arg(args, "turma", "class_name"),
            "dia", _get_arg(args, "allowed_days", "dias", "days"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_class_rooms":
        return _wrapped_required(
            ambientid, "turma", _get_arg(args, "turma", "class_name"),
            "sala", _get_arg(args, "allowed_rooms", "salas", "rooms"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_class_periods":
        return _wrapped_required(
            ambientid, "turma", _get_arg(args, "turma", "class_name"),
            "periodo", _get_arg(args, "allowed_periods", "periodos", "periods"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_subject_days":
        return _wrapped_required(
            ambientid, "disciplina", _get_arg(args, "disciplina", "subject"),
            "dia", _get_arg(args, "allowed_days", "dias", "days"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_subject_rooms":
        return _wrapped_required(
            ambientid, "disciplina", _get_arg(args, "disciplina", "subject"),
            "sala", _get_arg(args, "allowed_rooms", "salas", "rooms"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_subject_periods":
        return _wrapped_required(
            ambientid, "disciplina", _get_arg(args, "disciplina", "subject"),
            "periodo", _get_arg(args, "allowed_periods", "periodos", "periods"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_room_days":
        return _wrapped_required(
            ambientid, "sala", _get_arg(args, "sala", "room"),
            "dia", _get_arg(args, "allowed_days", "dias", "days"),
            _get_arg(args, "description"),
        )
    if function_name == "restrict_room_periods":
        return _wrapped_required(
            ambientid, "sala", _get_arg(args, "sala", "room"),
            "periodo", _get_arg(args, "allowed_periods", "periodos", "periods"),
            _get_arg(args, "description"),
        )
    if function_name == "require_subject_professor":
        return _wrapped_required(
            ambientid, "disciplina", _get_arg(args, "disciplina", "subject"),
            "professor", _get_arg(args, "professor"),
            _get_arg(args, "description"),
        )
    if function_name == "require_subject_room":
        return _wrapped_required(
            ambientid, "disciplina", _get_arg(args, "disciplina", "subject"),
            "sala", _get_arg(args, "sala", "room"),
            _get_arg(args, "description"),
        )
    if function_name == "require_class_room":
        return _wrapped_required(
            ambientid, "turma", _get_arg(args, "turma", "class_name"),
            "sala", _get_arg(args, "sala", "room"),
            _get_arg(args, "description"),
        )
    if function_name == "forbid_professor_subject":
        return _wrapped_forbidden(
            ambientid,
            [("professor", _get_arg(args, "professor")), ("disciplina", _get_arg(args, "disciplina", "subject"))],
            _get_arg(args, "description"),
        )
    if function_name == "forbid_professor_day":
        return _wrapped_forbidden(
            ambientid,
            [("professor", _get_arg(args, "professor")), ("dia", _get_arg(args, "dia", "day"))],
            _get_arg(args, "description"),
        )
    if function_name == "forbid_class_day":
        return _wrapped_forbidden(
            ambientid,
            [("turma", _get_arg(args, "turma", "class_name")), ("dia", _get_arg(args, "dia", "day"))],
            _get_arg(args, "description"),
        )
    if function_name == "forbid_subject_day":
        return _wrapped_forbidden(
            ambientid,
            [("disciplina", _get_arg(args, "disciplina", "subject")), ("dia", _get_arg(args, "dia", "day"))],
            _get_arg(args, "description"),
        )

    return None


def _wrapped_required(ambientid, source_field, source_value, target_field, allowed_values, description=None):
    return add_required_value_constraint(ambientid, {
        "source_field": source_field,
        "source_value": source_value,
        "target_field": target_field,
        "allowed_values": allowed_values,
        "description": description,
    })


def _wrapped_forbidden(ambientid, matches, description=None):
    return add_forbidden_combination_constraint(ambientid, {
        "matches": [
            {"field": field, "value": value}
            for field, value in matches
        ],
        "description": description,
    })


def _get_arg(args, *names):
    if not isinstance(args, dict):
        return None
    for name in names:
        if name in args and args[name] is not None:
            return args[name]
    return None


def _normalize_field(field):
    if field is None:
        return None
    aliases = {
        "prof": "professor",
        "teacher": "professor",
        "professora": "professor",
        "class": "turma",
        "classe": "turma",
        "tclass": "turma",
        "subject": "disciplina",
        "materia": "disciplina",
        "matéria": "disciplina",
        "room": "sala",
        "classroom": "sala",
        "day": "dia",
        "period": "periodo",
        "periodo": "periodo",
        "horario": "periodo",
        "horário": "periodo",
    }
    normalized = _normalize(field)
    normalized = aliases.get(normalized, normalized)
    if normalized not in ALLOWED_FIELDS:
        return None
    return normalized


def _resolve_field_values(ambientid, field, values):
    raw_values = values if isinstance(values, list) else [values]
    resolved = []
    for value in raw_values:
        resolved.append(_resolve_field_value(ambientid, field, value))
    if not resolved:
        raise ValueError(f"Nenhum valor informado para {field}.")
    return resolved


def _resolve_field_value(ambientid, field, value):
    if value is None:
        raise ValueError(f"Valor ausente para {field}.")
    if field == "professor":
        resolved = _resolve_professor_name_for_rule(
            ambientid,
            str(value),
            [{"field": "professor", "operator": "==", "value": value}],
        )
        if resolved:
            return resolved
        raise ValueError(f"Professor nao encontrado: {value}")
    if field == "disciplina":
        resolved = _resolve_subject_name_from_value(_subject_names_for_ambient(ambientid), value)
        if resolved:
            return resolved
        raise ValueError(f"Disciplina nao encontrada: {value}")
    if field in ["turma", "sala"]:
        resolved = _resolve_named_field_value(ambientid, field, value)
        if resolved:
            return resolved
        raise ValueError(f"{FIELD_LABELS[field].title()} nao encontrada: {value}")
    if field == "dia":
        day_index = _day_index(value)
        if day_index is not None:
            return _day_name(day_index)
        raise ValueError(f"Dia invalido: {value}")
    if field == "periodo":
        period_index = _period_index(value)
        if period_index is not None:
            return period_index
        raise ValueError(f"Periodo invalido: {value}")
    return value


def _resolve_named_field_value(ambientid, field, value):
    import difflib
    import re

    names = _names_for_field(ambientid, field)
    if not names:
        return None
    normalized = _normalize(value)
    normalized_map = {_normalize(name): name for name in names}
    if normalized in normalized_map:
        return normalized_map[normalized]

    if field == "sala":
        lab_match = re.search(r"\blab(?:oratorio)?\s*(\d+)\b", normalized or "")
        if lab_match:
            number = lab_match.group(1)
            for name in names:
                name_normalized = _normalize(name) or ""
                if "laboratorio" in name_normalized and number in name_normalized:
                    return name

    close = difflib.get_close_matches(normalized, normalized_map.keys(), n=1, cutoff=0.72)
    if close:
        return normalized_map[close[0]]
    return None


def _names_for_field(ambientid, field):
    try:
        from AllokAcads.models import Ambient

        ambient = Ambient.objects.get(ambientid=ambientid)
    except Exception:
        return []
    if field == "turma":
        return [aclass.name for aclass in ambient.classes.all() if aclass.name]
    if field == "sala":
        return [room.name for room in ambient.classrooms.all() if room.name]
    return []


def _condition_for_values(field, mode, values):
    values = values if isinstance(values, list) else [values]
    if mode == "match":
        return {
            "field": field,
            "operator": "==" if len(values) == 1 else "in",
            "value": values[0] if len(values) == 1 else values,
        }
    if mode == "exclude":
        return {
            "field": field,
            "operator": "!=" if len(values) == 1 else "not in",
            "value": values[0] if len(values) == 1 else values,
        }
    raise ValueError(f"Modo de condicao invalido: {mode}")


def _default_required_description(source_field, source_values, target_field, target_values):
    source_text = _format_values(source_values)
    target_text = _format_values(target_values)
    if source_field == "professor" and target_field == "dia":
        return f"{source_text} so pode dar aula em {target_text}"
    if source_field == "professor" and target_field == "disciplina":
        return f"{source_text} so pode dar {target_text}"
    if source_field == "professor" and target_field == "sala":
        return f"{source_text} so pode dar aula em {target_text}"
    if source_field == "professor" and target_field == "periodo":
        return f"{source_text} so pode dar aula no periodo {target_text}"
    if source_field == "disciplina" and target_field == "professor":
        return f"{source_text} deve ser com {target_text}"
    if source_field == "disciplina" and target_field == "sala":
        return f"{source_text} deve usar {target_text}"
    if source_field == "turma" and target_field == "sala":
        return f"{source_text} so pode usar {target_text}"
    return (
        f"{FIELD_LABELS[source_field].title()} {source_text} exige "
        f"{FIELD_LABELS[target_field]} em {target_text}"
    )


def _format_values(values):
    values = values if isinstance(values, list) else [values]
    formatted = []
    for value in values:
        if isinstance(value, int):
            formatted.append(str(value + 1))
        else:
            formatted.append(str(value))
    if len(formatted) <= 1:
        return formatted[0] if formatted else ""
    return ", ".join(formatted[:-1]) + " ou " + formatted[-1]


def _normalize_known_rule(ambientid, description, conditions):
    raw_description = description or ""
    text = _normalize(raw_description) or ""
    professor_name = _resolve_professor_name_for_rule(ambientid, raw_description, conditions)
    subject_name = _resolve_subject_name_for_rule(ambientid, raw_description, conditions)
    means_only_allowed = any(term in text for term in ["so pode", "somente", "apenas"])
    means_mandatory = any(term in text for term in ["tem que", "deve", "obrig"])
    is_negative = any(term in text for term in ["nao pode", "não pode", "proibir", "proiba"])
    has_day_condition = any(
        isinstance(cond, dict) and str(cond.get("field", "")).strip().lower() == "dia"
        for cond in (conditions if isinstance(conditions, list) else [])
    )

    if professor_name and subject_name and not is_negative and not has_day_condition:
        if means_only_allowed:
            return raw_description, [
                {"field": "professor", "operator": "==", "value": professor_name},
                {"field": "disciplina", "operator": "!=", "value": subject_name},
            ]
        if means_mandatory or _has_equal_professor_subject_pair(conditions):
            return raw_description, [
                {"field": "disciplina", "operator": "==", "value": subject_name},
                {"field": "professor", "operator": "!=", "value": professor_name},
            ]

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


def _has_equal_professor_subject_pair(conditions):
    if not isinstance(conditions, list):
        return False
    has_professor_equal = False
    has_subject_equal = False
    for cond in conditions:
        if not isinstance(cond, dict):
            continue
        field = str(cond.get("field", "")).strip().lower()
        operator = str(cond.get("operator", "")).strip().lower()
        if field == "professor" and operator == "==":
            has_professor_equal = True
        if field == "disciplina" and operator == "==":
            has_subject_equal = True
    return has_professor_equal and has_subject_equal


def _resolve_professor_name_for_rule(ambientid, description, conditions):
    import difflib

    professors = _professor_names_for_ambient(ambientid)
    if not professors:
        return None

    candidates = []
    if isinstance(conditions, list):
        for cond in conditions:
            if isinstance(cond, dict) and str(cond.get("field", "")).strip().lower() == "professor":
                value = cond.get("value")
                if isinstance(value, str):
                    candidates.append(value)
    candidates.extend(_extract_words(description))

    normalized_map = {_normalize(name): name for name in professors}
    token_map = {}
    for name in professors:
        for token in (_normalize(name) or "").split():
            token_map.setdefault(token, set()).add(name)

    for candidate in candidates:
        normalized = _normalize(candidate)
        if not normalized:
            continue
        if normalized in normalized_map:
            return normalized_map[normalized]
        token_matches = [name for name in professors if normalized in (_normalize(name) or "").split()]
        if len(token_matches) == 1:
            return token_matches[0]
        token_cutoff = 0.65 if len(normalized) >= 5 else 0.78
        close_tokens = difflib.get_close_matches(normalized, token_map.keys(), n=2, cutoff=token_cutoff)
        if len(close_tokens) == 1:
            token_candidates = token_map[close_tokens[0]]
            if len(token_candidates) == 1:
                return next(iter(token_candidates))

    text = _normalize(description) or ""
    for normalized_name, name in normalized_map.items():
        if normalized_name and normalized_name in text:
            return name
    return None


def _resolve_subject_name_for_rule(ambientid, description, conditions):
    subjects = _subject_names_for_ambient(ambientid)
    if not subjects:
        return None

    if isinstance(conditions, list):
        for cond in conditions:
            if isinstance(cond, dict) and str(cond.get("field", "")).strip().lower() == "disciplina":
                resolved = _resolve_subject_name_from_value(subjects, cond.get("value"))
                if resolved:
                    return resolved

    text = _normalize(description) or ""
    for subject in subjects:
        subject_normalized = _normalize(subject)
        if subject_normalized and subject_normalized in text:
            return subject

    return _resolve_subject_name_from_value(subjects, description)


def _resolve_subject_name_from_value(subjects, value):
    import re

    raw_value = str(value or "")
    normalized = _normalize(value)
    if not normalized:
        return None

    normalized_map = {_normalize(subject): subject for subject in subjects}
    if normalized in normalized_map:
        return normalized_map[normalized]

    subject_aliases = [
        ("Sistemas Operacionais", [r"(?<!\w)S\.?O\.?(?!\w)"]),
        ("Banco de Dados", [r"(?<!\w)B\.?D\.?(?!\w)"]),
        ("Interação Humano/Computador", [r"(?<!\w)I\.?H\.?C\.?(?!\w)"]),
        ("Programação Orientada a Objetos", [r"(?<!\w)P\.?O\.?O\.?(?!\w)"]),
    ]
    for subject, patterns in subject_aliases:
        subject_normalized = _normalize(subject)
        if subject_normalized not in normalized_map:
            continue
        if any(re.search(pattern, raw_value) for pattern in patterns):
            return normalized_map[subject_normalized]
    if "banco" in normalized and _normalize("Banco de Dados") in normalized_map:
        return normalized_map[_normalize("Banco de Dados")]
    if "web" in normalized and _normalize("Desenvolvimento WEB") in normalized_map:
        return normalized_map[_normalize("Desenvolvimento WEB")]
    return None


def _professor_names_for_ambient(ambientid):
    try:
        from AllokAcads.models import Ambient

        ambient = Ambient.objects.get(ambientid=ambientid)
    except Exception:
        return []
    return [
        member.user.name
        for member in ambient.members.filter(is_professor=True)
        if member.user and member.user.name
    ]


def _subject_names_for_ambient(ambientid):
    try:
        from AllokAcads.models import Ambient

        ambient = Ambient.objects.get(ambientid=ambientid)
    except Exception:
        return []
    return [subject.name for subject in ambient.subjects.all() if subject.name]


def _extract_words(text):
    import re

    return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'.-]*", text or "")


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
            "conditions": rule.get("conditions", []),
            "violacoes": [],
        }
        for idx, rule in enumerate(rules)
    ]
    resource_conflicts = []
    professor_day_usage = {}

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
            professor_name = entry["atividade"].get("professor")
            if professor_name:
                usage_key = (professor_name, _day_name(slot.column))
                professor_day_usage[usage_key] = professor_day_usage.get(usage_key, 0) + 1

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
    activity_by_id = {activity.id: activity for activity in ambient.activities.all()}
    pending_unique = list(pending_by_id.values())
    for pending in pending_unique:
        activity = pending.get("atividade") or {}
        activity_obj = activity_by_id.get(activity.get("id"))
        if activity_obj:
            pending["diagnostico"] = _diagnose_unallocated_activity(ambient, tt, activity_obj, rules)

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
        "uso_professor_dia": [
            {
                "professor": professor,
                "dia": day,
                "periodos_usados": periods,
                "periodos_disponiveis_no_dia": ambient.periods_in_a_day,
            }
            for (professor, day), periods in sorted(professor_day_usage.items())
        ],
        "observacoes": complexity_notes,
    }
    return "Analise deterministica da grade:\n" + json.dumps(report, ensure_ascii=False, indent=2)


def _diagnose_unallocated_activity(ambient, timetable_db, activity, rules):
    duration = activity.activities_qtd or 1
    periods = ambient.periods_in_a_day or 0
    days = ambient.days_in_a_cicle or 0
    windows = []
    viable_count = 0

    for col in range(days):
        for row in range(max(0, periods - duration + 1)):
            keys = [(row + offset, col) for offset in range(duration)]
            window = {
                "dia": _day_name(col),
                "periodo_inicio": row,
                "periodo_fim": row + duration - 1,
                "bloqueios": [],
            }

            for line, slot_col in keys:
                attrs = _activity_attributes(activity)
                attrs["dia"] = slot_col
                attrs["periodo"] = line
                for rule in rules:
                    if _rule_matches(rule, attrs):
                        window["bloqueios"].append({
                            "tipo": "restricao",
                            "periodo": line,
                            "restricao": rule.get("description"),
                        })

                try:
                    slot = timetable_db.table.get(line=line, column=slot_col)
                    slot_activities = list(slot.activitie.all())
                except Exception:
                    slot_activities = []

                for other in slot_activities:
                    if getattr(other, "id", None) == getattr(activity, "id", None):
                        continue
                    conflict_types = _activity_conflict_types(activity, other)
                    if conflict_types:
                        window["bloqueios"].append({
                            "tipo": "conflito_recurso",
                            "periodo": line,
                            "recursos": conflict_types,
                            "atividade": _activity_data(other),
                        })

            if window["bloqueios"]:
                windows.append(window)
            else:
                viable_count += 1

    relevant_windows = []
    for window in windows:
        has_only_restriction = any(block.get("tipo") == "restricao" for block in window["bloqueios"])
        has_resource_conflict = any(block.get("tipo") == "conflito_recurso" for block in window["bloqueios"])
        if has_resource_conflict or not has_only_restriction:
            relevant_windows.append(window)

    if not relevant_windows:
        relevant_windows = windows

    return {
        "janelas_viaveis_sem_bloqueio": viable_count,
        "janelas_analisadas": days * max(0, periods - duration + 1),
        "principais_bloqueios": relevant_windows[:3],
    }


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
        if function_name in FIXED_RESTRICTION_TOOLS:
            output = run_fixed_restriction_tool(ambientid, function_name, args)
            if output is not None:
                return output
        if function_name == "add_restriction_rule":
            return add_restriction_rule(
                ambientid,
                args.get("description"),
                args.get("conditions"),
            )
        if function_name == "add_custom_restriction_rule":
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
        "### ARQUITETURA DAS RESTRICOES:\n"
        "Voce deve ser um roteador de intencao, nao o autor manual de operadores. Use as tools fixas sempre que possivel; o backend monta os operadores corretos.\n"
        "- Para 'X so pode Y', use add_required_value_constraint ou um wrapper restrict_*.\n"
        "- Para 'X deve ser com/em Y', use add_required_value_constraint ou um wrapper require_*.\n"
        "- Para 'X nao pode Y', use add_forbidden_combination_constraint ou um wrapper forbid_*.\n"
        "- Use add_custom_restriction_rule somente como ultima opcao, quando nenhuma tool fixa representar a regra.\n"
        "Campos suportados pelas tools genericas: professor, turma, disciplina, sala, dia, periodo. Isso cobre todas as restricoes triviais entre dois campos e combinacoes proibidas simples.\n\n"
        "### DIRETRIZ CRITICA DE REGRAS (ESTADOS PROIBIDOS):\n"
        "Uma regra representa um ESTADO PROIBIDO. Se todas as condicoes de uma regra forem verdadeiras em uma aula, ela recebe penalidade maxima no RKO e sera evitada a todo custo.\n"
        "As tools fixas ja fazem a inversao. Nao tente montar operators manualmente quando houver tool fixa.\n"
        "- Exemplo: 'Wesley so pode terca ou quinta' => restrict_professor_days.\n"
        "- Exemplo: 'Wesley so pode dar SO' => restrict_professor_subjects.\n"
        "- Exemplo: 'SO deve ser com Wesley' => require_subject_professor.\n"
        "- Exemplo: 'Wesley nao pode BD' => forbid_professor_subject.\n\n"
        + "### FORA DO ESCOPO ATUAL:\n"
        + "Nao finja que aplicou restricoes agregadas ou qualitativas. Ainda estao fora do formato dinamico atual: maximo/minimo de aulas por turma ou professor por dia, limite de aulas consecutivas, janelas/gaps, balanceamento global da semana, relacoes entre duas disciplinas no mesmo dia e preferencias como 'aulas mais dificeis no comeco'. Nesses casos, explique que ainda precisa de uma regra nova no decoder/analisador e nao rode a otimizacao.\n\n"
        "### INSTRUCOES DE FERRAMENTAS:\n"
        "- Para ver as restricoes ativas: use 'list_constraints'.\n"
        "- Para remover uma restricao: use 'remove_restriction_rule' informando o indice obtido em 'list_constraints'.\n"
        "- Para apagar tudo: use 'clear_all_constraints'.\n"
        "- Se o usuario disser 'limpe/remova/apague as restricoes ativas' ou 'tire todas as restricoes', use 'clear_all_constraints' diretamente. Nao liste as restricoes nesse caso.\n"
        "- Se o usuario disser 'remova a restricao 2', trate como a segunda regra exibida ao usuario e use index 1. Se ele disser explicitamente 'indice 0', use index 0.\n"
        "- Antes de adicionar uma regra, confira se o usuario informou a entidade exata. Se ele disser apenas 'o professor', 'a materia', 'a turma' ou 'a sala', use 'respond_to_user' perguntando qual e o nome exato; nao invente valores e nao aplique restricao.\n"
        "- Se houver nome de professor + 'aula' + dia, isso e disponibilidade do professor. Use 'restrict_professor_days' e nao pergunte disciplina. Ex: 'Wesley so de aula terca' => restrict_professor_days.\n"
        "- A palavra 'aula' nao e uma disciplina. So pergunte disciplina quando o usuario falar de 'materia' ou 'disciplina' sem dizer qual.\n"
        "- Se o nome informado nao aparecer claramente no CONTEXTO REAL DO AMBIENTE, use 'respond_to_user' pedindo confirmacao antes de executar.\n"
        "- Para ver a grade horaria/timetable gerada: use 'get_current_timetable'.\n"
        "- Para verificar se a solucao respeitou as restricoes e explicar problemas: use 'analyze_solution'.\n"
        "- Para rodar a otimizacao completa pela IA: use 'run_unified_solver'. Essa ferramenta escolhe professor, sala e horario em uma unica solucao.\n"
        "Dica: Se o usuario pedir para 'gerar a grade' ou 'otimizar', voce deve adicionar as restricoes solicitadas (se houver), rodar 'run_unified_solver' e depois chamar 'analyze_solution' para verificar se a solucao ficou boa antes de explicar.\n\n"
        f"CONTEXTO REAL DO AMBIENTE:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
    )


def apply_attribution_constraints(cost, activities, ambientid, professor_limits=None):
    rules = [
        rule for rule in load_rules(ambientid)
        if all(cond.get("field") in ATTRIBUTION_FIELDS for cond in rule.get("conditions", []))
    ]
    for activity in activities:
        attrs = _activity_attributes(activity)
        for rule in rules:
            if _rule_matches(rule, attrs):
                cost += PENALTY

    if professor_limits is None:
        return cost
    return _apply_professor_day_capacity_constraints(cost, activities, professor_limits)


def _apply_professor_day_capacity_constraints(cost, activities, professor_limits):
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
    if field == "periodo" and isinstance(value, int):
        return {
            _normalize(value),
            _normalize(value + 1),
            _normalize(f"Periodo {value + 1}"),
            _normalize(f"{value + 1}o"),
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
        if field == "periodo":
            period_index = _period_index(item)
            if period_index is not None:
                values.add(_normalize(period_index))
                values.add(_normalize(period_index + 1))
                values.add(_normalize(f"Periodo {period_index + 1}"))
                values.add(_normalize(f"{period_index + 1}o"))
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


def _period_index(value):
    import re

    if isinstance(value, int):
        return value if value == 0 else max(0, value - 1)
    text = _normalize(value)
    if text is None:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    return max(0, int(match.group(0)) - 1)
