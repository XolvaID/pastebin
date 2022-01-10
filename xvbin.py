'sialan kau tukang recode'
import os
from flask import Flask, redirect, url_for, render_template, Markup, request, Response, send_from_directory
from flask_bootstrap import Bootstrap
from hashids import Hashids
import sqlite3
# DEFINE GLOBAL VARIABLE #
__author__ = "xolvadev"
app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "PASTE"
hash = Hashids(min_length=5, salt="PASTE")

# DETECTING DATABASE *

try:
	open("PASTE.XV")
except FileNotFoundError:
	x = sqlite3.connect("PASTE.XV")
	sc = """
CREATE TABLE xv (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT NOT NULL,
	content TEXT NOT NULL,
	date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
	);
"""
	x.executescript(sc)
else:
	pass
	
@app.errorhandler(404)
def not_found():
    return render_template("404.html")

@app.route("/favicon.ico")
def favicon():
	return send_from_directory(os.path.join(app.root_path,'static'),
	'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route("/")
def home():
	return redirect(url_for("paste"))
@app.route("/paste",methods=["GET","POST"])
def paste():
	if request.method == "POST":
		title = request.form["title"]
		content = request.form["content"]
		if not title or not content:
			flash("Empty Title Or Content")
			return redirect(url_for("paste"))
		else:
			# CONNECTING TO DATABASE #
			x = sqlite3.connect("PASTE.XV")
			c = x.cursor()
			z = c.execute("INSERT INTO xv (title,content) VALUES (?,?)",
			(title,content,))
			x.commit()
			paste_id = z.lastrowid
			created = c.execute("SELECT * FROM xv WHERE id = (?)",(paste_id,)).fetchone()[3]
			c.close()
			hashid = hash.encode(paste_id)
			paste_url = request.host_url + "p/" + hashid
			raw_paste_url = request.host_url + "raw/" + hashid
			paste_url = Markup(f'''<div class="alert alert-success">XV-Bin Successfully Created
<br><br>
Paste URL :- {paste_url}<br>
Raw Paste URL :- {raw_paste_url}<br><br>
Created :- {created}<br>
<br>
Please Note This Paste Is PERMANENT, cant be deleted, Or edited!</div>''')
			return render_template("index.html", paste_url=paste_url)
	else:
		return render_template("index.html")

@app.route("/p/<id>", methods=["GET"])
def getPaste(id):
	x = sqlite3.connect("PASTE.XV")
	c = x.cursor()
	original_id = hash.decode(id)
	if original_id:
		original_id = original_id[0]
		raw = c.execute("SELECT * FROM xv WHERE id = (?)",(original_id,)).fetchone()
		title, content, date = raw[1], raw[2], raw[3]
		return render_template("paste.html", title=title, content=content, date=date)
	else:
		return render_template("404.html")

@app.route("/raw/<id>", methods=["GET"])
def getRawPaste(id):
	x = sqlite3.connect("PASTE.XV")
	c = x.cursor()
	original_id = hash.decode(id)
	if original_id:
		original_id = original_id[0]
		raw = c.execute("SELECT * FROM xv WHERE id = (?)",(original_id,)).fetchone()[2]
		return Response(raw, mimetype='text/plain')
	else:
		return render_template("404.html")

if __name__ == "__main__":
	app.run(debug=False, host="0.0.0.0",port=443)
