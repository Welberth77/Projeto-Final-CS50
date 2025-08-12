from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Validação da página de login
@app.route("/", methods=['GET', 'POST'])
def login():
    pass