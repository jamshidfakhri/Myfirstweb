import os
import sqlite3
import urllib.request
import urllib.parse
import uuid
from flask import Flask, request, redirect, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
SITE_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

DB_NAME = "site_data.db"

# ---------------- دیتابیس ----------------
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            sender TEXT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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

def save_message(conversation_id, sender, text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, text) VALUES (?, ?, ?)",
        (conversation_id, sender, text)
    )
    conn.commit()
    conn.close()

def get_messages(conversation_id, after_id=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, sender, text FROM messages WHERE conversation_id = ? AND id > ? ORDER BY id",
        (conversation_id, after_id)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "sender": r[1], "text": r[2]} for r in rows]

# ---------------- ارسال به تلگرام ----------------
def notify_admin(conversation_id, text):
    if not BOT_TOKEN or not ADMIN_ID:
        return False
    
    msg = (
        f"پیام جدید از سایت\n\n"
        f"شناسه گفتگو: {conversation_id}\n\n"
        f"پیام:\n{text}\n\n"
        f"برای پاسخ، روی همین پیام Reply بزن."
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": ADMIN_ID,
        "text": msg
    }).encode()
    
    try:
        urllib.request.urlopen(url, data=data)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# ---------------- CSS ----------------
CSS = """
<style>
    :root {
        --bg-gradient: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        --card-bg: #ffffff;
        --text-color: #333333;
        --heading-color: #764ba2;
        --header-bg: rgba(255, 255, 255, 0.95);
    }
    [data-theme="dark"] {
        --bg-gradient: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e);
        --card-bg: #1f2937;
        --text-color: #e5e7eb;
        --heading-color: #a78bfa;
        --header-bg: rgba(31, 41, 55, 0.95);
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
    }
    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 900px;
        margin: 0 auto;
    }
    .logo { font-size: 22px; font-weight: bold; color: var(--heading-color); }
    nav a {
        color: var(--heading-color);
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
    }
    .theme-btn {
        background: transparent;
        border: 2px solid var(--heading-color);
        color: var(--heading-color);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
    }
    .container { max-width: 700px; margin: 40px auto; padding: 0 20px; }
    .chat-box {
        background: var(--card-bg);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 70vh;
    }
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        padding: 20px;
        text-align: center;
    }
    .chat-header h1 { font-size: 20px; }
    .chat-header p { font-size: 13px; opacity: 0.9; margin-top: 5px; }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        background: var(--card-bg);
    }
    .message {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 15px;
        font-size: 15px;
        line-height: 1.6;
        word-wrap: break-word;
        animation: fadeInUp 0.3s ease;
    }
    .message.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
    }
    .message.admin {
        background: #f0f0f5;
        color: #333;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
    }
    [data-theme="dark"] .message.admin {
        background: #374151;
        color: #e5e7eb;
    }
    .message.system {
        background: transparent;
        color: #999;
        text-align: center;
        align-self: center;
        font-size: 13px;
        padding: 5px;
    }
    .chat-input {
        display: flex;
        padding: 15px;
        gap: 10px;
        background: var(--card-bg);
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
    .chat-input input {
        flex: 1;
        padding: 12px 18px;
        border: 2px solid #e0e0e0;
        border-radius: 25px;
        font-size: 15px;
        font-family: Tahoma, sans-serif;
        outline: none;
        background: var(--card-bg);
        color: var(--text-color);
    }
    .chat-input input:focus { border-color: #764ba2; }
    .chat-input button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 15px;
        font-family: Tahoma, sans-serif;
    }
    .chat-input button:hover { opacity: 0.9; }
</style>
"""

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
            if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
        }
        window.addEventListener('DOMContentLoaded', function() {
            const current = document.documentElement.getAttribute('data-theme');
            const btn = document.getElementById('themeBtn');
            if (btn) btn.textContent = current === 'dark' ? '☀️' : '🌙';
        });
    </script>
    """

def header_html():
    return """
    <header>
        <nav>
            <div class="logo">سایت من</div>
            <div>
                <a href="/">خانه</a>
                <a href="/chat">چت</a>
                <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">🌙</button>
            </div>
        </nav>
    </header>
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
            <div class="chat-box" style="height:auto; padding: 60px 40px; text-align:center;">
                <div style="font-size: 70px;">👋</div>
                <h1 style="color: var(--heading-color); margin: 20px 0;">سلام! خوش اومدی</h1>
                <p style="margin-bottom: 30px; line-height: 1.8;">این اولین وب‌سایت منه. می‌تونی با من چت کنی!</p>
                <a href="/chat" style="display:inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:#fff; padding: 16px 35px; border-radius: 30px; text-decoration: none; font-size: 16px;">شروع چت</a>
                <p style="margin-top: 30px; font-size: 14px; color: #999;">👀 بازدید: {count}</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>چت با من</title>
        {CSS}
        {theme_script()}
    </head>
    <body>
        {header_html()}
        <div class="container">
            <div class="chat-box">
                <div class="chat-header">
                    <h1>چت با من</h1>
                    <p>پیامت مستقیم به دستم می‌رسه</p>
                </div>
                <div class="chat-messages" id="messages">
                    <div class="message system">گفتگو رو شروع کن...</div>
                </div>
                <div class="chat-input">
                    <input type="text" id="messageInput" placeholder="پیامت رو بنویس..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">ارسال</button>
                </div>
            </div>
        </div>
        
        <script>
            let conversationId = localStorage.getItem('conversationId');
            if (!conversationId) {{
                conversationId = 'conv_' + Math.random().toString(36).substring(2, 15);
                localStorage.setItem('conversationId', conversationId);
            }}
            
            let lastMessageId = 0;
            const messagesDiv = document.getElementById('messages');
            
            function addMessage(sender, text) {{
                const div = document.createElement('div');
                div.className = 'message ' + sender;
                div.textContent = text;
                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }}
            
            async function sendMessage() {{
                const input = document.getElementById('messageInput');
                const text = input.value.trim();
                if (!text) return;
                
                addMessage('user', text);
                input.value = '';
                
                try {{
                    await fetch('/api/send', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            conversation_id: conversationId,
                            text: text
                        }})
                    }});
                }} catch (e) {{
                    addMessage('system', 'خطا در ارسال');
                }}
            }}
            
            async function fetchMessages() {{
                try {{
                    const res = await fetch('/api/messages?conversation_id=' + conversationId + '&after=' + lastMessageId);
                    const data = await res.json();
                    
                    if (data.messages && data.messages.length > 0) {{
                        data.messages.forEach(function(msg) {{
                            if (msg.sender === 'admin') {{
                                addMessage('admin', msg.text);
                            }}
                            lastMessageId = msg.id;
                        }});
                    }}
                }} catch (e) {{}}
            }}
            
            setInterval(fetchMessages, 3000);
            fetchMessages();
        </script>
    </body>
    </html>
    """

# ---------------- API ----------------
@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.get_json()
    conversation_id = data.get("conversation_id", "").strip()
    text = data.get("text", "").strip()
    
    if not conversation_id or not text:
        return jsonify({"ok": False})
    
    save_message(conversation_id, "user", text)
    notify_admin(conversation_id, text)
    
    return jsonify({"ok": True})

@app.route("/api/messages")
def api_messages():
    conversation_id = request.args.get("conversation_id", "")
    after_id = int(request.args.get("after", 0))
    
    if not conversation_id:
        return jsonify({"messages": []})
    
    msgs = get_messages(conversation_id, after_id)
    return jsonify({"messages": msgs})

# ---------------- دریافت پاسخ از ربات ----------------
@app.route("/api/admin_reply", methods=["POST"])
def admin_reply():
    data = request.get_json()
    conversation_id = data.get("conversation_id", "").strip()
    text = data.get("text", "").strip()
    
    if not conversation_id or not text:
        return jsonify({"ok": False})
    
    save_message(conversation_id, "admin", text)
    return jsonify({"ok": True})

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)