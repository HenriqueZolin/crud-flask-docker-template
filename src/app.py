"""API de Tarefas — Flask + sqlite3 (stdlib). Escuta em 0.0.0.0:8080.

Referência de CRUD completo para prova prática corrigida em container.
Troque os nomes de campo e os códigos de erro pelos do SEU contrato.
"""
import os
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)
db = sqlite3.connect(":memory:", check_same_thread=False)
db.row_factory = sqlite3.Row
db.execute("""CREATE TABLE tarefas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo    TEXT    NOT NULL,
    descricao TEXT    NOT NULL DEFAULT '',
    concluida INTEGER NOT NULL DEFAULT 0)""")


def saida(r):
    """SQLite guarda boolean como 0/1 — o contrato pede true/false."""
    return {"id": r["id"], "titulo": r["titulo"],
            "descricao": r["descricao"], "concluida": bool(r["concluida"])}


def busca(tid):
    return db.execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.post("/tasks")
def criar():
    body = request.get_json(silent=True) or {}
    titulo = body.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        return jsonify(erro="titulo_invalido"), 400
    cur = db.execute("INSERT INTO tarefas (titulo, descricao) VALUES (?, ?)",
                     (titulo.strip(), body.get("descricao") or ""))
    db.commit()
    return jsonify(saida(busca(cur.lastrowid))), 201


@app.get("/tasks")
def listar():
    return jsonify([saida(r) for r in db.execute("SELECT * FROM tarefas ORDER BY id")])


@app.get("/tasks/<int:tid>")
def obter(tid):
    r = busca(tid)
    return (jsonify(saida(r)), 200) if r else (jsonify(erro="nao_encontrado"), 404)


@app.put("/tasks/<int:tid>")
def atualizar(tid):
    if not busca(tid):
        return jsonify(erro="nao_encontrado"), 404
    body = request.get_json(silent=True) or {}
    campos, valores = [], []
    if "titulo" in body:
        if not isinstance(body["titulo"], str) or not body["titulo"].strip():
            return jsonify(erro="titulo_invalido"), 400
        campos.append("titulo = ?")
        valores.append(body["titulo"].strip())
    if "descricao" in body:
        campos.append("descricao = ?")
        valores.append(body["descricao"] or "")
    if "concluida" in body:
        if not isinstance(body["concluida"], bool):
            return jsonify(erro="concluida_invalida"), 400
        campos.append("concluida = ?")
        valores.append(int(body["concluida"]))
    if campos:  # campos ausentes preservam o valor atual
        db.execute("UPDATE tarefas SET %s WHERE id = ?" % ", ".join(campos),
                   valores + [tid])
        db.commit()
    return jsonify(saida(busca(tid))), 200


@app.delete("/tasks/<int:tid>")
def remover(tid):
    if not busca(tid):
        return jsonify(erro="nao_encontrado"), 404
    db.execute("DELETE FROM tarefas WHERE id = ?", (tid,))
    db.commit()
    return "", 204


if __name__ == "__main__":
    # 0.0.0.0 e obrigatorio: em 127.0.0.1 o container nao responde de fora.
    app.run("0.0.0.0", int(os.environ.get("PORT", 8080)))
