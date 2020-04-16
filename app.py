import csv
import re
import json

from flask import Flask, jsonify, redirect, render_template, request
from ucnumber import validate # TODO
from urllib.parse import urlparse

# Check database
try:
    with open('cursos.csv', 'r', newline='') as cursos:
        reader = csv.DictReader(cursos, fieldnames=["Sigla", "Sección", "Facultad", "Plataforma", "Link"])
        next(reader, None)
        modelo = [row for row in reader]
except FileNotFoundError:
    with open('cursos.csv', 'w', newline='') as cursos:
        writer = csv.DictWriter(cursos, fieldnames=["Sigla", "Sección", "Facultad", "Plataforma", "Link"])
        writer.writeheader()

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    try:
        form = {
            "Sigla": request.form['Sigla'],
            "Sección": request.form['Sección'],
            "Facultad": request.form['Facultad'],
            "Plataforma": request.form['Plataforma'],
            "Link": request.form['Link']
        }

        if valid_form(form['Sigla'], form['Facultad'], form['Plataforma'], form['Sección'], form['Link']):
            write_row(form)
            return redirect("/sheet")
        else:
            return render_template("error.html", message="El formulario que enviaste era inválido. Asegúrate que pusiste todo bien!")
    except KeyError:
        raise
        return render_template("error.html", message="Tu formulario tiene un header inválido. ¿Qué estás intentando?")

def validar_url(link):
    dominios_permitidos = ["zoom.us", "uc.cl", "cursos.canvas.uc.cl", "meet.google.com", "discordapp.com"]
    try:
        url = urlparse(link)
        if url.hostname not in dominios_permitidos:
            return False
        else:
            return True
    except:
        return False

@app.route("/sheet", methods=["GET"])
def sheet():
    return render_template("sheet.html", message="TODO")


def valid_form(sigla, facultad, plataforma, seccion, link):
    facultades = ["Ingeniería", "Matemáticas", "Ciencias Biológicas"]
    plataformas = ["Zoom", "Meet", "Canvas", "Discord"]
    try:
        seccion = int(seccion) # Probar si es un entero válido
    except TypeError:
        return False

    if facultad not in facultades:
        return False
    elif sigla == "":
        return False
    elif len(sigla) > 10:
        return False
    elif plataforma not in plataformas:
        return False
    elif not (0 < seccion < 50):
        return False
    elif not validar_url(link):
        return False
    else:
        return True

def revisar_existente(sigla, seccion):
    for indice, entrada in enumerate(modelo):
        if entrada['Sigla'] == sigla:
            if entrada['Sección'] == seccion:
                return indice
    return False

def write_row(form):
    if revisar_existente(form["Sigla"], form["Sección"]):
        print("Found existing course.")
    else:
        with open('cursos.csv', 'a', newline='') as cursos:
            writer = csv.DictWriter(cursos, fieldnames=["Sigla", "Sección", "Facultad", "Plataforma", "Link"])
            writer.writerow(form)
    update_sheet()

def update_sheet():
    with open('cursos.csv', 'r', newline='') as cursos:
        reader = csv.DictReader(cursos, fieldnames=["Sigla", "Sección", "Facultad", "Plataforma", "Link"])
        next(reader, None)
        modelo = [row for row in reader]
        sheet = json.dumps(modelo)
    with open('static/sheet.json', 'w', newline='') as sheetj:
        sheetj.write(sheet)