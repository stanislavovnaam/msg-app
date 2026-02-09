from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
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
        formuser = request.form['username'].strip()
        formpass = request.form['password'].strip()

        if msg != "":
            conn = sqlite3.connect(DB_PATH)
            
            
            db_user = conn.execute("SELECT username FROM users WHERE username = ?", (formuser,)).fetchone()
            
            if db_user is None:
                conn.execute(
                    "INSERT INTO users (username,password) VALUES (?,?)",
                    (formuser,formpass)
                )
                print("account created")
                loggedIn =True
            else:
                print("user exists!")
                db_pass = conn.execute("SELECT password FROM users WHERE username = ?", (formuser,)).fetchone()
                
                if formpass == db_pass[0]:
                    loggedIn =True
                else:
                    sysmsg = "wrong pass"
                    
                if loggedIn:
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

    return render_template('index.html', msgs=msgs, sysmsg=sysmsg, user=formuser, passed=formpass)

@app.route('/database')
def database():
    conn = sqlite3.connect(DB_PATH)
    msgs = conn.execute("SELECT * FROM msgs").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    
    return str(msgs) + "<br><br>" + str(users)

if __name__ == "__main__":
    app.run()
