from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

        if not name or not email or not password or not password_confirmation:
            error = "Todos os campos são obrigatórios."
            return render_template("register.html", error=error)

        if password != password_confirmation:
            error = "As senhas não coincidem."
            return render_template('register.html', error=error)

        return render_template('register.html', error=error)
    else:
        return render_template("register.html")
