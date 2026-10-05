import os
import sqlite3
from flask import Flask, request, redirect, session, jsonify, render_template

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


def create_post(t, ct):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (t, ct))
    conn.commit()
    conn.close()


def update_post(pid, t, ct):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE posts SET title=?, content=? WHERE id=?", (t, ct, pid))
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


def render_page(title, content):
    return render_template("page.html", title=title, content=content)


@app.route("/ping")
def ping():
    return jsonify({"ok": True})


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = "<h1>وبلاگ</h1>"
    if not posts:
        html += "<p class='muted'>هنوز پستی نوشته نشده.</p>"
    for p in posts:
        html += "<div class='post'><h2><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h2><p class='muted'>" + p[2][:150] + "...</p></div>"
    return render_page("وبلاگ", html)


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return render_page("پیدا نشد", "<h1>پست پیدا نشد</h1><p><a href='/blog'>برگرد به وبلاگ</a></p>"), 404
    html = "<h1>" + p[1] + "</h1><p class='muted'><a href='/blog'>← برگرد به وبلاگ</a></p><hr><p>" + p[2] + "</p>"
    return render_page(p[1], html)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return render_page("خطا", "<h1>رمز اشتباهه</h1><p><a href='/admin/login'>دوباره</a></p>")
    html = "<h1>ورود مدیریت</h1><form method='POST'><input type='password' name='password' placeholder='رمز عبور' required><button type='submit' class='btn'>ورود</button></form>"
    return render_page("ورود", html)


@app.route("/admin/logout")
def admin_logout():
    session.pop("logged", None)
    return redirect("/")


@app.route("/admin/posts")
def admin_posts():
    if not logged_in():
        return redirect("/admin/login")
    posts = get_all_posts()
    html = "<h1>مدیریت پست‌ها</h1><p><a href='/admin/posts/new'>➕ پست جدید</a> | <a href='/admin/logout'>خروج</a></p><hr>"
    if not posts:
        html += "<p class='muted'>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div class='post'><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div>"
    return render_page("مدیریت", html)


@app.route("/admin/posts/new", methods=["GET", "POST"])
def admin_new():
    if not logged_in():
        return redirect("/admin/login")
    if request.method == "POST":
        t = request.form.get("title", "")
        ct = request.form.get("content", "")
        if t and ct:
            create_post(t, ct)
            return redirect("/admin/posts")
    html = "<h1>پست جدید</h1><form method='POST'><input name='title' placeholder='عنوان' required><textarea name='content' placeholder='متن' required></textarea><button type='submit' class='btn'>ذخیره</button></form><p><a href='/admin/posts'>لغو</a></p>"
    return render_page("پست جدید", html)


@app.route("/admin/posts/<int:pid>/edit", methods=["GET", "POST"])
def admin_edit(pid):
    if not logged_in():
        return redirect("/admin/login")
    p = get_post(pid)
    if not p:
        return redirect("/admin/posts")
    if request.method == "POST":
        t = request.form.get("title", "")
        ct = request.form.get("content", "")
        if t and ct:
            update_post(pid, t, ct)
            return redirect("/admin/posts")
    html = "<h1>ویرایش پست</h1><form method='POST'><input name='title' value='" + p[1] + "' required><textarea name='content' required>" + p[2] + "</textarea><button type='submit' class='btn'>ذخیره</button></form><p><a href='/admin/posts'>لغو</a></p>"
    return render_page("ویرایش", html)


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