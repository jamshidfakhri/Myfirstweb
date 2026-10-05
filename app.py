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

# آدرس مرکز — این رو با آدرس واقعی عوض کن
CENTER_ADDRESS = "تهران، خیابان انقلاب، خیابان دانشگاه، پلاک ۱۲۳"
CENTER_LAT = "35.7000"
CENTER_LNG = "51.4000"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age TEXT, grade TEXT, phone TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
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


def logged_in():
    return session.get("logged", False)


def render_page(title, content):
    return render_template("page.html", title=title, content=content)


FAQ_ITEMS = [
    ("شهریه چقدر است؟", "شهریه بر اساس نوع اتاق و مدت اقامت متفاوت است. برای اطلاع از قیمت دقیق، با ما تماس بگیرید یا فرم ثبت‌نام را پر کنید."),
    ("ساعت ورود و خروج چگونه است؟", "پذیرش دانش‌آموزان روزهای شنبه تا چهارشنبه از ساعت ۱۴ تا ۲۰ است."),
    ("آیا وعده‌های غذایی شامل شهریه می‌شود؟", "بله، سه وعده‌ی غذایی به همراه میان‌وعده زیر نظر متخصص تغذیه ارائه می‌شود."),
    ("اتاق‌ها چند نفره هستند؟", "اتاق‌ها به دو صورت دو نفره و چهار نفره موجود هستند."),
    ("آیا اینترنت و فضای مطالعه وجود دارد؟", "بله، اینترنت پرسرعت و سالن‌های مطالعه‌ی مجهز در اختیار دانش‌آموزان قرار می‌گیرد."),
    ("اگر دانش‌آموز مریض شود چه می‌شود؟", "بلافاصله به والدین اطلاع داده می‌شود و در صورت نیاز به پزشک ارجاع داده خواهد شد."),
    ("آیا امکان بازدید از مرکز وجود دارد؟", "بله، والدین می‌توانند با هماهنگی قبلی از مرکز بازدید کنند."),
    ("چه مدارکی برای ثبت‌نام لازم است؟", "کپی شناسنامه، کارت ملی والدین، دو قطعه عکس و آخرین کارنامه‌ی تحصیلی."),
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
    html += "<a href='/location' class='btn ghost'>آدرس ما</a>"
    html += "</div>"
    return html


def build_location_html():
    # نقشه با OpenStreetMap (بدون API Key)
    osm_embed = (
        "https://www.openstreetmap.org/export/embed.html?"
        "bbox=" + str(float(CENTER_LNG) - 0.008) + "," + str(float(CENTER_LAT) - 0.005) + "," +
        str(float(CENTER_LNG) + 0.008) + "," + str(float(CENTER_LAT) + 0.005) +
        "&layer=mapnik&marker=" + CENTER_LAT + "," + CENTER_LNG
    )

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

    html += "<p style='font-weight:700;color:var(--brass);margin-bottom:10px;'>🧭 مسیریابی با:</p>"
    html += "<div style='display:flex;gap:8px;flex-wrap:wrap;'>"
    html += "<a href='" + neshan_url + "' target='_blank' class='btn'>نشان</a>"
    html += "<a href='" + balad_url + "' target='_blank' class='btn ghost'>بلد</a>"
    html += "</div>"
    html += "</div>"

    html += "<div style='margin-top:20px;padding:20px;border:1px solid var(--line);'>"
    html += "<p style='font-weight:700;color:var(--brass);margin-bottom:12px;'>🚇 دسترسی:</p>"
    html += "<ul style='padding-right:20px;line-height:2.2;'>"
    html += "<li>نزدیک‌ترین ایستگاه مترو: [نام ایستگاه] — ۵ دقیقه پیاده</li>"
    html += "<li>ایستگاه اتوبوس: [نام ایستگاه] — ۲ دقیقه پیاده</li>"
    html += "<li>پارکینگ: موجود در محل</li>"
    html += "</ul>"
    html += "</div>"

    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/register' class='btn'>ثبت‌نام</a> "
    html += "<a href='/contact' class='btn ghost'>تماس با ما</a>"
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
    html += "<p>📞 تلفن: <a href='tel:+989931783620'>۰۹۹۳۱۷۸۳۶۲۰</a></p>"
    html += "<p>✉️ ایمیل: <a href='mailto:cady1max1@gmail.com'>cady1max1@gmail.com</a></p>"
    html += "<p>📍 آدرس: " + CENTER_ADDRESS + "</p>"
    html += "<p>🕐 شنبه تا پنجشنبه، ۹ صبح تا ۶ عصر</p>"
    html += "</div>"
    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/location' class='btn'>مشاهده روی نقشه</a> "
    html += "<a href='/register' class='btn ghost'>ثبت‌نام</a>"
    html += "</div>"
    return render_page("تماس با ما", html)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        grade = request.form.get("grade", "").strip()
        phone = request.form.get("phone", "").strip()
        notes = request.form.get("notes", "").strip()

        if not name or not age or not grade or not phone:
            return render_page("خطا", "<h1>خطا</h1><p>لطفاً فیلدهای ضروری را پر کنید.</p><p><a href='/register'>برگرد</a></p>")

        save_registration(name, age, grade, phone, notes)

        msg = "ثبت‌نام جدید در سایت\n\n"
        msg += "نام: " + name + "\n"
        msg += "سن: " + age + "\n"
        msg += "پایه: " + grade + "\n"
        msg += "تلفن: " + phone
        if notes:
            msg += "\nتوضیحات: " + notes

        send_to_telegram(msg)
        send_email("ثبت‌نام جدید: " + name, msg)

        return render_page("ثبت‌نام موفق", "<h1>ثبت‌نام انجام شد ✅</h1><p>ممنون " + name + " عزیز! به زودی با شما تماس می‌گیریم.</p><p><a href='/'>برگرد به خانه</a></p>")

    form = "<h1>فرم ثبت‌نام</h1>"
    form += "<p class='muted'>لطفاً اطلاعات زیر را کامل کنید.</p>"
    form += "<form method='POST' style='margin-top:20px;'>"
    form += "<label>نام و نام خانوادگی دانش‌آموز *</label><input name='name' required>"
    form += "<label>سن *</label><input name='age' type='number' min='8' max='25' required>"
    form += "<label>پایه‌ی تحصیلی *</label><input name='grade' placeholder='مثلاً: دهم' required>"
    form += "<label>شماره تلفن والدین *</label><input name='phone' type='tel' required>"
    form += "<label>توضیحات (اختیاری)</label><textarea name='notes'></textarea>"
    form += "<button type='submit' class='btn'>ارسال فرم</button>"
    form += "</form>"
    return render_page("ثبت‌نام", form)


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
        return render_page("پیدا نشد", "<h1>پست پیدا نشد</h1><p><a href='/blog'>برگرد</a></p>"), 404
    html = "<h1>" + p[1] + "</h1><p class='muted'><a href='/blog'>← برگرد به وبلاگ</a></p><hr><p>" + p[2] + "</p>"
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
    html = "<h1>مدیریت</h1><p><a href='/admin/posts/new'>➕ پست جدید</a> | <a href='/admin/registrations'>📋 ثبت‌نام‌ها</a> | <a href='/admin/logout'>خروج</a></p><hr>"
    if not posts:
        html += "<p class='muted'>هنوز پستی نیست.</p>"
    for p in posts:
        html += "<div class='post'><b>" + p[1] + "</b> | <a href='/admin/posts/" + str(p[0]) + "/edit'>ویرایش</a></div>"
    return render_page("مدیریت", html)


@app.route("/admin/registrations")
def admin_registrations():
    if not logged_in():
        return redirect("/admin/login")
    regs = get_all_registrations()
    html = "<h1>ثبت‌نام‌ها</h1><p><a href='/admin/posts'>← برگرد</a></p><hr>"
    if not regs:
        html += "<p class='muted'>هنوز ثبت‌نامی نیومده.</p>"
    for r in regs:
        html += "<div class='post'><b>" + r[1] + "</b> (سن: " + r[2] + "، پایه: " + r[3] + ")<br>"
        html += "<span class='muted'>📞 " + r[4] + "</span><br>"
        if r[5]:
            html += "<span class='muted'>" + r[5] + "</span><br>"
        html += "<span class='muted'>" + str(r[6]) + "</span>"
        html += "<form method='POST' action='/admin/registrations/" + str(r[0]) + "/delete' style='margin-top:8px;'><button type='submit' class='btn' style='padding:5px 15px;font-size:.85rem;'>حذف</button></form>"
        html += "</div>"
    return render_page("ثبت‌نام‌ها", html)


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