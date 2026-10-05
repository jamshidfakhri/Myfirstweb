import os
import sqlite3
from flask import Flask, request, redirect, session, jsonify, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DB_NAME = "site_data.db"

STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {
        --bg: #f8f9ff;
        --card-bg: #ffffff;
        --text: #1f2937;
        --text-light: #6b7280;
        --heading: #764ba2;
        --accent: #667eea;
        --border: #e5e7eb;
        --shadow: rgba(0,0,0,0.08);
    }
    [data-theme="dark"] {
        --bg: #0f172a;
        --card-bg: #1e293b;
        --text: #e5e7eb;
        --text-light: #94a3b8;
        --heading: #a78bfa;
        --accent: #a78bfa;
        --border: #334155;
        --shadow: rgba(0,0,0,0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: Tahoma, sans-serif;
        background: var(--bg);
        min-height: 100vh;
        color: var(--text);
        line-height: 1.9;
    }
    .topbar {
        position: sticky;
        top: 0;
        background: var(--card-bg);
        border-bottom: 1px solid var(--border);
        padding: 15px 25px;
        z-index: 100;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .logo { font-size: 20px; font-weight: bold; color: var(--heading); }
    .topbar nav a {
        color: var(--text);
        text-decoration: none;
        margin: 0 10px;
        font-size: 15px;
    }
    .topbar nav a:hover { color: var(--accent); }
    .theme-btn {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: transparent;
        border: 2px solid var(--heading);
        color: var(--heading);
        font-size: 18px;
        cursor: pointer;
    }
    .box {
        background: var(--card-bg);
        max-width: 700px;
        margin: 40px auto;
        padding: 40px 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px var(--shadow);
        border: 1px solid var(--border);
    }
    .box h1 { color: var(--heading); margin-bottom: 20px; }
    .box p { color: var(--text); margin-bottom: 15px; }
    a { color: var(--accent); text-decoration: none; }
    input, textarea {
        width: 100%;
        padding: 13px 16px;
        border: 2px solid var(--border);
        border-radius: 12px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        margin-bottom: 15px;
        background: var(--card-bg);
        color: var(--text);
    }
    textarea { min-height: 150px; resize: vertical; }
    button.btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        padding: 13px 32px;
        border: none;
        border-radius: 30px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        cursor: pointer;
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 25px 0; }
    .post-item { padding: 20px 0; border-bottom: 1px solid var(--border); }
    .post-item:last-child { border-bottom: none; }
    .post-item h3 { color: var(--heading); margin-bottom: 8px; font-size: 20px; }
    .post-item .preview { color: var(--text-light); font-size: 15px; }
    footer {
        background: var(--card-bg);
        border-top: 1px solid var(--border);
        padding: 40px 25px 25px;
        text-align: center;
        color: var(--text-light);
        font-size: 14px;
    }
    footer a { color: var(--text-light); margin: 0 10px; font-size: 13px; }
</style>
<script>
    (function() {
        var saved = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
    })();
    function toggleTheme() {
        var current = document.documentElement.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        var btn = document.getElementById('themeBtn');
        if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
    }
    window.addEventListener('DOMContentLoaded', function() {
        var current = document.documentElement.getAttribute('data-theme');
        var btn = document.getElementById('themeBtn');
        if (btn) btn.textContent = current === 'dark' ? '☀️' : '🌙';
    });
</script>
"""


def topbar():
    return """
    <div class="topbar">
        <div class="logo">سایت من</div>
        <nav>
            <a href="/">خانه</a>
            <a href="/blog">وبلاگ</a>
            <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">🌙</button>
        </nav>
    </div>
    """


def footer():
    return """
    <footer>
        <div style="margin-bottom:15px;">ساخته شده با ❤️ و پایتون</div>
        <div>
            <a href="/">خانه</a>
            <a href="/blog">وبلاگ</a>
            <a href="/admin/login">ورود مدیریت</a>
        </div>
    </footer>
    """


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
    return render_template("home.html")


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = STYLE + topbar() + "<div class='box'><h1>وبلاگ</h1><hr>"
    if not posts:
        html += "<p>هنوز پستی نوشته نشده.</p>"
    for p in posts:
        html += "<div class='post-item'><h3><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h3><div class='preview'>" + p[2][:150] + "...</div></div>"
    html += "</div>" + footer()
    return html


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return STYLE + topbar() + "<div class='box'><h1>پست پیدا نشد</h1><a href='/blog'>برگرد</a></div>" + footer(), 404
    return STYLE + topbar() + "<div class='box'><h1>" + p[1] + "</h1><a href='/blog'>← برگرد</a><hr><p>" + p[2] + "</p></div>" + footer()


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return STYLE + topbar() + "<div class='box'><h1>رمز اشتباهه</h1><a href='/admin/login'>دوباره</a></div>" + footer()
    return STYLE + topbar() + "<div class='box'><h1>ورود مدیریت</h1><form method='POST'><input type='password' name='password' placeholder='رمز' required><button type='submit' class='btn-primary'>ورود</button></form></div>" + footer()


@app.route("/admin/logout")
def admin_logout():
    session.pop("logged", None)
    return redirect("/")


@app.route("/admin/posts")
def admin_posts():
    if not logged_in():
        return redirect("/admin/login")
    posts = get_all_posts()
    html = STYLE + topbar() + "<div class='box'><h1>مدیریت پست‌ها</h1><a href='/admin/posts/new'>پست جدید</a> | <a href='/admin/logout'>خروج</a><hr>"
    if not posts:
        html += "<p>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div class='post-item'><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div>"
    html += "</div>" + footer()
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
    return STYLE + topbar() + "<div class='box'><h1>پست جدید</h1><form method='POST'><input name='title' placeholder='عنوان' required><textarea name='content' placeholder='متن' required></textarea><button type='submit' class='btn-primary'>ذخیره</button></form></div>" + footer()


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
    return STYLE + topbar() + "<div class='box'><h1>ویرایش</h1><form method='POST'><input name='title' value='" + p[1] + "' required><textarea name='content' required>" + p[2] + "</textarea><button type='submit' class='btn-primary'>ذخیره</button></form></div>" + footer()


@app.route("/admin/posts/<int:pid>/delete", methods=["POST"])
def admin_delete(pid):
    if not logged_in():
        return redirect("/admin/login")
    delete_post(pid)
    return redirect("/admin/posts")


init_db()

if __name__ == "__