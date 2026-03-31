import csv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

# Configurações estáticas e de template
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

ARQUIVO_ALUNOS = "alunos.csv"

class Aluno(BaseModel):
    nome: str


# ==========================================
# SERVIÇOS (Lógica de Dados / Regras de Negócio)
# ==========================================

def obter_todos_alunos() -> dict:
    """Lê o CSV e retorna um dicionário de alunos."""
    alunos = {}
    try:
        with open(ARQUIVO_ALUNOS, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0] == "NUMERO":
                    continue
                alunos[row[0]] = row[1]
    except FileNotFoundError:
        # Se o arquivo não existir, apenas retorna o dicionário vazio
        pass
    
    return alunos


def salvar_novo_aluno(nome_aluno: str) -> None:
    """Calcula o próximo ID e salva o novo aluno no arquivo CSV."""
    data = [["NUMERO", "NOME"]]
    maior_numero = 0

    # 1. Lê os dados existentes e encontra o maior ID
    try:
        with open(ARQUIVO_ALUNOS, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0] == "NUMERO":
                    continue
                data.append(row)
                maior_numero = max(maior_numero, int(row[0])) 
    except FileNotFoundError:
        pass

    # 2. Adiciona o novo registro
    novo_numero = maior_numero + 1
    data.append([novo_numero, nome_aluno])

    # 3. Sobrescreve o arquivo com os dados atualizados
    with open(ARQUIVO_ALUNOS, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)


# ==========================================
# CONTROLADORES (Rotas / Endpoints)
# ==========================================

@app.get("/home")
async def home(request: Request):
    alunos = obter_todos_alunos()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"lista_alunos": alunos},
    )


@app.get("/adicionar")
async def pagina_adicionar(request: Request):
    """Renderiza a página com o formulário web para adicionar aluno."""
    return templates.TemplateResponse(
        request=request,
        name="add.html"
    )


@app.post("/add")
async def add_cliente_api(request: Request, aluno: Aluno):
    """Endpoint via API (Postman/JSON) que adiciona aluno e devolve a lista HTML."""
    salvar_novo_aluno(aluno.nome)
    
    alunos_atualizados = obter_todos_alunos()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"lista_alunos": alunos_atualizados},
    )


@app.post("/add_web")
async def add_cliente_web(request: Request):
    """Endpoint que recebe dados do formulário HTML e redireciona."""
    form = await request.form()
    nome_aluno = form.get("nome")
    
    if nome_aluno:
        salvar_novo_aluno(nome_aluno)

    return RedirectResponse(url="/home", status_code=303)