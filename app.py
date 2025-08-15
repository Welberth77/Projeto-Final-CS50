import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Validação de email
def email_valido(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

# Validação da página de login
@app.route("/", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Validação do forms
        if not email or not password: 
            error = "No field can be empty"
            return render_template("index.html", error=error)
        
        # Abrir conexão com o banco de dados
        conn = sqlite3.connect("database.db")
        db = conn.cursor()
        # Verificar se email existe no banco de dados
        db.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (email,))
        user = db.fetchone()
        conn.close()

        # Email não encontrado
        if user is None:
            error = "Email not found"
            return render_template("index.html", error=error)
    
        user_id, user_name, password_hash = user

         # Verificar senha
        if not check_password_hash(password_hash, password):
            error = "Senha incorreta."
            return render_template("index.html", error=error)

        # Login bem-sucedido
        session["user_id"] = user_id
        return redirect("home")

    else:
        return render_template("index.html")


# Validação da página de Sign in
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirmation = request.form.get("passwordConfirmation")

        # Validação do forms
        if not name or not email or not password or not password_confirmation: 
            error = "No field can be empty"
            return render_template("register.html", error=error) 
        if not email_valido(email):
            error = "invalid email"
            return render_template("register.html", error=error) 

        if password != password_confirmation:
            error = "The passwords are not the same."
            return render_template("register.html", error=error) 

        # Gerar hash da senha
        password_hash = generate_password_hash(password)

        # Adicionar ao banco de dados
        conn = sqlite3.connect("database.db")
        db = conn.cursor()
        db.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", (name, email, password_hash))
        conn.commit()  # <- ESSENCIAL para salvar os dados
        conn.close()
        
        return redirect('/')
    else:
        return render_template("register.html")

# Home
@app.route("/home", methods=['GET'])
def home():
    return render_template("home.html")