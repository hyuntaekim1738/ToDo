import os
import sqlite3
from flask import Flask, render_template, flash, request, redirect, session, g, url_for
from flask_session import Session
from functools import wraps

app = Flask(__name__)

"""DAILY TASK
Style the index page
"""

#login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#puts temporary login to the file
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

#makes sure that templates uato reoload
app.config["TEMPLATES_AUTO_RELOAD"]=True

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#database creation
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()
userCommand = """CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL)"""
homeworkCommand = """CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY,
    assignment TEXT NOT NULL,
    class TEXT NOT NULL,
    date TEXT NOT NULL,
    user INTEGER NOT NULL)"""
choreCommand = """CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY,
    chore TEXT NOT NULL,
    date TEXT NOT NULL,
    user INTEGER NOT NULL)"""
cursor.execute(userCommand)
cursor.execute(homeworkCommand)
cursor.execute(choreCommand)

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":      
        matches = cursor.execute("SELECT * FROM users WHERE username = ? AND password=?", (request.form.get("username"), request.form.get("password")))
        res=matches.fetchone()
        if res is None:
            return render_template("apology.html", errorMessage="Username or password is incorrect")
        else:
            session["user_id"] = res[0]
            return redirect("/")     
    else:
        return render_template("login.html")
        
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method=="POST":
         if not request.form.get("username"):
            return render_template("apology.html", errorMessage="You must enter a username")
         if not request.form.get("password"):
            return render_template("apology.html", errorMessage="You must enter a password")
         if not request.form.get("confirm-password"):
            return render_template("apology.html", errorMessage="You must confirm password")
         matches=cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
         if matches.fetchone() is None:
            if request.form.get("password")==request.form.get("confirm-password"):
                cursor.execute("INSERT INTO users (username, password) VALUES(?, ?)", (request.form.get("username"), request.form.get("password")))
                res = cursor.execute("SELECT id FROM users WHERE username=?", (request.form.get("username"),))
                res = res.fetchone()
                session["user_id"] = res[0]
                return redirect("/")
            else:
                return render_template("apology.html", errorMessage="Password does not match confirm password")
         else:
            return render_template("apology.html", errorMessage="Username is taken")
    else:
        return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/chores", methods=["GET", "POST"])
@login_required
def chores():
    if request.method=="POST":
        cursor.execute("INSERT INTO chores (chore, date, user) VALUES (?, ?, ?)", (request.form.get("chore-title"), request.form.get("date"), session["user_id"]))
        return redirect("/chores")
    else:
        cursor.execute("SELECT * FROM chores WHERE user = ? ORDER BY date ASC", (session["user_id"],))
        list=cursor.fetchall()
        #list.sort()
        return render_template("chores.html", list=list)

@app.route("/homework", methods=["GET", "POST"])
@login_required
def homework():
    if request.method=="POST":
        cursor.execute("INSERT INTO homework (assignment, class, date, user) VALUES (?, ?, ?, ?)", (request.form.get("homework-title"), request.form.get("class"), request.form.get("date"), session["user_id"]))
        return redirect("/homework")
    else:
        cursor.execute("SELECT * FROM homework WHERE user = ? ORDER BY date ASC", (session["user_id"],))
        list=cursor.fetchall()
        #list.sort()
        return render_template("homework.html", list=list)
#cursor.close() 
@app.route("/deleteHw",methods=["POST"])
@login_required
def deleteHw():
    cursor.execute("DELETE FROM homework WHERE id = ?", (request.form.get("hw"),))
    return redirect("/homework")

@app.route("/delete",methods=["POST"])
@login_required
def delete():
    cursor.execute("DELETE FROM chores WHERE id = ?", (request.form.get("chore"),))
    return redirect("/chores")