from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"

# Caminho do banco de dados (tentativa de usar volume do Railway)
DATABASE = "/app/documentos.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tipo TEXT,
                  nivel TEXT,
                  nome TEXT,
                  url TEXT UNIQUE,
                  data_cadastro TEXT,
                  cidade TEXT,
                  estado TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_documento():
    if request.method == 'POST':
        tipo_doc = request.form['tipo_doc']
        nivel = request.form['nivel'].capitalize()
        nome = request.form['nome']
        url = request.form['url'].strip()

        if nivel not in ["Municipal", "Estadual", "Federal"]:
            flash("Nível inválido! Use Municipal, Estadual ou Federal.", "error")
            return redirect(url_for('adicionar_documento'))

        novo_documento = {
            "tipo": tipo_doc,
            "nivel": nivel,
            "nome": nome,
            "url": url,
            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cidade": request.form.get('cidade', None),
            "estado": request.form.get('estado', None)
        }

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO documentos (tipo, nivel, nome, url, data_cadastro, cidade, estado)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (novo_documento["tipo"], novo_documento["nivel"], novo_documento["nome"],
                       novo_documento["url"], novo_documento["data_cadastro"],
                       novo_documento["cidade"], novo_documento["estado"]))
            conn.commit()
            flash("Link adicionado com sucesso!", "success")
        except sqlite3.IntegrityError:
            flash("Erro: Esta URL já foi cadastrada!", "error")
            conn.close()
            return redirect(url_for('adicionar_documento'))
        finally:
            conn.close()

        return redirect(url_for('listar_documentos'))
    return render_template('adicionar.html')

@app.route('/listar')
def listar_documentos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM documentos")
    documentos = c.fetchall()
    conn.close()
    return render_template('listar.html', documentos=documentos)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar_documento():
    if request.method == 'POST':
        busca = request.form['busca'].lower()
        finalidade = request.form['finalidade']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM documentos WHERE tipo LIKE ? OR nome LIKE ? OR cidade LIKE ? OR estado LIKE ?",
                  (f"%{busca}%", f"%{busca}%", f"%{busca}%", f"%{busca}%"))
        encontrados = c.fetchall()
        conn.close()
        return render_template('buscar.html', encontrados=encontrados, finalidade=finalidade)
    return render_template('buscar.html', encontrados=None)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))