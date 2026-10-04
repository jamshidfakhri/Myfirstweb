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
    body {
        font-family: Tahoma, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        color: #333;
    }
    header {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 900px;
        margin: 0 auto;
    }
    .logo { font-size: 22px; font-weight: bold; color: #764ba2; }
    nav a {
        color: #764ba2;
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
    }
    nav a:hover { color: #667eea; }
    .container { max-width: 900px; margin: 60px auto; padding: 0 20px; }
    .card {
        background: #fff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        text-align: center;
    }
    h1 { color: #764ba2; font-size: 32px; margin-bottom: 20px; }
    p { font-size: 18px; line-height: 1.8; color: #555; margin-bottom: 30px; }
    .btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        padding: 14px 30px;
        border-radius: 30px;
        text-decoration: none;
        font-size: 16px;
        border: none;
        cursor: pointer;
        font-family: Tahoma, sans-serif;
    }
    form { display: flex; flex-direction: column; gap: 15px; text-align: right; }
    label { font-size: 16px; color: #555; margin-bottom: 5px; display: block; }
    input, textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        font-size: 16px;
        font-family: Tahoma, sans-serif;
        outline: none;
    }
    input:focus, textarea:focus { border-color: #764ba2; }
    textarea { resize: vertical; min-height: 120px; }
    footer { text-align: center; padding: 20px; color: #fff; margin-top: 40px; }
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
    return "<footer>ساخته‌شده با پایتون</footer>"

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
                <h1>سلام! خوش اومدی</h1>
                <p>این اولین وب‌سایت منه که با پایتون و Flask ساختم.</p>
                <a href="/about" class="btn">درباره من بیشتر بدون</a>
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
                <h1>درباره من</h1>
                <p>من دارم پایتون یاد می‌گیرم و این اولین وب‌سایتمه.</p>
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
                <h1>تماس با من</h1>
                <p>هر پیامی داری، اینجا بنویس.</p>
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
                <h1>پیامت ارسال شد!</h1>
                <p>ممنون {name} جان. پیامت به دستم رسید.</p>
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
