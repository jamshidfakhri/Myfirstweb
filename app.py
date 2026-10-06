import os
import sqlite3
import smtplib
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from flask import Flask, request, redirect, session, jsonify, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")
DB_NAME = "site_data.db"

CENTER_ADDRESS = "کرمان، خیابان خواجو"
CENTER_LAT = "30.2802837"
CENTER_LNG = "57.0492426"

RUBIKA_USERNAME = "Jamshidfakhrii"
EITAA_USERNAME = "Jamshidfakhrii"
CENTER_PHONE = "09931783620"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age TEXT, grade TEXT, phone TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS consultations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, best_time TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()


def send_email(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not NOTIFY_EMAIL:
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = NOTIFY_EMAIL
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email error: " + str(e))
        return False


def send_to_telegram(text):
    if not BOT_TOKEN or not ADMIN_ID:
        return False
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = urllib.parse.urlencode({"chat_id": ADMIN_ID, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data=data)
        return True
    except Exception as e:
        print("Telegram error: " + str(e))
        return False


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


def save_registration(name, age, grade, phone, notes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO registrations (name, age, grade, phone, notes) VALUES (?, ?, ?, ?, ?)", (name, age, grade, phone, notes))
    conn.commit()
    conn.close()


def get_all_registrations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, age, grade, phone, notes, created_at FROM registrations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def delete_registration(rid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM registrations WHERE id=?", (rid,))
    conn.commit()
    conn.close()


def save_consultation(name, phone, best_time, notes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO consultations (name, phone, best_time, notes) VALUES (?, ?, ?, ?)", (name, phone, best_time, notes))
    conn.commit()
    conn.close()


def get_all_consultations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, best_time, notes, created_at FROM consultations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def delete_consultation(cid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM consultations WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def logged_in():
    return session.get("logged", False)


def render_page(title, content):
    return render_template("page.html", title=title, content=content)


FAQ_ITEMS = [
    ("شهریه چقدر است؟", "شهریه بر اساس نوع اتاق و مدت اقامت متفاوت است."),
    ("ساعت ورود و خروج چگونه است؟", "پذیرش دانش‌آموزان روزهای شنبه تا چهارشنبه از ساعت ۱۴ تا ۲۰ است."),
    ("آیا وعده‌های غذایی شامل شهریه می‌شود؟", "بله، سه وعده‌ی غذایی به همراه میان‌وعده ارائه می‌شود."),
    ("اتاق‌ها چند نفره هستند؟", "اتاق‌ها دو نفره و چهار نفره موجود هستند."),
    ("آیا اینترنت و فضای مطالعه وجود دارد؟", "بله، اینترنت پرسرعت و سالن‌های مطالعه‌ی مجهز موجود است."),
    ("اگر دانش‌آموز مریض شود چه می‌شود؟", "بلافاصله به والدین اطلاع داده می‌شود و به پزشک ارجاع داده می‌شود."),
    ("آیا امکان بازدید از مرکز وجود دارد؟", "بله، والدین می‌توانند با هماهنگی قبلی بازدید کنند."),
    ("چه مدارکی برای ثبت‌نام لازم است؟", "کپی شناسنامه، کارت ملی والدین، دو قطعه عکس و آخرین کارنامه."),
]


def build_faq_html():
    html = "<h1>سوالات متداول</h1>"
    html += "<p class='muted'>پاسخ سوالات رایج درباره‌ی مرکز مطالعه.</p>"
    html += "<div style='margin-top:24px;'>"
    for q, a in FAQ_ITEMS:
        html += "<details style='border:1px solid var(--line);padding:14px 18px;margin-bottom:8px;background:var(--card);'>"
        html += "<summary style='cursor:pointer;font-weight:700;color:var(--brass);list-style:none;'>" + q + "</summary>"
        html += "<p style='margin-top:12px;line-height:2;'>" + a + "</p>"
        html += "</details>"
    html += "</div>"
    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/register' class='btn'>ثبت‌نام</a> "
    html += "<a href='/consultation' class='btn ghost'>مشاوره‌ی رایگان</a>"
    html += "</div>"
    return html


def build_location_html():
    lat = float(CENTER_LAT)
    lng = float(CENTER_LNG)
    osm_embed = ("https://www.openstreetmap.org/export/embed.html?bbox="
                 + str(lng - 0.008) + "," + str(lat - 0.005) + ","
                 + str(lng + 0.008) + "," + str(lat + 0.005)
                 + "&layer=mapnik&marker=" + CENTER_LAT + "," + CENTER_LNG)
    neshan_url = "https://neshan.org/maps/@" + CENTER_LAT + "," + CENTER_LNG + ",16z"
    balad_url = "https://balad.ir/location?latitude=" + CENTER_LAT + "&longitude=" + CENTER_LNG + "&zoom=16"
    html = "<h1>آدرس و لوکیشن</h1>"
    html += "<p class='muted'>برای بازدید حضوری، از آدرس زیر استفاده کنید.</p>"
    html += "<div style='margin-top:24px;border:1px solid var(--line);background:var(--card);'>"
    html += "<iframe src='" + osm_embed + "' style='width:100%;height:380px;border:0;display:block;' loading='lazy'></iframe>"
    html += "</div>"
    html += "<div style='margin-top:20px;padding:20px;border:1px solid var(--line);background:var(--cream);'>"
    html += "<p style='font-weight:700;color:var(--brass);margin-bottom:10px;'>📍 آدرس:</p>"
    html += "<p style='margin-bottom:16px;'>" + CENTER_ADDRESS + "</p>"
    html += "<div style='display:flex;gap:8px;flex-wrap:wrap;'>"
    html += "<a href='" + neshan_url + "' target='_blank' class='btn'>نشان</a>"
    html += "<a href='" + balad_url + "' target='_blank' class='btn ghost'>بلد</a>"
    html += "</div>"
    html += "</div>"
    return html


@app.route("/ping")
def ping():
    return jsonify({"ok": True})


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/faq")
def faq():
    return render_page("سوالات متداول", build_faq_html())


@app.route("/location")
def location():
    return render_page("آدرس و لوکیشن", build_location_html())


@app.route("/contact")
def contact():
    html = "<h1>تماس با ما</h1>"
    html += "<p class='muted'>از راه‌های زیر با ما در ارتباط باشید.</p>"
    html += "<div style='margin-top:24px;line-height:2.4;'>"
    html += "<p>📞 تلفن: <a href='tel:+98" + CENTER_PHONE[1:] + "'>۰۹۹۳۱۷۸۳۶۲۰</a></p>"
    html += "<p>✉️ ایمیل: <a href='mailto:cady1max1@gmail.com'>cady1max1@gmail.com</a></p>"
    html += "<p>📍 آدرس: " + CENTER_ADDRESS + "</p>"
    html += "<p>🕐 شنبه تا پنجشنبه، ۹ صبح تا ۶ عصر</p>"
    html += "<p>💬 روبیکا: <a href='https://rubika.ir/" + RUBIKA_USERNAME + "'>@" + RUBIKA_USERNAME + "</a></p>"
    html += "<p>💬 ایتا: <a href='https://eitaa.com/" + EITAA_USERNAME + "'>@" + EITAA_USERNAME + "</a></p>"
    html += "</div>"
    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/consultation' class='btn'>مشاوره‌ی رایگان</a> "
    html += "<a href='/location' class='btn ghost'>آدرس روی نقشه</a>"
    html += "</div>"
    return render_page("تماس با ما", html)


@app.route("/consultation", methods=["GET", "POST"])
def consultation():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        best_time = request.form.get("best_time", "").strip()
        notes = request.form.get("notes", "").strip()
        if not name or not phone:
            return render_page("خطا", "<h1>خطا</h1><p>لطفاً نام و شماره تماس را وارد کنید.</p><p><a href='/consultation'>برگرد</a></p>")
        save_consultation(name, phone, best_time, notes)
        msg = "🔔 درخواست مشاوره‌ی رایگان\n\n"
        msg += "نام: " + name + "\n"
        msg += "شماره: " + phone + "\n"
        msg += "ساعت مناسب: " + (best_time if best_time else "فرقی نمی‌کنه")
        if notes:
            msg += "\nتوضیحات: " + notes
        send_to_telegram(msg)
        send_email("درخواست مشاوره: " + name, msg)
        return render_page("ثبت شد", "<h1>درخواستت ثبت شد ✅</h1><p>ممنون " + name + " عزیز! در اولین فرصت با شما تماس می‌گیریم.</p><p><a href='/'>برگرد به خانه</a></p>")
    form = "<h1>مشاوره‌ی رایگان</h1>"
    form += "<p class='muted'>اطلاعاتت رو وارد کن، کارشناسان ما در سریع‌ترین زمان با شما تماس می‌گیرن.</p>"
    form += "<form method='POST' style='margin-top:20px;'>"
    form += "<label>نام و نام خانوادگی *</label><input name='name' required>"
    form += "<label>شماره تماس *</label><input name='phone' type='tel' required>"
    form += "<label>چه ساعتی تماس بگیریم؟</label>"
    form += "<select name='best_time' style='width:100%;padding:13px 16px;border:2px solid var(--line);border-radius:10px;font-size:16px;font-family:inherit;margin-bottom:15px;background:var(--card);color:var(--ink);'>"
    form += "<option>صبح (۹ تا ۱۲)</option>"
    form += "<option>بعدازظهر (۱۲ تا ۱۷)</option>"
    form += "<option>عصر (۱۷ تا ۲۱)</option>"
    form += "<option>فرقی نمی‌کنه</option>"
    form += "</select>"
    form += "<label>توضیحات (اختیاری)</label><textarea name='notes'></textarea>"
    form += "<button type='submit' class='btn'>درخواست مشاوره</button>"
    form += "</form>"
    form += "<div style='margin-top:30px;padding-top:24px;border-top:1px solid var(--line);text-align:center;'>"
    form += "<p class='muted' style='margin-bottom:16px;'>یا مستقیم پیام بده:</p>"
    form += "<a href='https://rubika.ir/" + RUBIKA_USERNAME + "' class='btn'>💬 روبیکا</a> "
    form += "<a href='https://eitaa.com/" + EITAA_USERNAME + "' class='btn ghost'>💬 ایتا</a>"
    form += "</div>"
    return render_page("مشاوره‌ی رایگان", form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        grade = request.form.get("grade", "").strip()
        phone = request.form.get("phone", "").strip()
        notes = request.form.get("notes", "").strip()
        if not name or not age or not grade or not phone:
            return render_page("خطا", "<h1>خطا</h1><p>لطفاً همه‌ی فیلدها را پر کنید.</p><p><a href='/register'>برگرد</a></p>")
        save_registration(name, age, grade, phone, notes)
        msg = "ثبت‌نام جدید\n\nنام: " + name + "\nسن: " + age + "\nپایه: " + grade + "\nتلفن: " + phone
        if notes:
            msg += "\nتوضیحات: " + notes
        send_to_telegram(msg)
        send_email("ثبت‌نام جدید: " + name, msg)
        return render_page("ثبت‌نام موفق", "<h1>ثبت‌نام انجام شد ✅</h1><p>ممنون " + name + " عزیز!</p><p><a href='/'>برگرد</a></p>")
    form = "<h1>فرم ثبت‌نام</h1>"
    form += "<form method='POST' style='margin-top:20px;'>"
    form += "<label>نام دانش‌آموز *</label><input name='name' required>"
    form += "<label>سن *</label><input name='age' type='number' required>"
    form += "<label>پایه‌ی تحصیلی *</label><input name='grade' required>"
    form += "<label>شماره تلفن والدین *</label><input name='phone' type='tel' required>"
    form += "<label>توضیحات</label><textarea name='notes'></textarea>"
    form += "<button type='submit' class='btn'>ارسال</button>"
    form += "</form>"
    return render_page("ثبت‌نام", form)


@app.route("/blog")
def blog():
    posts = get_all_posts()
    html = "<h1>وبلاگ</h1>"
    if not posts:
        html += "<p class='muted'>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div class='post'><h2><a href='/blog/" + str(p[0]) + "'>" + p[1] + "</a></h2><p class='muted'>" + p[2][:150] + "...</p></div>"
    return render_page("وبلاگ", html)


@app.route("/blog/<int:pid>")
def blog_post(pid):
    p = get_post(pid)
    if not p:
        return render_page("پیدا نشد", "<h1>پیدا نشد</h1><p><a href='/blog'>برگرد</a></p>"), 404
    html = "<h1>" + p[1] + "</h1><p class='muted'><a href='/blog'>← برگرد</a></p><hr><p>" + p[2] + "</p>"
    return render_page(p[1], html)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return render_page("خطا", "<h1>رمز اشتباهه</h1><p><a href='/admin/login'>دوباره</a></p>")
    html = "<h1>ورود مدیریت</h1><form method='POST'><input type='password' name='password' placeholder='رمز' required><button type='submit' class='btn'>ورود</button></form>"
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
    html = "<h1>مدیریت</h1><p><a href='/admin/posts/new'>➕ پست جدید</a> | <a href='/admin/registrations'>📋 ثبت‌نام‌ها</a> | <a href='/admin/consultations'>💬 مشاوره‌ها</a> | <a href='/admin/logout'>خروج</a></p><hr>"
    for p in posts:
        html += "<div class='post'><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div>"
    return render_page("مدیریت", html)


@app.route("/admin/registrations")
def admin_registrations():
    if not logged_in():
        return redirect("/admin/login")
    regs = get_all_registrations()
    html = "<h1>ثبت‌نام‌ها</h1><p><a href='/admin/posts'>← برگرد</a></p><hr>"
    for r in regs:
        html += "<div class='post'><b>" + r[1] + "</b> (سن: " + r[2] + "، پایه: " + r[3] + ")<br>"
        html += "<span class='muted'>📞 " + r[4] + "</span><br>"
        if r[5]:
            html += "<span class='muted'>" + r[5] + "</span><br>"
        html += "<span class='muted'>" + str(r[6]) + "</span>"
        html += "<form method='POST' action='/admin/registrations/" + str(r[0]) + "/delete' style='margin-top:8px;'><button type='submit' class='btn' style='padding:5px 15px;font-size:.85rem;'>حذف</button></form>"
        html += "</div>"
    return render_page("ثبت‌نام‌ها", html)


@app.route("/admin/consultations")
def admin_consultations():
    if not logged_in():
        return redirect("/admin/login")
    items = get_all_consultations()
    html = "<h1>درخواست‌های مشاوره</h1><p><a href='/admin/posts'>← برگرد</a></p><hr>"
    if not items:
        html += "<p class='muted'>هنوز درخواستی نیومده.</p>"
    for r in items:
        html += "<div class='post'><b>" + r[1] + "</b><br>"
        html += "<span class='muted'>📞 " + r[2] + "</span><br>"
        html += "<span class='muted'>🕐 " + (r[3] if r[3] else "—") + "</span><br>"
        if r[4]:
            html += "<span class='muted'>💬 " + r[4] + "</span><br>"
        html += "<span class='muted'>" + str(r[5]) + "</span>"
        html += "<form method='POST' action='/admin/consultations/" + str(r[0]) + "/delete' style='margin-top:8px;'><button type='submit' class='btn' style='padding:5px 15px;font-size:.85rem;'>حذف</button></form>"
        html += "</div>"
    return render_page("مشاوره‌ها", html)


@app.route("/admin/consultations/<int:cid>/delete", methods=["POST"])
def admin_delete_consultation(cid):
    if not logged_in():
        return redirect("/admin/login")
    delete_consultation(cid)
    return redirect("/admin/consultations")


@app.route("/admin/registrations/<int:rid>/delete", methods=["POST"])
def admin_delete_registration(rid):
    if not logged_in():
        return redirect("/admin/login")
    delete_registration(rid)
    return redirect("/admin/registrations")


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
    html = "<h1>پست جدید</h1><form method='POST'><input name='title' placeholder='عنوان' required><textarea name='content' placeholder='متن' required></textarea><button type='submit' class='btn'>ذخیره</button></form>"
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
    html = "<h1>ویرایش</h1><form method='POST'><input name='title' value='" + p[1] + "' required><textarea name='content' required>" + p[2] + "</textarea><button type='submit' class='btn'>ذخیره</button></form>"
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