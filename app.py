import os
import urllib.request
import urllib.parse
from flask import Flask, request, redirect

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")

CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(118, 75, 162, 0.7); }
        50% { box-shadow: 0 0 0 15px rgba(118, 75, 162, 0); }
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    body {
        font-family: Tahoma, sans-serif;
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        color: #333;
    }
    
    header {
        background: rgba(255, 255, 255, 0.95);
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
        color: #764ba2;
        transition: transform 0.3s;
    }
    
    .logo:hover {
        transform: scale(1.1);
    }
    
    nav a {
        color: #764ba2;
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
    
    nav a:hover::after {
        width: 100%;
    }
    
    nav a:hover {
        color: #667eea;
    }
    
    .container {
        max-width: 900px;
        margin: 60px auto;
        padding: 0 20px;
    }
    
    .card {
        background: #fff;
        padding: 50px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
        animation: fadeInUp 0.8s ease;
        transition: transform 0.3s, box-shadow 0.3s;
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
        color: #764ba2;
        font-size: 34px;
        margin-bottom: 20px;
        animation: fadeInUp 1s ease;
    }
    
    p {
        font-size: 18px;
        line-height: 1.8;
        color: #555;
        margin-bottom: 30px;
        animation: fadeInUp 1.2s ease;
    }
    
    .typing {
        display: inline-block;
        border-left: 3px solid #764ba2;
        padding-left: 5px;
        animation: blink 1s step-end infinite;
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
    
    .btn:active {
        transform: translateY(0) scale(0.98);
    }
    
    form {
        display: flex;
        flex-direction: column;
        gap: 15px;
        text-align: right;
    }
    
    label {
        font-size: 16px;
        color: #555;
        margin-bottom: 5px;
        display: block;
    }
    
    input, textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        outline: none;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    
    input:focus, textarea:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.15);
    }
    
    textarea {
        resize: vertical;
        min-height: 120px;
    }
    
    footer {
        text-align: center;
        padding: 30px;
        color: #fff;
        margin-top: 40px;
        font-size: 15px;
        animation: fadeInUp 1.5s ease;
    }
    
    .heart {
        display: inline-block;
        animation: bounce 1s infinite;
    }
    
    .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    
    .stat-card {
        background: #f8f9ff;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        transition: transform 0.3s, background 0.3s;
        animation: fadeInUp 0.8s ease backwards;
    }
    
    .stat-card:nth-child(1) { animation-delay: 0.2s; }
    .stat-card:nth-child(2) { animation-delay: 0.4s; }
    .stat-card:nth-child(3) { animation-delay: 0.6s; }
    
    .stat-card:hover {
        transform: translateY(-8px);
        background: #eef2ff;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: #764ba2;
        margin-bottom: 10px;
    }
    
    .stat-label {
        font-size: 15px;
        color: #777;
    }
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

def header_html():
    return """
    <header>
        <nav>
            <div class="logo">سایت من</div>
            <div>
                <a href="/">خانه</a>
                <a href="/about">درباره من</a>
                <a href="/contact">تماس با من</a>
            </div>
        </nav>
    </header>
    """

def footer_html():
    return '<footer>ساخته‌شده با <span class="heart">❤️</span> و پایتون</footer>'

@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>سایت من</title>
        {CSS}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">👋</div>
                <h1>سلام! خوش اومدی</h1>
                <p>این اولین وب‌سایت منه که با پایتون و Flask ساختم. دارم کم‌کم یاد می‌گیرم چطور وب‌سایت بسازم و این تازه شروع کارمه.</p>
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
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="card">
                <div class="emoji">✅</div>
                <h1>پیامت ارسال شد!</h1>
                <p>ممنون {name} جان. پیامت به دستم رسید. به زودی جواب می‌دم.</p>
                <a href="/" class="btn">برگرد به خانه</a>
            </div>
        </div>
        {footer_html()}
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)