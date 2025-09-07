import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
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


# Deslogar
@app.route("/logout")
def logout():
    usuario_id = session.get("user_id")

    if usuario_id:
        db = sqlite3.connect("database.db")
        db.execute("DELETE FROM carrinho WHERE usuario_id = ?", (usuario_id,))
        db.commit()
        db.close()

    session.clear()  # remove dados da sessão
    return redirect("/")  


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
    # Verifica se o usuário está logado
    if not session.get('user_id'):
        return redirect("/")
    
    # Conectando ao banco de dados
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row  # permite acessar por nome da coluna
    pizzas = db.execute('SELECT * FROM pizzas WHERE mais_vendida = 1 LIMIT 6').fetchall()

    db.close()
    return render_template('home.html', pizzas=pizzas)


# Menu (MOSTRA TODAS AS PIZZAS)
@app.route("/menu", methods=["GET"])
def menu():
    # Verificando de usuário está logado
    if not session.get('user_id'):
        return redirect("/")
    
    # pega o que foi digitado no Search
    q = request.args.get("q", "").strip()  

    # Conectando ao banco de dados
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row  

    # Se perquisou alguma pizza especifica
    if q:  
        pizzas = db.execute(
            "SELECT * FROM pizzas WHERE nome LIKE ? OR descricao LIKE ?",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    # Se não pesquisou mostra todas
    else:
        pizzas = db.execute('SELECT * FROM pizzas').fetchall()

    db.close()
    return render_template('menu.html', pizzas=pizzas)


# Adicionar ao carrinho
@app.route("/add_cart", methods=['POST'])
def add_cart():
    # Verificando se está logado
    user_id = session.get("user_id")
    if not user_id:
        flash("Você precisa estar logado para adicionar ao carrinho.")
        return redirect("/")

    # Conectando ao banco de dados
    db = sqlite3.connect("database.db")
    # Acessar por nomes por coluna
    db.row_factory = sqlite3.Row 
    # Pegando valores do usuário
    userId = session.get("user_id")

    # Pegando valores da pizza
    pizzaId = request.form.get("pizza_id")
    quantidade = int(request.form.get("quantity", 1))

    # validação da quantidade
    if quantidade < 1 or quantidade > 99:
        flash("Quantidade inválida. Escolha entre 1 e 99.", "danger")
        return redirect("home")
    
    # Buscar pizza
    cur = db.execute("SELECT id, preco, tempo_preparo FROM pizzas WHERE id = ?", (pizzaId,))
    pizza = cur.fetchone()
    # Pizza não encontrada
    if not pizza:
        flash("Pizza não encontrada.", "danger")
        return redirect("home")

    # Calcular preço total
    preco_unitario = pizza["preco"]
    preco_total = preco_unitario * quantidade

    # Calcular tempo total
    tempo_preparo = pizza["tempo_preparo"]
    tempo_preparo_total = tempo_preparo * quantidade

    # Adionando produtos ao banco de dados co carrinho
    db.execute('''
        INSERT INTO carrinho (usuario_id, pizza_id, quantidade, preco_unitario, preco_total, tempo_preparo_total)
        VALUES (?, ?, ?, ?, ?, ?)''', (userId, pizzaId, quantidade, preco_unitario, preco_total, tempo_preparo_total))
    db.commit()
    db.close()

    
    flash("Pizza added to the cart!", "success")
    page = request.form.get("page")
    return redirect(page or "home")


# Deletar item do carrinho
@app.route("/delete_item_cart", methods=["POST"])
def delete_item():
    userId = session.get("user_id")

    if not userId:
        return redirect("/")
    
    # Id do item
    item_id = request.form.get("item_id")
    
    db = sqlite3.connect("database.db")
    db.execute("DELETE FROM carrinho WHERE id = ? AND usuario_id = ?", (item_id, userId))
    db.commit()
    db.close()

    return redirect("cart")


# cart
@app.route("/cart", methods=['GET', 'POST'])
def cart():
    
    user_id = session.get("user_id")
    
    # Verifica se o usuário está logado
    if not user_id:
        return redirect("/")
    
    # Conectando ao bando de dados
    db = sqlite3.connect("database.db")
    # Acessar os dados pelo nome da coluna
    db.row_factory = sqlite3.Row  
    # Junção das tabelas Pizzas e Carrinho
    cartItems = db.execute('''
        SELECT c.id,
            c.quantidade,
            c.preco_unitario,
            c.preco_total,
            c.tempo_preparo_total,
            p.nome
        FROM carrinho c
        JOIN pizzas p ON c.pizza_id = p.id
        WHERE c.usuario_id = ?
    ''', (user_id,)).fetchall()

    # Totais do carrinho
    totals = db.execute('''
        SELECT 
            COALESCE(SUM(c.preco_total), 0) AS total_preco,
            COALESCE(SUM(c.tempo_preparo_total), 0) AS total_tempo
        FROM carrinho c
        WHERE c.usuario_id = ?
    ''', (user_id,)).fetchone()

    db.close()

    # formatando preço para 2 casas decimais
    total_preco = round(totals["total_preco"], 2)

    # Formatando tempo para horas e minutos
    minutos = totals["total_tempo"]
    if minutos >= 60:
        horas = minutos // 60
        minutos_rest = minutos % 60
        if minutos_rest > 0:
            total_tempo = f"{horas}h {minutos_rest}min"
        else:
            total_tempo = f"{horas}h"
    else:
        total_tempo = f"{minutos}min"

    totals = {
        "total_preco": total_preco,
        "total_tempo": total_tempo
    }

    return render_template("cart.html", cartItems=cartItems, totals=totals)
