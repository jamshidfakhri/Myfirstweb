import os
import sqlite3
from flask import Flask, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DB_NAME = "site_data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()


def get_all_posts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_post(pid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM posts WHERE id = ?", (pid,))
    row = c.fetchone()
    conn.close()
    return row


def create_post(title, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()


def update_post(pid, title, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE posts SET title=?, content=? WHERE id=?", (title, content, pid))
    conn.commit()
    conn.close()


def delete_post(pid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (pid,))
    conn.commit()
    conn.close()


def logged_in():
    return session.get("logged", False)


@app.route("/ping")
def ping():
    return jsonify({"ok": True})


@app.route("/")
def home():
    return "<h1>سایت کار می کند</h1><a href='/blog'>وبلاگ</a> | <a href='/admin/login'>ورود ادمین</a>"


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = "<h1>وبلاگ</h1><a href='/'>خانه</a> | <a href='/admin/login'>ورود ادمین</a><hr>"
    if not posts:
        html += "<p>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div><h2><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h2><p>" + p[2][:100] + "...</p></div><hr>"
    return html


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return "پست پیدا نشد", 404
    return "<h1>" + p[1] + "</h1><a href='/blog'>برگرد</a><hr><p>" + p[2] + "</p>"


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return "<h1>رمز اشتباهه</h1><a href='/admin/login'>دوباره</a>"
    return """
    <h1>ورود ادمین</h1>
    <form method='POST'>
        <input type='password' name='password' placeholder='رمز' required>
        <button type='submit'>ورود</button>
    </form>
    """


@app.route("/admin/logout")
def admin_logout():
    session.pop("logged", None)
    return redirect("/")


@app.route("/admin/posts")
def admin_posts():
    if not logged_in():
        return redirect("/admin/login")
    posts = get_all_posts()
    html = "<h1>مدیریت پست‌ها</h1><a href='/admin/posts/new'>پست جدید</a> | <a href='/admin/logout'>خروج</a><hr>"
    for p in posts:
        html += "<div><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div><hr>"
    return html


@app.route("/admin/posts/new", methods=["GET", "POST"])
def admin_new():
    if not logged_in():
        return redirect("/admin/login")
    if request.method == "POST":
        t = request.form.get("title", "")
        c = request.form.get("content", "")
        if t and c:
            create_post(t, c)
            return redirect("/admin/posts")
    return """
    <h1>پست جدید</h1>
    <form method='POST'>
        <input name='title' placeholder='عنوان' required><br><br>
        <textarea name='content' placeholder='متن' required></textarea><br><br>
        <button type='submit'>ذخیره</button>
    </form>
    """


@app.route("/admin/posts/<int:pid>/edit", methods=["GET", "POST"])
def admin_edit(pid):
    if not logged_in():
        return redirect("/admin/login")
    p = get_post(pid)
    if not p:
        return redirect("/admin/posts")
    if request.method == "POST":
        t = request.form.get("title", "")
        c = request.form.get("content", "")
        if t and c:
            update_post(pid, t, c)
            return redirect("/admin/posts")
    return """
    <h1>ویرایش پست</h1>
    <form method='POST'>
        <input name='title' value='""" + p[1] + """' required><br><br>
        <textarea name='content' required>""" + p[2] + """</textarea><br><br>
        <button type='submit'>ذخیره</button>
    </form>
    """


@app.route("/admin/posts/<int:pid>/delete", methods=["POST"])
def admin_delete(pid):
    if not logged_in():
        return redirect("/admin/login")
    delete_post(pid)
    return redirect("/admin/posts")


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)