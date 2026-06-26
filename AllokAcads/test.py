import requests

# Funções de exemplo
def somar(a, b):
    return float(a) + float(b)

def subtrair(a, b):
    return float(a) - float(b)

funcoes = {
    "somar": somar,
    "subtrair": subtrair,
}

user_input = input("Digite seu comando: ")

prompt = f"""
Você é um assistente Python. Analise o comando do usuário e responda em JSON com o nome da função e os argumentos.
Exemplo de resposta: {{"function": "somar", "args": [1, 2]}}
Comando: {user_input}
"""

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
    },
    json={
        "model": "openrouter/owl-alpha",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
)

result = response.json()
try:
    resposta_llm = result["choices"][0]["message"]["content"]
    import json
    dados = json.loads(resposta_llm)
    func = funcoes.get(dados["function"])
    if func:
        output = func(*dados["args"])
        print("Resultado:", output)
    else:
        print("Função não encontrada:", dados["function"])
except Exception as e:
    print("Erro ao processar resposta da LLM:", e)



    def formation_preference_adjustment(request, activitie, tformation, weight):
    pass
def class_preference_adjustment(request, activitie, tclass, weight):
    pass
def subject_adjustment(request, solicitation):
    pass
def professor_adjustment(request, solicitation):
    pass
def classroom_adjustment(request, solicitation):
    pass
def schedule_adjustment(request, solicitation):
    pass
def formation_adjustment(request, solicitation):
    pass
def class_adjustment(request, solicitation):
    pass
def subject_CRUD(request, solicitation):
    pass
def professor_CRUD(request, solicitation):
    pass
def classroom_CRUD(request, solicitation):
    pass
def schedule_CRUD(request, solicitation):
    pass
def formation_CRUD(request, solicitation):
    pass
def class_CRUD(request, solicitation):
    pass
def position_adjustment(request, solicitation):
    pass
def columns_lines_number_adjustment(request, solicitation):
    pass
def admin_permissions_adjustment(request, solicitation):
    pass
def min_max_activities_adjustment(request, solicitation):