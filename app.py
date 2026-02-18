from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret"

DB_PATH = "data.db"


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secret"


# ---------------------------
# Инициализация базы данных
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)

    # Таблица сообщений
    conn.execute("""
        CREATE TABLE IF NOT EXISTS msgs (
            username TEXT,
            msg TEXT
        )
    """)

    # Таблица пользователей
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            password TEXT
        )
    """)
    
    # Создания админ аккаунта
    hashed = generate_password_hash(ADMIN_PASSWORD)

    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (ADMIN_USERNAME, hashed)
    )

    conn.commit()
    conn.close()


init_db()


# ---------------------------
# Главная страница (чат)
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def index():

    # Если пользователь не залогинен — отправляем на login
    if 'username' not in session:
        return redirect('/login')

    # POST — отправка сообщения
    if request.method == 'POST':
        msg = request.form['msg'].strip()

        if msg:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO msgs (username, msg) VALUES (?, ?)",
                (session['username'], msg)
            )
            conn.commit()
            conn.close()

            return redirect('/')  # предотвращаем повторную отправку формы
        
    is_admin = False
    user = session.get('username')
    
    if user and user == ADMIN_USERNAME:
        is_admin = True
    # GET — получение сообщений
    conn = sqlite3.connect(DB_PATH)
    msgs = conn.execute("SELECT * FROM msgs").fetchall()
    conn.close()

    return render_template('index.html', msgs=msgs, is_admin=is_admin)


# ---------------------------
# Просмотр базы (для отладки)
# ---------------------------
@app.route('/database')
def database():
    conn = sqlite3.connect(DB_PATH)

    msgs = conn.execute("SELECT * FROM msgs").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()

    conn.close()

    return render_template('database.html', msgs=msgs, users=users)


# ---------------------------
# Админ панель
# ---------------------------
@app.route('/admin')
def admin():
    is_admin = False
    user = session.get('username')
    
    if user and user == ADMIN_USERNAME:
        is_admin = True
    
    if is_admin:
        conn = sqlite3.connect(DB_PATH)
        users = conn.execute("SELECT username FROM users").fetchall()
        conn.close()
        return render_template('admin.html',users=users)
    else:
        return "Доступ запрещен"
    


# ---------------------------
# Логин / регистрация
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            return render_template('login.html', sysmsg="Введите логин и пароль")

        conn = sqlite3.connect(DB_PATH)

        # Проверяем, существует ли пользователь
        user = conn.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            # Пользователя нет → создаём аккаунт
            hashed = generate_password_hash(password)

            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
            conn.close()

            session['username'] = username
            return redirect('/')

        else:
            # Пользователь существует → проверяем пароль
            stored_hash = user[0]

            if check_password_hash(stored_hash, password):
                conn.close()
                session['username'] = username
                return redirect('/')
            else:
                conn.close()
                return render_template('login.html', sysmsg="Неверный пароль")

    return render_template('login.html')


# ---------------------------
# Выход
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------------------
# Запуск
# ---------------------------
if __name__ == "__main__":
    app.run()
