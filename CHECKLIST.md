# Checklist — antes de entregar

Ordem importa: o que zera a prova vem antes do que tira pontos, e o que tira
pontos vem antes do que é estético.

---

## 0. Antes de começar (fora da janela, enquanto o relógio não corre)

- [ ] `pip install pytest` — a suíte local depende dele
- [ ] `docker pull python:3.12-slim` — não gastar a janela baixando ~180MB
- [ ] `ss -ltnp | grep :8080` — descubra se a 8080 já está ocupada na sua
      máquina. Se estiver, use `PORT=8111` nos testes locais (dentro do
      container continua 8080)
- [ ] Nome e RA preenchidos no arquivo de identidade (RA com 5+ dígitos, sem
      placeholder tipo `PREENCHER`)

---

## 1. O container sobe de verdade

O teste local passando **não** prova isso. Quatro falhas clássicas passam no
loop local e quebram no corretor.

```bash
docker build -t prova .
docker run --rm -p 8080:8080 prova    # sem -d: você vê o log e se o processo morre
curl localhost:8080/healthz           # de FORA do container
```

- [ ] `docker build` termina sem erro
- [ ] o processo **não** morre no boot (`docker ps` mostra o container)
- [ ] `curl` de fora responde → prova que o bind é `0.0.0.0`, não `127.0.0.1`
- [ ] `COPY` cobre **todas** as pastas que o app lê (`src/`, `public/`,
      `variante/`). Esquecer `public/` dá 404 só no container
- [ ] caminhos de arquivo no código são relativos ao **arquivo**
      (`os.path.dirname(__file__)`), não ao CWD

> Se `/healthz` não responder, a suíte não emite resumo de pytest e o critério
> de testes vai a **zero** — não a "alguns testes falharam". É o único item
> desta lista que derruba tudo de uma vez.

---

## 2. Semântica da resposta (o que passa no olho e falha no assert)

- [ ] **boolean sai `true`/`false`, não `0`/`1`** — SQLite não tem boolean, e em
      Python `1 == True` é verdadeiro, então um `assert x == True` não pega.
      Converta com `bool()` na serialização
- [ ] **`204` sem corpo** — zero bytes (Flask/Werkzeug já descarta o corpo
      sozinho; implementação em `http.server` puro não)
- [ ] **status codes exatos do contrato** — `404` para id inexistente, `400`
      para payload inválido, `409` para conflito/duplicidade. Não deixe o
      framework escolher: FastAPI/Pydantic devolve `422` por padrão
- [ ] **nomes de campo e de erro byte a byte** iguais ao contrato
- [ ] **atualização parcial preserva campos ausentes** — use
      `if "campo" in body`, não `body.get("campo")`, senão enviar um campo
      apaga os outros
- [ ] **campos derivados recalculados** no update (preço com desconto, total,
      etc.), não gravados uma vez na criação
- [ ] **`>` vs `>=`** em qualquer regra de limiar — releia a frase do contrato
- [ ] `Content-Type` conforme o contrato (`application/json`, `text/plain`,
      `text/html`)
- [ ] IDs sequenciais começando em 1, lista ordenada por id

---

## 3. Critérios mecânicos (pontos baratos, verificados por regex)

Estes não dependem de teste nenhum — são pontos que você perde em silêncio.

- [ ] `Dockerfile` contém **`EXPOSE 8080`** literal. Não afeta o `-p` em nada,
      o container funciona perfeitamente sem ele, e costuma valer a maior parte
      da nota de Dockerfile
- [ ] `Dockerfile` contém `CMD` ou `ENTRYPOINT`
- [ ] `README` menciona subida **local** E **container** (as duas, não uma)
- [ ] o arquivo da solução está no caminho exato que o enunciado pede
      (ex.: `src/app.py` — não `app.py`, não `src/main.py`)
- [ ] o stub foi apagado: sem a string `TODO` no arquivo da solução
- [ ] se houver frontend, os `id`/`name` exigidos existem no HTML

```bash
grep -n "EXPOSE 8080" Dockerfile
grep -rn "TODO" src/
```

---

## 4. Rastreabilidade

- [ ] cada site/IA consultado está declarado como **linha numerada de tabela**:
      `| 1 | URL | o que usou | onde aparece |`. Link em texto corrido ou em
      exemplo normalmente **não conta**
- [ ] conversas com IA estão **compartilhadas publicamente** e o link está na
      tabela
- [ ] se não consultou nada, está declarado explicitamente
      (ex.: "Nenhum site consultado.")
- [ ] você sabe explicar **qualquer** trecho do que entregou. Se não sabe,
      troque por algo que você sabe, mesmo que mais feio

---

## 5. Nunca toque (zeramento automático)

- [ ] não alterou as pastas do esqueleto (`scripts/`, `.github/`, `docs/`)
- [ ] não alterou contrato, rubrica ou lockfile depois da aplicação
- [ ] mais de um commit, todos dentro da janela — commit único em lote é
      sinalizado como suspeita

```bash
git status --short            # nada de estranho modificado
git log --oneline             # commits pequenos, dentro da janela
```

---

## 6. Sequência final

1. [ ] rodar a suíte **pelo caminho do corretor** (o script de testes do repo,
       que faz build + run + espera healthz + pytest) — não só pelo loop local
2. [ ] `git push` antes do fim da janela
3. [ ] disparar a auto-correção ao menos **uma vez** (costuma ser obrigatório;
       fechar sem isso pode reabrir a entrega)
4. [ ] conferir a nota parcial e corrigir o que der tempo
5. [ ] fechar a issue/entrega para gerar o artefato final

> Vermelho no job de testes não é quebra do sistema — é o feedback normal. A
> nota sai junto com o que falhou. Corrija e rode de novo.
