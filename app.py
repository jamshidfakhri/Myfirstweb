import os
import sqlite3
from flask import Flask, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DB_NAME = "site_data.db"

STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    :root {
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-bg: #ffffff;
        --text-color: #333333;
        --text-secondary: #555555;
        --heading-color: #764ba2;
        --link-color: #667eea;
        --border-color: #eeeeee;
        --input-border: #e0e0e0;
    }
    [data-theme="dark"] {
        --bg-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        --card-bg: #1f2937;
        --text-color: #e5e7eb;
        --text-secondary: #b0b0b0;
        --heading-color: #a78bfa;
        --link-color: #a78bfa;
        --border-color: #374151;
        --input-border: #374151;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: Tahoma, sans-serif;
        background: var(--bg-gradient);
        min-height: 100vh;
        padding: 20px;
        color: var(--text-color);
        line-height: 1.8;
        transition: background 0.4s, color 0.4s;
    }
    .box {
        background: var(--card-bg);
        max-width: 700px;
        margin: 0 auto;
        padding: 40px 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: background 0.4s;
    }
    .hero { text-align: center; margin-bottom: 25px; }
    .hero h1 { color: var(--heading-color); font-size: 32px; margin-bottom: 15px; }
    .hero p { color: var(--text-secondary); font-size: 17px; margin-bottom: 25px; }
    .nav-links { text-align: center; padding-top: 20px; border-top: 1px solid var(--border-color); }
    a { color: var(--link-color); text-decoration: none; margin: 0 8px; font-weight: bold; }
    a:hover { text-decoration: underline; }
    .btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff !important;
        padding: 14px 30px;
        border-radius: 30px;
        text-decoration: none !important;
        margin: 5px;
    }
    .btn:hover { text-decoration: none !important; opacity: 0.9; }
    input, textarea {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid var(--input-border);
        border-radius: 10px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        margin-bottom: 15px;
        background: var(--card-bg);
        color: var(--text-color);
        transition: border-color 0.3s, background 0.4s, color 0.4s;
    }
    input:focus, textarea:focus { outline: none; border-color: var(--heading-color); }
    textarea { min-height: 150px; resize: vertical; }
    button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        padding: 14px 30px;
        border: none;
        border-radius: 30px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        cursor: pointer;
    }
    button:hover { opacity: 0.9; }
    hr { border: none; border-top: 1px solid var(--border-color); margin: 20px 0; }
    h2 { color: var(--heading-color); }
    .theme-btn {
        position: fixed;
        top: 20px;
        left: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--card-bg);
        border: 2px solid var(--heading-color);
        color: var(--heading-color);
        font-size: 22px;
        cursor: pointer;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s, background 0.4s;
    }
    .theme-btn:hover { transform: rotate(20deg) scale(1.1); }
    @media (max-width: 600px) {
        body { padding: 10px; }
        .box { padding: 25px 20px; border-radius: 15px; }
        .hero h1 { font-size: 24px; }
        .hero p { font-size: 15px; }
        .theme-btn { top: 10px; left: 10px; width: 42px; height: 42px; font-size: 18px; }
    }
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

THEME_BTN = "<button class='theme-btn' id='themeBtn' onclick='toggleTheme()'>🌙</button>"


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
    return STYLE + THEME_BTN + """
    <div class='box'>
        <div class='hero'>
            <h1>به سایت من خوش اومدی 👋</h1>
            <p>اینجا جاییه که تجربه‌های یادگیری برنامه‌نویسی‌ام رو باهات به اشتراک می‌ذارم. از پایتون و Flask تا ساخت ربات تلگرام و وب‌سایت.</p>
            <a href='/blog' class='btn'>وبلاگم رو بخون</a>
        </div>
        <div class='nav-links'>
            <a href='/blog'>وبلاگ</a>
            <a href='/admin/login'>ورود ادمین</a>
        </div>
    </div>
    """


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = STYLE + THEME_BTN + "<div class='box'><h1>وبلاگ من</h1><a href='/'>خانه</a> | <a href='/admin/login'>ورود ادمین</a><hr>"
    if not posts:
        html += "<p>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div><h2><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h2><p>" + p[2][:150] + "...</p></div><hr>"
    html += "<p><a href='/'>برگرد به خانه</a></p></div>"
    return html


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return STYLE + THEME_BTN + "<div class='box'><h1>پست پیدا نشد</h1><a href='/blog'>برگرد</a></div>", 404
    return STYLE + THEME_BTN + "<div class='box'><h1>" + p[1] + "</h1><a href='/blog'>برگرد به وبلاگ</a><hr><p>" + p[2] + "</p></div>"


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return STYLE + THEME_BTN + "<div class='box'><h1>رمز اشتباهه</h1><a href='/admin/login'>دوباره تلاش کن</a></div>"
    return STYLE + THEME_BTN + """
    <div class='box'>
        <h1>ورود ادمین</h1>
        <form method='POST'>
            <input type='password' name='password' placeholder='رمز عبور' required>
            <button type='submit'>ورود</button>
        </form>
        <p><a href='/'>برگرد به خانه</a></p>
    </div>
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
    html = STYLE + THEME_BTN + "<div class='box'><h1>مدیریت پست‌ها</h1><a href='/admin/posts/new'>پست جدید</a> | <a href='/admin/logout'>خروج</a><hr>"
    if not posts:
        html += "<p>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div><hr>"
    html += "</div>"
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
    return STYLE + THEME_BTN + """
    <div class='box'>
        <h1>پست جدید</h1>
        <form method='POST'>
            <input name='title' placeholder='عنوان' required>
            <textarea name='content' placeholder='متن' required></textarea>
            <button type='submit'>ذخیره</button>
        </form>
        <p><a href='/admin/posts'>لغو</a></p>
    </div>
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
    return STYLE + THEME_BTN + """
    <div class='box'>
        <h1>ویرایش پست</h1>
        <form method='POST'>
            <input name='title' value='""" + p[1] + """' required>
            <textarea name='content' required>""" + p[2] + """</textarea>
            <button type='submit'>ذخیره</button>
        </form>
        <p><a href='/admin/posts'>لغو</a></p>
    </div>
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