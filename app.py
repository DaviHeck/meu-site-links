import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"

# Pegando a URL do banco de dados do Render
DATABASE_URL = os.getenv("DATABASE_URL")  # Render armazena a URL do banco nesta variável
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")  # Ajuste para SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Criando a instância do banco
db = SQLAlchemy(app)

# Modelo de Dados (Tabela no Banco)
class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)

# Criar as tabelas no banco
with app.app_context():
    db.create_all()

# Rota para página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para adicionar novo site
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_documento():
    if request.method == 'POST':
        tipo_doc = request.form['tipo_doc']
        nivel = request.form['nivel'].capitalize()
        nome = request.form['nome']
        url = request.form['url'].strip()

        # Verifica se a URL já existe
        if Documento.query.filter_by(url=url).first():
            flash("Erro: Esta URL já foi cadastrada!", "error")
            return redirect(url_for('adicionar_documento'))

        novo_documento = Documento(
            tipo=tipo_doc,
            nivel=nivel,
            nome=nome,
            url=url
        )

        if nivel == "Municipal":
            novo_documento.cidade = request.form['cidade']
            novo_documento.estado = request.form['estado']
        elif nivel == "Estadual":
            novo_documento.estado = request.form['estado']

        db.session.add(novo_documento)
        db.session.commit()
        
        flash("Link adicionado com sucesso!", "success")
        return redirect(url_for('listar_documentos'))
    
    return render_template('adicionar.html')

# Rota para listar todos os sites
@app.route('/listar')
def listar_documentos():
    documentos = Documento.query.all()
    return render_template('listar.html', documentos=documentos)

# Rota para buscar sites
@app.route('/buscar', methods=['GET', 'POST'])
def buscar_documento():
    if request.method == 'POST':
        busca = request.form['busca'].lower()
        finalidade = request.form['finalidade']
        documentos = Documento.query.filter(
            (Documento.nome.ilike(f"%{busca}%")) | 
            (Documento.tipo.ilike(f"%{busca}%")) | 
            (Documento.cidade.ilike(f"%{busca}%")) | 
            (Documento.estado.ilike(f"%{busca}%"))
        ).all()
        return render_template('buscar.html', encontrados=documentos, finalidade=finalidade)

    return render_template('buscar.html', encontrados=None)

# Executa a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
