import os
import sqlite3
import urllib.request
import urllib.parse
from flask import Flask, request, redirect

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")

DB_NAME = "visits.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY,
            count INTEGER
        )
    """)
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

CSS = """
<style>
    :root {
        --bg-gradient: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        --card-bg: #ffffff;
        --text-color: #333333;
        --text-secondary: #555555;
        --heading-color: #764ba2;
        --header-bg: rgba(255, 255, 255, 0.95);
        --input-border: #e0e0e0;
        --stat-bg: #f8f9ff;
        --stat-hover: #eef2ff;
    }
    
    [data-theme="dark"] {
        --bg-gradient: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e);
        --card-bg: #1f2937;
        --text-color: #e5e7eb;
        --text-secondary: #9ca3af;
        --heading-color: #a78bfa;
        --header-bg: rgba(31, 41, 55, 0.95);
        --input-border: #374151;
        --stat-bg: #111827;
        --stat-hover: #1f2937;
    }
    
    * { margin: 0; padding: 0; box-sizing: border-box; transition: background-color 0.3s, color 0.3s; }
    
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
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
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
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .logo {
        font-size: 22px;
        font-weight: bold;
        color: var(--heading-color);
        transition: transform 0.3s;
    }
    .logo:hover { transform: scale(1.1); }
    
    .nav-links {
        display: flex;
        align-items: center;
    }
    
    nav a {
        color: var(--heading-color);
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
        position: relative;
        transition: color 0.3s;
    }
    nav a::after {
        content: '';
        position: absolute;
        bottom: -5px;
        right: 0;
        width: 0;
        height: 2px;
        background: #667eea;
        transition: width 0.3s;
    }
    nav a:hover::after { width: 100%; }
    nav a:hover { color: #667eea; }
    
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
        transition: transform 0.3s, background 0.3s;
    }
    .theme-btn:hover {
        transform: rotate(20deg) scale(1.1);
        background: var(--heading-color);
        color: #fff;
    }
    
    .container { max-width: 900px; margin: 60px auto; padding: 0 20px; }
    
    .card {
        background: var(--card-bg);
        padding: 50px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
        animation: fadeInUp 0.8s ease;
        transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }
    
    .emoji {
        font-size: 70px;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 20px;
    }
    
    h1 {
        color: var(--heading-color);
        font-size: 34px;
        margin-bottom: 20px;
        animation: fadeInUp 1s ease;
    }
    
    p {
        font-size: 18px;
        line-height: 1.8;
        color: var(--text-secondary);
        margin-bottom: 30px;
        animation: fadeInUp 1.2s ease;
    }
    
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
        transition: transform 0.3s, box-shadow 0.3s;
        animation: pulse 2s infinite;
    }
    .btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 30px rgba(118, 75, 162, 0.4);
    }
    .btn:active { transform: translateY(0) scale(0.98); }
    
    form { display: flex; flex-direction: column; gap: 15px; text-align: right; }
    
    label {
        font-size: 16px;
        color: var(--text-secondary);
        margin-bottom: 5px;
        display: block;
    }
    
    input, textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid var(--input-border);
        border-radius: 10px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        outline: none;
        background: var(--card-bg);
        color: var(--text-color);
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    input:focus, textarea:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.15);
    }
    textarea { resize: vertical; min-height: 120px; }
    
    footer {
        text-align: center;
        padding: 30px;
        color: #fff;
        margin-top: 40px;
        font-size: 15px;
        animation: fadeInUp 1.5s ease;
    }
    .heart { display: inline-block; animation: bounce 1s infinite; }
    
    .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    
    .stat-card {
        background: var(--stat-bg);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        transition: transform 0.3s, background 0.3s;
        animation: fadeInUp 0.8s ease backwards;
    }
    .stat-card:nth-child(1) { animation-delay: 0.2s; }
    .stat-card:nth-child(2) { animation-delay: 0.4s; }
    .stat-card:nth-child(3) { animation-delay: 0.6s; }
    .stat-card:nth-child(4) { animation-delay: 0.8s; }
    .stat-card:hover {
        transform: translateY(-8px);
        background: var(--stat-hover);
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: var(--heading-color);
        margin-bottom: 10px;
    }
    .stat-label { font-size: 15px; color: var(--text-secondary); }
