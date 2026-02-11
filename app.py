from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret"
DB_PATH = "data.db"

def init_db():
    #if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS msgs (
                username TEXT,
                msg TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT,
                password TEXT
            )
        """)
        conn.commit()
        conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    sysmsg = ""
    loggedIn = False
    formuser = ""
    formpass = ""
    # POST
    if request.method == 'POST':
        msg = request.form['msg'].strip()

        if msg != "":
            conn = sqlite3.connect(DB_PATH)
            
            formuser = session.get('username')
            #if loggedIn:
            conn.execute(
                    "INSERT INTO msgs (username,msg) VALUES (?,?)",
                    (formuser,msg)
                 )
            conn.commit()
            conn.close()

        #return redirect('/')

    # GET 
    conn = sqlite3.connect(DB_PATH)
    msgs = conn.execute("SELECT * FROM msgs").fetchall()
    conn.close()

    return render_template('index.html', msgs=msgs, sysmsg=sysmsg)

@app.route('/database')
def database():
    conn = sqlite3.connect(DB_PATH)
    msgs = conn.execute("SELECT * FROM msgs").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    
    return render_template('database.html', msgs=msgs, users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    sysmsg = ""
    conn = sqlite3.connect(DB_PATH)
    if request.method == 'POST':
        formuser = request.form['username'].strip()
        formpass = request.form['password'].strip()

        db_user = conn.execute("SELECT username FROM users WHERE username = ?", (formuser,)).fetchone()

        if db_user is None:
            encryptedPass = generate_password_hash(formpass)
            conn.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (formuser,encryptedPass)
            )
            print("account created")
            loggedIn =True
            sysmsg = "account created"
        else:
            print("user exists!")
            db_pass = conn.execute("SELECT password FROM users WHERE username = ?", (formuser,)).fetchone()

            if check_password_hash(db_pass[0], formpass):
                loggedIn =True
                sysmsg = "logged in"
            else:
                sysmsg = "wrong pass"
                
        conn.commit()
        conn.close() 
                
        if loggedIn:
            session['username'] = formuser
            return redirect('/')
                
           
    return render_template('login.html', sysmsg=sysmsg)

if __name__ == "__main__":
    app.run()
