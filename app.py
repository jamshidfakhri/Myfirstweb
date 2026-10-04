import os
import sqlite3
import urllib.request
import urllib.parse
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")

DB_NAME = "site_data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, count INTEGER)")
    cursor.execute("SELECT count FROM counter WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO counter (id, count) VALUES (1, 0)")
    conn.commit()
    conn.close()


def increment_visit():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE counter SET count = count + 1 WHERE id = 1")
    conn.commit()
    cursor.execute("SELECT count FROM counter WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def get_visit_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM counter WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def send_to_telegram(name, email, message):
    if not BOT_TOKEN or not ADMIN_ID:
        return False
    text = "پیام جدید از سایت\n\nاسم: " + name + "\nایمیل: " + email + "\n\nپیام:\n" + message
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = urllib.parse.urlencode({"chat_id": ADMIN_ID, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data=data)
        return True
    except Exception as e:
        print("Error: " + str(e))
        return False


CSS = """
<style>
    :root, [data-theme="white"] {
        --bg-gradient: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        --card-bg: #ffffff;
        --text-color: #333333;
        --text-secondary: #555555;
        --heading-color: #764ba2;
        --header-bg: rgba(255, 255, 255, 0.95);
        --accent: #667eea;
    }
    [data-theme="black"] {
        --bg-gradient: linear-gradient(-45deg, #0f0f0f, #1a1a1a, #2d2d2d, #0f0f0f);
        --card-bg: #1a1a1a;
        --text-color: #f5f5f5;
        --text-secondary: #b0b0b0;
        --heading-color: #a78bfa;
        --header-bg: rgba(26, 26, 26, 0.95);
        --accent: #a78bfa;
    }
    [data-theme="yellow"] {
        --bg-gradient: linear-gradient(-45deg, #f9d423, #ff4e50, #f9d423, #f6b93b);
        --card-bg: #fffbea;
        --text-color: #3a2e00;
        --text-secondary: #6b5500;
        --heading-color: #b8860b;
        --header-bg: rgba(255, 251, 234, 0.95);
        --accent: #b8860b;
    }
    [data-theme="cream"] {
        --bg-gradient: linear-gradient(-45deg, #f5e6d3, #e8d5b7, #f5e6d3, #d4c4a8);
        --card-bg: #fffaf0;
        --text-color: #4a3f2f;
        --text-secondary: #6b5d4a;
        --heading-color: #8b6f47;
        --header-bg: rgba(255, 250, 240, 0.95);
        --accent: #8b6f47;
    }
    [data-theme="purple"] {
        --bg-gradient: linear-gradient(-45deg, #667eea, #764ba2, #a78bfa, #8b5cf6);
        --card-bg: #faf5ff;
        --text-color: #3b1f5e;
        --text-secondary: #6b4a8f;
        --heading-color: #7c3aed;
        --header-bg: rgba(250, 245, 255, 0.95);
        --accent: #7c3aed;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(118, 75, 162, 0.7); }
        50% { box-shadow: 0 0 0 15px rgba(118, 75, 162, 0); }
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pingPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    body {
        font-family: Tahoma, sans-serif;
        background: var(--bg-gradient);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        color: var(--text-color);
    }
    header {
        background: var(--header-bg);
        padding: 15px 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    .header-inner {
        max-width: 900px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .menu-wrapper { position: relative; flex-shrink: 0; }
    .menu-btn {
        background: transparent;
        border: none;
        cursor: pointer;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 5px;
        border-radius: 8px;
    }
    .menu-btn span {
        display: block;
        width: 26px;
        height: 3px;
        background: var(--heading-color);
        border-radius: 3px;
        transition: transform 0.3s, opacity 0.3s;
    }
    .menu-btn.active span:nth-child(1) { transform: translateY(8px) rotate(45deg); }
    .menu-btn.active span:nth-child(2) { opacity: 0; }
    .menu-btn.active span:nth-child(3) { transform: translateY(-8px) rotate(-45deg); }
    .dropdown-menu {
        position: absolute;
        top: 50px;
        right: 0;
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        padding: 10px;
        min-width: 180px;
        display: none;
        z-index: 200;
    }
    .dropdown-menu.open { display: block; animation: slideDown 0.3s ease; }
    .dropdown-menu a {
        display: block;
        padding: 12px 16px;
        color: var(--text-color);
        text-decoration: none;
        border-radius: 8px;
        font-size: 15px;
    }
    .dropdown-menu a:hover { background: var(--accent); color: #fff; }
    .greeting {
        font-size: 17px;
        font-weight: bold;
        color: var(--heading-color);
        text-align: center;
        flex: 1;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }
    .ping-box {
        background: rgba(118, 75, 162, 0.1);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        color: var(--heading-color);
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ping-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        animation: pingPulse 2s infinite;
    }
    .theme-wrapper { position: relative; }
    .theme-btn {
        background: transparent;
        border: 2px solid var(--heading-color);
        color: var(--heading-color);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .theme-panel {
        position: absolute;
        top: 50px;
        left: 0;
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        padding: 15px;
        display: none;
        z-index: 200;
    }
    .theme-panel.open { display: block; animation: slideDown 0.3s ease; }
    .theme-panel p {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 10px;
        text-align: center;
    }
    .color-options { display: flex; gap: 10px; }
    .color-option {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 3px solid transparent;
        cursor: pointer;
    }
    .color-option.active { border-color: var(--heading-color); }
    .contact-float {
        position: fixed;
        bottom: 25px;
        left: 25px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        text-decoration: none;
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.5);
        z-index: 90;
        animation: pulse 2s infinite;
    }
    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
    .card {
        background: var(--card-bg);
        padding: 50px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
        animation: fadeInUp 0.8s ease;
    }
    .emoji {
        font-size: 70px;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 20px;
    }
    h1 { color: var(--heading-color); font-size: 34px; margin-bottom: 20px; }
    p { font-size: 18px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 30px; }
    .btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        padding: 16px 35px;
        border-radius: 30px;
        text-decoration: none;
        font-size: 16px;
        border: none;
        cursor: pointer;
        font-family: Tahoma, sans-serif;
    }
    form { display: flex; flex-direction: column; gap: 15px; text-align: right; }
    label { font-size: 16px; color: var(--text-secondary); margin-bottom: 5px; display: block; }
    input, textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        outline: none;
        background: var(--card-bg);
        color: var(--text-color);
    }
    textarea { resize: vertical; min-height: 120px; }
    .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    .stat-card {
        background: var(--card-bg);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
    }
    .stat-number { font-size: 36px; font-weight: bold; color: var(--heading-color); margin-bottom: 10px; }
    .stat-label { font-size: 15px; color: var(--text-secondary); }
    @media (max-width: 600px) {
        .greeting { font-size: 14px; }
        .ping-box { font-size: 11px; padding: 4px 8px; }
        .menu-btn span { width: 22px; }
    }
</style>
"""

EXTRA_CSS_PORTFOLIO = """
<style>
    .projects-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    .project-card {
        background: var(--card-bg);
        padding: 30px 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        text-decoration: none;
        color: var(--text-color);
        display: block;
        animation: fadeInUp 0.8s ease backwards;
    }
    .project-emoji { font-size: 55px; margin-bottom: 15px; display: inline-block; }
    .project-card h2 { color: var(--heading-color); font-size: 22px; margin-bottom: 15px; }
    .project-card p { font-size: 15px; line-height: 1.8; margin-bottom: 15px; }
    .project-tech {
        font-size: 13px;
        color: #999;
        padding-top: 15px;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
</style>
"""


JS_SCRIPT = """
<script>
    (function() {
        var savedTheme = localStorage.getItem('theme') || 'white';
        document.documentElement.setAttribute('data-theme', savedTheme);
    })();

    function toggleThemePanel() {
        var panel = document.getElementById('themePanel');
        if (panel) panel.classList.toggle('open');
    }

    function setTheme(name) {
        document.documentElement.setAttribute('data-theme', name);
        localStorage.setItem('theme', name);
        var options = document.querySelectorAll('.color-option');
        for (var i = 0; i < options.length; i++) {
            options[i].classList.remove('active');
            if (options[i].getAttribute('data-theme') === name) {
                options[i].classList.add('active');
            }
        }
        setTimeout(function() {
            var panel = document.getElementById('themePanel');
            if (panel) panel.classList.remove('open');
        }, 300);
    }

    function toggleMenu() {
        var menu = document.getElementById('dropdownMenu');
        var btn = document.getElementById('menuBtn');
        if (menu) menu.classList.toggle('open');
        if (btn) btn.classList.toggle('active');
    }

    window.addEventListener('click', function(e) {
        var menu = document.getElementById('dropdownMenu');
        var menuBtn = document.getElementById('menuBtn');
        var themePanel = document.getElementById('themePanel');
        var themeBtn = document.getElementById('themeBtn');
        if (menu && menuBtn && !menu.contains(e.target) && !menuBtn.contains(e.target)) {
            menu.classList.remove('open');
            menuBtn.classList.remove('active');
        }
        if (themePanel && themeBtn && !themePanel.contains(e.target) && !themeBtn.contains(e.target)) {
            themePanel.classList.remove('open');
        }
    });

    function measurePing() {
        var start = performance.now();
        fetch('/ping?t=' + Date.now(), {cache: 'no-store'})
            .then(function() {
                var end = performance.now();
                var ping = Math.round(end - start);
                var el = document.getElementById('pingValue');
                var dot = document.getElementById('pingDot');
                if (el) el.textContent = ping + ' ms';
                if (dot) {
                    if (ping < 200) dot.style.background = '#22c55e';
                    else if (ping < 500) dot.style.background = '#f59e0b';
                    else dot.style.background = '#ef4444';
                }
            })
            .catch(function() {
                var el = document.getElementById('pingValue');
                if (el) el.textContent = '-- ms';
            });
    }

    window.addEventListener('DOMContentLoaded', function() {
        var savedTheme = localStorage.getItem('theme') || 'white';
        var options = document.querySelectorAll('.color-option');
        for (var i = 0; i < options.length; i++) {
            if (options[i].getAttribute('data-theme') === savedTheme) {
                options[i].classList.add('active');
            }
        }
        measurePing();
        setInterval(measurePing, 5000);
    });
</script>
"""


HEADER_HTML = """
<header>
    <div class="header-inner">
        <div class="menu-wrapper">
            <button class="menu-btn" id="menuBtn" onclick="toggleMenu()" title="منو">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <div class="dropdown-menu" id="dropdownMenu">
                <a href="/">خانه</a>
                <a href="/about">درباره من</a>
                <a href="/portfolio">نمونه‌کارها</a>
                <a href="/contact">تماس با من</a>
                <a href="/chat">چت با من</a>
            </div>
        </div>
        <div class="greeting">سلام خوش اومدی</div>
        <div class="header-right">
            <div class="ping-box">
                <span class="ping-dot" id="pingDot"></span>
                <span id="pingValue">-- ms</span>
            </div>
            <div class="theme-wrapper">
                <button class="theme-btn" id="themeBtn" onclick="toggleThemePanel()" title="تغییر تم">🎨</button>
                <div class="theme-panel" id="themePanel">
                    <p>انتخاب تم</p>
                    <div class="color-options">
                        <div class="color-option" data-theme="white" onclick="setTheme('white')" style="background: #ffffff; border: 2px solid #ddd;" title="سفید"></div>
                        <div class="color-option" data-theme="black" onclick="setTheme('black')" style="background: #1a1a1a;" title="مشکی"></div>
                        <div class="color-option" data-theme="yellow" onclick="setTheme('yellow')" style="background: #f9d423;" title="زرد"></div>
                        <div class="color-option" data-theme="cream" onclick="setTheme('cream')" style="background: #e8d5b7;" title="کرم"></div>
                        <div class="color-option" data-theme="purple" onclick="setTheme('purple')" style="background: #7c3aed;" title="بنفش"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>

<a href="/contact" class="contact-float" title="ارتباط با من">💬</a>
"""


def page_template(title, body_content, extra_head=""):
    count = get_visit_count()
    footer = ""
    html = "<!DOCTYPE html>\n"
    html += '<html lang="fa" dir="rtl">\n'
    html += "<head>\n"
    html += '<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    html += "<title>" + title + "</title>\n"
    html += CSS
    html += extra_head
    html += JS_SCRIPT
    html += "</head>\n"
    html += "<body>\n"
    html += HEADER_HTML
    html += body_content
    html += footer
    html += "\n</body>\n</html>"
    return html


@app.route("/ping")
def ping():
    return jsonify({"ok": True})


@app.route("/")
def home():
    count = increment_visit()
    body = '<div class="container"><div class="card"><div class="emoji">👋</div><h1>سلام! خوش اومدی</h1><p>این اولین وب‌سایت منه که با پایتون و Flask ساختم.</p><a href="/portfolio" class="btn">نمونه‌کارهام رو ببین</a></div><div class="stats"><div class="stat-card"><div class="stat-number">' + str(count) + '</div><div class="stat-label">بازدید کل</div></div><div class="stat-card"><div class="stat-number">4</div><div class="stat-label">صفحه سایت</div></div><div class="stat-card"><div class="stat-number">24/7</div><div class="stat-label">آنلاین</div></div></div></div>'
    return page_template("سایت من", body)


@app.route("/about")
def about():
    body = '<div class="container"><div class="card"><div class="emoji">🚀</div><h1>درباره من</h1><p>من دارم پایتون یاد می‌گیرم و این اولین وب‌سایتمه.</p><a href="/" class="btn">برگرد به خانه</a></div></div>'
    return page_template("درباره من", body)


@app.route("/portfolio")
def portfolio():
    projects = [
        {"emoji": "🤖", "title": "ربات تلگرام", "desc": "یه ربات که با پایتون ساختم.", "tech": "Python - pyTelegramBotAPI", "link": "#"},
        {"emoji": "🌐", "title": "وب‌سایت شخصی", "desc": "همین سایتی که داری می‌بینی.", "tech": "Python - Flask", "link": "/"},
        {"emoji": "🎨", "title": "پنج تم رنگی", "desc": "پنج تا تم برای سایت.", "tech": "JavaScript - CSS", "link": "/"},
        {"emoji": "📩", "title": "فرم تماس", "desc": "پیام‌ها مستقیم به ربات می‌رسه.", "tech": "Flask - Telegram API", "link": "/contact"},
    ]
    cards = ""
    for i, p in enumerate(projects):
        cards += '<a href="' + p["link"] + '" class="project-card" style="animation-delay: ' + str(i * 0.15) + 's;"><div class="project-emoji">' + p["emoji"] + '</div><h2>' + p["title"] + '</h2><p>' + p["desc"] + '</p><div class="project-tech">' + p["tech"] + '</div></a>'
    body = '<div class="container"><h1 style="text-align:center; color: var(--heading-color); margin-bottom: 10px;">نمونه‌کارهای من</h1><div class="projects-grid">' + cards + '</div></div>'
    return page_template("نمونه‌کارها", body, EXTRA_CSS_PORTFOLIO)


@app.route("/contact")
def contact():
    body = '<div class="container"><div class="card"><div class="emoji">💌</div><h1>تماس با من</h1><p>هر پیامی داری، اینجا بنویس.</p><form method="POST" action="/contact"><div><label>اسمت:</label><input type="text" name="name" required></div><div><label>ایمیلت:</label><input type="email" name="email" required></div><div><label>پیامت:</label><textarea name="message" required></textarea></div><button type="submit" class="btn">ارسال پیام</button></form></div></div>'
    return page_template("تماس با من", body)


@app.route("/contact", methods=["POST"])
def contact_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not email or not message:
        return redirect("/contact")
    send_to_telegram(name, email, message)
    body = '<div class="container"><div class="card"><div class="emoji">✅</div><h1>پیامت ارسال شد!</h1><p>ممنون ' + name + ' جان.</p><a href="/" class="btn">برگرد به خانه</a></div></div>'
    return page_template("ارسال شد", body)


@app.route("/chat")
def chat():
    body = '<div class="container"><div class="card"><div class="emoji">💬</div><h1>چت با من</h1><p>این بخش فعلاً در دست ساخته. از فرم تماس استفاده کن.</p><a href="/contact" class="btn">برو به فرم تماس</a></div></div>'
    return page_template("چت", body)


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)