</style>
"""

def send_to_telegram(name, email, message):
    if not BOT_TOKEN or not ADMIN_ID:
        return False
    text = (
        f"پیام جدید از سایت:\n\n"
        f"اسم: {name}\n"
        f"ایمیل: {email}\n\n"
        f"پیام:\n{message}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": ADMIN_ID,
        "text": text
    }).encode()
    try:
        urllib.request.urlopen(url, data=data)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def theme_script():
    return """
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        })();
        
        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            
            const btn = document.getElementById('themeBtn');
            btn.textContent = next === 'dark' ? '☀️' : '🌙';
        }
        
        window.addEventListener('DOMContentLoaded', function() {
            const current = document.documentElement.getAttribute('data-theme');
            const btn = document.getElementById('themeBtn');
            if (btn) {
                btn.textContent = current === 'dark' ? '☀️' : '🌙';
            }
        });
    </script>
    """

def header_html():
    return f"""
    <header>
        <nav>
            <div class="logo">سایت من</div>
            <div class="nav-links">
                <a href="/">خانه</a>
                <a href="/about">درباره من</a>
                <a href="/contact">تماس با من</a>
                <button class="theme-btn" id="themeBtn" onclick="toggleTheme()" title="تغییر حالت">🌙</button>
            </div>
        </nav>
    </header>
    """

def footer_html():
    count = get_visit_count()
    return f"""
    <footer>
        ساخته‌شده با <span class="heart">❤️</span> و پایتون
        <br>
        <span style="font-size: 13px; opacity: 0.8;">👀 بازدید: {count}</span>
    </footer>
    """

@app.route("/")
def home():
    count = increment_visit()
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>سایت من</title>
        {CSS}
        {theme_script()}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">👋</div>
                <h1>سلام! خوش اومدی</h1>
                <p>این اولین وب‌سایت منه که با پایتون و Flask ساختم. دارم کم‌کم یاد می‌گیرم چطور وب‌سایت بسازم.</p>
                <a href="/about" class="btn">درباره من بیشتر بدون</a>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">۳</div>
                    <div class="stat-label">صفحه سایت</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">۲۴/۷</div>
                    <div class="stat-label">آنلاین</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{count}</div>
                    <div class="stat-label">بازدید کل</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">∞</div>
                    <div class="stat-label">انگیزه یادگیری</div>
                </div>
            </div>
        </div>
        {footer_html()}
    </body>
    </html>
    """

@app.route("/about")
def about():
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>درباره من</title>
        {CSS}
        {theme_script()}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">🚀</div>
                <h1>درباره من</h1>
                <p>من دارم پایتون یاد می‌گیرم و این اولین وب‌سایتمه. هدفم اینه که بتونم برنامه‌ها و وب‌سایت‌های واقعی بسازم.</p>
                <a href="/" class="btn">برگرد به خانه</a>
            </div>
        </div>
        {footer_html()}
    </body>
    </html>
    """

@app.route("/contact")
def contact():
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تماس با من</title>
        {CSS}
        {theme_script()}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">💌</div>
                <h1>تماس با من</h1>
                <p>هر پیامی داری، اینجا بنویس. مستقیم به دستم می‌رسه.</p>
                <form method="POST" action="/contact">
                    <div>
                        <label>اسمت:</label>
                        <input type="text" name="name" required>
                    </div>
                    <div>
                        <label>ایمیلت:</label>
                        <input type="email" name="email" required>
                    </div>
                    <div>
                        <label>پیامت:</label>
                        <textarea name="message" required></textarea>
                    </div>
                    <button type="submit" class="btn">ارسال پیام</button>
                </form>
            </div>
        </div>
        {footer_html()}
    </body>
    </html>
    """

@app.route("/contact", methods=["POST"])
def contact_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    
    if not name or not email or not message:
        return redirect("/contact")
    
    send_to_telegram(name, email, message)
    
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ارسال شد</title>
        {CSS}
        {theme_script()}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">✅</div>
                <h1>پیامت ارسال شد!</h1>
                <p>ممنون {name} جان. پیامت به دستم رسید.</p>
                <a href="/" class="btn">برگرد به خانه</a>
            </div>
        </div>
        {footer_html()}
    </body>
    </html>
    """

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)