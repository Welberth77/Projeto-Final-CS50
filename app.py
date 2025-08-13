from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

# Validação de email
def email_valido(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

# Validação da página de login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        return render_template("index.html")
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

        # Adicionar ao banco de dados
        
        return redirect('/')
    else:
        return render_template("register.html")
