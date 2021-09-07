from flask import Flask, render_template, request, flash, redirect, session
from tempfile import mkdtemp
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from threading import Timer
import random
import csv
import sys

# Configure app
app = Flask(__name__)
app.secret_key = b'foo'

# Autoreload Templates
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Intialize DB (TODO: work with a CSV file)
WORDS = []
with open("data/glossario.csv", "r", encoding='ISO-8859-1') as f:
    header = [h.strip() for h in f.readline().split(';')]
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        entry = {}
        values = [x.strip() for x in row]
        entry[header[0]] = values[0]
        entry[header[1]] = values[1]
        entry[header[2]] = values[2]
        
        WORDS.append(entry)

# Write to main page
@app.route("/")
def index():
    session['life'] = 5
    return render_template("index.html", words = WORDS)

# Add Words
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")

    if request.method == "POST":        
        it = request.form.get("it")
        es = request.form.get("es")
        desc = request.form.get("desc")

        # Handle None Values
        if not it or not es:
            flash("Completa la entrada")
            return redirect("/add")
        desc = "" if not desc else desc

        # Check if words in dict
        for word in WORDS:
            if it == word['it']:
                flash("Palabra existente")
                return redirect("/add")

        # Append the word
        WORDS.append({'it': it, 'es':es, 'desc': desc})
        flash(f"Palabra añadida: {es}({it})")

        # Sumar palabra al CSV
        with open("data/glossario.csv", "a") as f:
            f.write(f"\n{it}; {es}; {desc}")

        return redirect("/")


@app.route("/remove", methods=["GET", "POST"])
def remove():
    if request.method == "GET":
        return render_template("remove.html", word_count=enumerate(WORDS))

    if request.method == "POST":
        i = request.form.get("index")
        if not i:
            flash("Ocurrio un error")
            return redirect("/remove")
        else:
            i = int(i)

        es, it = WORDS[i]['es'], WORDS[i]['it']
        WORDS.pop(i)

        flash(f"Palabra Removida: {es}({it})")
        return redirect("/")


@app.route("/play", methods=["GET", "POST"])
def play():

    if request.method == "GET":
        word = random.choice(WORDS)
        lang = {'es': 'español', 'it': 'italiano'}
        
        # Make selection
        choice = random.randint(0, 1)
        choice_lang = "es" if choice == 1 else "it"
        guess_lang = "es" if choice == 0 else "it"

        session['correct'] = word[guess_lang]
        return render_template("game.html", lifes=session['life'], lang=lang[guess_lang], word=word[choice_lang])

    if request.method == "POST":
        ans = request.form.get("ans")
        lifes = request.form.get("lifes")
        correct = session['correct']

        if not ans:
            ans = ""

        if not correct:
            assert False

        if ans.strip().lower() == correct.strip().lower():
            flash(f"Respuesta Correcta! {correct} = {ans}")
        else:
            flash(f"Respuesta Incorrecta! La respuesta correcta era {session['correct']} y no {ans}.")
            session['life'] = session['life'] - 1

        if session['life'] < 1:
            flash("Perdiste!")
            return redirect("/")
        
        return redirect("/play")
        
# Define function for QtWebEngine
def ui(location):
    qt_app = QApplication(sys.argv)
    web = QWebEngineView()
    web.setWindowTitle("Elenco Di Parole")
    web.resize(600, 600)
    web.load(QUrl(location))
    web.show()
    sys.exit(qt_app.exec_())
    
if __name__ == "__main__":
    # start sub-thread to open the browser.
    Timer(1, lambda: ui("http://127.0.0.1:5000/")).start()
    app.run(debug = False)
