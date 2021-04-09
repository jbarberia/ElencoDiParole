from flask import Flask, render_template, request, flash, redirect
from tempfile import mkdtemp
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from threading import Timer
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
WORDS = [{'it': 'foo', 'es': 'bar', 'desc': ""}]

# Write to main page
@app.route("/")
def index():
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

#@app.route("/play", methods=["GET", "POST"])
#def play():
#    pass


## Define function for QtWebEngine
#def ui(location):
#    qt_app = QApplication(sys.argv)
#    web = QWebEngineView()
#    web.setWindowTitle("Elenco Di Parole")
#    web.resize(600, 600)
#    web.load(QUrl(location))
#    web.show()
#    sys.exit(qt_app.exec_())
#    
#if __name__ == "__main__":
#    # start sub-thread to open the browser.
#    Timer(1, lambda: ui("http://127.0.0.1:5000/")).start()
#    app.run(debug = False)