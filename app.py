from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Nome do arquivo onde os dados serão armazenados
ARQUIVO_DADOS = "documentos_sites.json"

# Função para carregar os documentos do arquivo JSON
def carregar_documentos():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"documentos": []}

# Função para salvar os documentos no arquivo JSON
def salvar_documentos(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para adicionar novo site
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_documento():
    if request.method == 'POST':
        dados = carregar_documentos()
        tipo_doc = request.form['tipo_doc']
        nivel = request.form['nivel'].capitalize()
        nome = request.form['nome']
        url = request.form['url']
        
        if nivel not in ["Municipal", "Estadual", "Federal"]:
            return "Nível inválido! Use Municipal, Estadual ou Federal.", 400

        novo_documento = {
            "tipo": tipo_doc,
            "nivel": nivel,
            "nome": nome,
            "url": url,
            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if nivel == "Municipal":
            novo_documento["cidade"] = request.form['cidade']
            novo_documento["estado"] = request.form['estado']
        elif nivel == "Estadual":
            novo_documento["estado"] = request.form['estado']
        
        dados["documentos"].append(novo_documento)
        salvar_documentos(dados)
        return redirect(url_for('listar_documentos'))
    return render_template('adicionar.html')

# Rota para listar todos os sites
@app.route('/listar')
def listar_documentos():
    dados = carregar_documentos()
    return render_template('listar.html', documentos=dados["documentos"])

# Rota para buscar sites
@app.route('/buscar', methods=['GET', 'POST'])
def buscar_documento():
    if request.method == 'POST':
        busca = request.form['busca'].lower()
        finalidade = request.form['finalidade']
        dados = carregar_documentos()
        encontrados = []
        for doc in dados["documentos"]:
            if (busca in doc["nome"].lower() or 
                busca in doc["tipo"].lower() or 
                ("cidade" in doc and busca in doc["cidade"].lower()) or 
                ("estado" in doc and busca in doc["estado"].lower())):
                encontrados.append(doc)
        
        return render_template('buscar.html', encontrados=encontrados, finalidade=finalidade)
    return render_template('buscar.html', encontrados=None)

# Executa a aplicação
if __name__ == '__main__':
    app.run(debug=True)
    