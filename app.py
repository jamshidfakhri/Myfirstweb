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
        --bg: #f8f9ff;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        --bg-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        --card-bg: #1e293b;
        --text: #e5e7eb;
        --text-light: #94a3b8;
        --heading: #a78bfa;
        --accent: #a78bfa;
        --border: #334155;
        --shadow: rgba(0,0,0,0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    body {
        font-family: Tahoma, sans-serif;
        background: var(--bg);
        min-height: 100vh;
        color: var(--text);
        line-height: 1.9;
        transition: background 0.4s, color 0.4s;
    }

    /* ---------- هدر ---------- */
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
        transition: background 0.4s, border-color 0.4s;
        animation: slideDown 0.5s ease;
    }
    .logo {
        font-size: 20px;
        font-weight: bold;
        color: var(--heading);
        transition: transform 0.3s;
    }
    .logo:hover { transform: scale(1.08); }
    .topbar nav a {
        color: var(--text);
        text-decoration: none;
        margin: 0 10px;
        font-size: 15px;
        position: relative;
        transition: color 0.3s;
    }
    .topbar nav a::after {
        content: '';
        position: absolute;
        bottom: -5px;
        right: 0;
        width: 0;
        height: 2px;
        background: var(--accent);
        transition: width 0.3s;
    }
    .topbar nav a:hover { color: var(--accent); }
    .topbar nav a:hover::after { width: 100%; }
    .theme-btn {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: transparent;
        border: 2px solid var(--heading);
        color: var(--heading);
        font-size: 18px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s;
    }
    .theme-btn:hover { transform: rotate(20deg) scale(1.1); }

    /* ---------- هیرو ---------- */
    .hero {
        padding: 90px 25px 70px;
        text-align: center;
        background: var(--bg-gradient);
        background-size: 200% 200%;
        animation: gradientShift 12s ease infinite;
        color: #fff;
    }
    .hero h1 {
        font-size: 42px;
        margin-bottom: 20px;
        line-height: 1.4;
        color: #fff;
        animation: fadeInUp 0.8s ease;
    }
    .hero p {
        font-size: 18px;
        max-width: 600px;
        margin: 0 auto 35px;
        opacity: 0.95;
        animation: fadeInUp 1s ease;
    }
    .hero .btn {
        display: inline-block;
        background: #fff;
        color: #764ba2;
        padding: 15px 40px;
        border-radius: 40px;
        font-size: 17px;
        font-weight: bold;
        text-decoration: none;
        transition: transform 0.3s, box-shadow 0.3s;
        animation: fadeInUp 1.2s ease;
    }
    .hero .btn:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }

    /* ---------- کارت‌ها ---------- */
    .section {
        padding: 70px 25px;
        max-width: 1000px;
        margin: 0 auto;
    }
    .section-title {
        text-align: center;
        color: var(--heading);
        font-size: 28px;
        margin-bottom: 45px;
        animation: fadeInUp 0.6s ease;
    }
    .cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 25px;
    }
    .card {
        background: var(--card-bg);
        padding: 35px 25px;
        border-radius: 20px;
        border: 1px solid var(--border);
        text-align: center;
        transition: transform 0.4s, box-shadow 0.4s, border-color 0.4s;
        animation: fadeInUp 0.8s ease backwards;
    }
    .card:nth-child(1) { animation-delay: 0.1s; }
    .card:nth-child(2) { animation-delay: 0.25s; }
    .card:nth-child(3) { animation-delay: 0.4s; }
    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px var(--shadow);
        border-color: var(--accent);
    }
    .card .icon {
        font-size: 50px;
        margin-bottom: 15px;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    .card:nth-child(2) .icon { animation-delay: 0.5s; }
    .card:nth-child(3) .icon { animation-delay: 1s; }
    .card h3 {
        color: var(--heading);
        font-size: 20px;
        margin-bottom: 12px;
    }
    .card p {
        color: var(--text-light);
        font-size: 15px;
    }

    /* ---------- فوتر ---------- */
    footer {
        background: var(--card-bg);
        border-top: 1px solid var(--border);
        padding: 40px 25px 25px;
        text-align: center;
        color: var(--text-light);
        font-size: 14px;
    }
    footer a {
        color: var(--text-light);
        text-decoration: none;
        margin: 0 10px;
        font-size: 13px;
        opacity: 0.7;
        transition: color 0.3s, opacity 0.3s;
    }
    footer a:hover { color: var(--accent); opacity: 1; }
    footer .copy { margin-bottom: 15px; }

    /* ---------- صفحه‌های داخلی ---------- */
    .box {
        background: var(--card-bg);
        max-width: 700px;
        margin: 40px auto;
        padding: 40px 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px var(--shadow);
        border: 1px solid var(--border);
        transition: background 0.4s, border-color 0.4s;
        animation: fadeInUp 0.7s ease;
    }
    .box h1 { color: var(--heading); margin-bottom: 20px; }
    .box h2 { color: var(--heading); margin: 20px 0 10px; }
    .box p { color: var(--text); margin-bottom: 15px; }
    a { color: var(--accent); text-decoration: none; transition: opacity 0.3s; }
    a:hover { text-decoration: underline; }
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
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    input:focus, textarea:focus {
        outline: none;
        border-color: var(--heading);
        box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.12);
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
        transition: transform 0.3s, box-shadow 0.3s;
    }
    button.btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(118, 75, 162, 0.35);
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 25px 0; }
    .post-item {
        padding: 20px 0;
        border-bottom: 1px solid var(--border);
        transition: padding-right 0.3s;
        animation: fadeInUp 0.6s ease backwards;
    }
    .post-item:hover { padding-right: 10px; }
    .post-item:last-child { border-bottom: none; }
    .post-item h3 { color: var(--heading); margin-bottom: 8px; font-size: 20px; }
    .post-item .preview { color: var(--text-light); font-size: 15px; }

    @media (max-width: 600px) {
        .hero { padding: 60px 20px 45px; }
        .hero h1 { font-size: 28px; }
        .hero p { font-size: 15px; }
        .section { padding: 45px 20px; }
        .section-title { font-size: 22px; }
        .topbar { padding: 12px 15px; }
        .topbar nav a { margin: 0 5px; font-size: 13px; }
        .logo { font-size: 17px; }
        .box { padding: 25px 20px; margin: 20px 15px; }
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
        <div class="copy">ساخته شده با ❤️ و پایتون</div>
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
    return STYLE + topbar() + """
    <div class="hero">
        <h1>به سایت من خوش اومدی 👋</h1>
        <p>اینجا جاییه که تجربه‌های یادگیری برنامه‌نویسی‌ام رو باهات به اشتراک می‌ذارم. از پایتون و Flask تا ساخت ربات تلگرام و وب‌سایت.</p>
        <a href="/blog" class="btn">وبلاگم رو بخون</a>
    </div>

    <div class="section">
        <h2 class="section-title">اینجا چی پیدا می‌کنی؟</h2>
        <div class="cards">
            <div class="card">
                <div class="icon">📝</div>
                <h3>یادداشت‌های یادگیری</h3>
                <p>هر چیزی که یاد می‌گیرم رو اینجا می‌نویسم تا خودم هم بعداً مرورش کنم.</p>
            </div>
            <div class="card">
                <div class="icon">🤖</div>
                <h3>پروژه‌های واقعی</h3>
                <p>ربات تلگرام، وب‌سایت، و هر چیزی که با دست خودم ساختم.</p>
            </div>
            <div class="card">
                <div class="icon">🌱</div>
                <h3>مسیر یادگیری</h3>
                <p>از صفر شروع کردم. اگه تو هم تازه‌کاری، می‌تونی با من همراه بشی.</p>
            </div>
        </div>
    </div>
    """ + footer()


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = STYLE + topbar() + "<div class='box'><h1>وبلاگ من</h1><p>اینجا یادداشت‌هام رو می‌نویسم.</p><hr>"
    if not posts:
        html += "<p>هنوز پستی نوشته نشده. به زودی...</p>"
    for i, p in enumerate(posts):
        html += (
            "<div class='post-item' style='animation-delay:" + str(i * 0.1) + "s;'>"
            "<h3><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h3>"
            "<div class='preview'>" + p[2][:150] + "...</div>"
            "</div>"
        )
    html += "</div>" + footer()
    return html


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return STYLE + topbar() + "<div class='box'><h1>پست پیدا نشد</h1><p><a href='/blog'>برگرد به وبلاگ</a></p></div>" + footer(), 404
    return STYLE + topbar() + "<div class='box'><h1>" + p[1] + "</h1><p><a href='/blog'>← برگرد به وبلاگ</a></p><hr><p>" + p[2] + "</p></div>" + footer()


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return STYLE + topbar() + "<div class='box'><h1>رمز اشتباهه</h1><p><a href='/admin/login'>دوباره تلاش کن</a></p></div>" + footer()
    return STYLE + topbar() + """
    <div class='box'>
        <h1>ورود مدیریت</h1>
        <p>این بخش فقط برای مدیر سایته.</p>
        <form method='POST'>
            <input type='password' name='password' placeholder='رمز عبور' required>
            <button type='submit' class='btn-primary'>ورود</button>
        </form>
    </div>
    """ + footer()


@app.route("/admin/logout")
def admin_logout():
    session.pop("logged", None)
    return redirect("/")


@app.route("/admin/posts")
def admin_posts():
    if not logged_in():
        return redirect("/admin/login")
    posts = get_all_posts()
    html = STYLE + topbar() + "<div class='box'><h1>مدیریت پست‌ها</h1><p><a href='/admin/posts/new'>➕ پست جدید</a> | <a href='/admin/logout'>خروج</a></p><hr>"
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
    return STYLE + topbar() + """
    <div class='box'>
        <h1>پست جدید</h1>
        <form method='POST'>
            <input name='title' placeholder='عنوان پست' required>
            <textarea name='content' placeholder='متن پست رو اینجا بنویس...' required></textarea>
            <button type='submit' class='btn-primary'>ذخیره</button>
        </form>
        <p style="margin-top:15px;"><a href='/admin/posts'>لغو و برگشت</a></p>
    </div>
    """ + footer()


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
    return STYLE + topbar() + """
    <div class='box'>
        <h1>ویرایش پست</h1>
        <form method='POST'>
            <input name='title' value='""" + p[1] + """' required>
            <textarea name='content' required>""" + p[2] + """</textarea>
            <button type='submit' class='btn-primary'>ذخیره تغییرات</button>
        </form>
        <p style="margin-top:15px;"><a href='/admin/posts'>لغو و برگشت</a></p>
    </div>
    """ + footer()


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