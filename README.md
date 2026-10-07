# CRUD Flask + SQLite + Docker — template de prova prática

Modelo de referência para provas práticas em que a correção é automatizada e
roda o código do aluno em container.

## A restrição que define a arquitetura

O corretor executa, a partir da raiz do repositório:

```bash
docker build -t prova .
docker run -p <PORTA>:8080 prova
# aguarda GET /healthz responder 200, depois roda a suíte de testes
```

Um container, uma porta. Isso elimina `docker-compose`, banco em serviço
separado e dev server de frontend. O que sobra:

| Camada | Escolha | Por quê |
| --- | --- | --- |
| Backend | Flask | o contrato exige status codes exatos; FastAPI/Pydantic devolve 422 por padrão |
| Banco | `sqlite3` (stdlib) | em processo, zero dependência nativa, zero serviço externo |
| Frontend | HTML + `fetch` estático | servido pelo próprio backend na mesma porta, sem build step |
| Imagem | `python:3.12-slim` | ~198MB, build em ~13s |

## Conteúdo

| Arquivo | Papel |
| --- | --- |
| `Dockerfile` | imagem da entrega — `EXPOSE 8080` + `CMD` |
| `requirements.txt` | uma linha |
| `src/app.py` | CRUD completo de referência (API de Tarefas) |
| `prompts/01-contexto.txt` | contexto para colar uma vez na LLM de consulta |
| `prompts/02-pedidos.txt` | pedidos por etapa |
| `CHECKLIST.md` | verificações antes de entregar |

## Rodar local

```bash
pip install -r requirements.txt
PORT=8111 python3 src/app.py        # PORT só para local; no container é 8080
curl localhost:8111/healthz
```

> Use `PORT` se a 8080 já estiver ocupada na sua máquina — dentro do container
> continua 8080, que é o que o contrato exige.

Repo limpo e o remote já está configurado. Os dois comandos:

Loop rápido — a cada edição (~0,1s, sem Docker)
```bash
# terminal 1
PORT=8111 python3 src/app.py

# terminal 2
BASE_URL=http://localhost:8111 REPO_SLUG=prova-escolati-2026 \
  python3 -m pytest tests/public -q
Loop real — a cada commit (é o que o professor roda)
bash scripts/rodar_testes.sh
```

## Rodar em container

```bash
docker build -t prova .
docker run --rm -p 8080:8080 prova   # sem -d: você vê o log e se o processo morre
curl localhost:8080/healthz          # de fora do container, prova o bind 0.0.0.0
```

## Consulta a IA

Os prompts em `prompts/` servem para consulta a LLM onde isso é permitido.
Regras típicas exigem que a conversa seja **pública** e que o link seja
declarado no `FONTES.md` como linha numerada de tabela. Veja o `CHECKLIST.md`.
