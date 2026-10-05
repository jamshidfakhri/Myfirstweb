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


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age TEXT, grade TEXT, phone TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()


def send_email(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not NOTIFY_EMAIL:
        print("Email config missing")
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
    ("شهریه چقدر است؟",
     "شهریه بر اساس نوع اتاق (دو نفره یا چهار نفره) و مدت اقامت (ماهانه یا سالانه) متفاوت است. برای اطلاع از قیمت دقیق، لطفاً با ما تماس بگیرید یا فرم ثبت‌نام را پر کنید."),
    ("ساعت ورود و خروج چگونه است؟",
     "پذیرش دانش‌آموزان روزهای شنبه تا چهارشنبه از ساعت ۱۴ تا ۲۰ است. خروج در پایان هر ماه یا با هماهنگی قبلی امکان‌پذیر است."),
    ("آیا وعده‌های غذایی شامل شهریه می‌شود؟",
     "بله، سه وعده‌ی غذایی (صبحانه، ناهار، شام) به همراه میان‌وعده زیر نظر متخصص تغذیه ارائه می‌شود."),
    ("اتاق‌ها چند نفره هستند؟",
     "اتاق‌ها به دو صورت دو نفره و چهار نفره موجود هستند. هر اتاق دارای سرویس بهداشتی و کولر است."),
    ("آیا اینترنت و فضای مطالعه وجود دارد؟",
     "بله، اینترنت پرسرعت وای‌فای به همراه سالن‌های مطالعه‌ی مجهز و ساکت در اختیار دانش‌آموزان قرار می‌گیرد."),
    ("امکانات ورزشی و تفریحی چیست؟",
     "سالن ورزشی کوچک، زمین بازی و اتاق تلویزیون برای اوقات فراغت دانش‌آموزان در نظر گرفته شده است."),
    ("اگر دانش‌آموز مریض شود چه می‌شود؟",
     "در صورت بیماری، بلافاصله به والدین اطلاع داده می‌شود و در صورت نیاز به پزشک ارجاع داده خواهد شد. هزینه‌ی درمان بر عهده‌ی خانواده است."),
    ("آیا امکان بازدید از مرکز وجود دارد؟",
     "بله، والدین می‌توانند با هماهنگی قبلی از مرکز بازدید کنند و از نزدیک با فضا و امکانات آشنا شوند."),
    ("چه مدارکی برای ثبت‌نام لازم است؟",
     "کپی شناسنامه، کارت ملی والدین، دو قطعه عکس و آخرین کارنامه‌ی تحصیلی. برای ثبت‌نام آنلاین، فرم سایت را پر کنید."),
    ("آیا امکان انصراف و بازگشت وجه وجود دارد؟",
     "در صورت انصراف تا یک هفته پس از ثبت‌نام، شهریه به‌طور کامل بازگردانده می‌شود. پس از آن، بر اساس مدت استفاده محاسبه می‌شود."),
]


def build_faq_html():
    html = "<h1>سوالات متداول</h1>"
    html += "<p class='muted'>پاسخ سوالات رایج درباره‌ی مرکز مطالعه. اگر سوال دیگری دارید، با ما تماس بگیرید.</p>"
    html += "<div style='margin-top:24px;'>"
    for q, a in FAQ_ITEMS:
        html += "<details style='border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-bottom:10px;background:var(--card);'>"
        html += "<summary style='cursor:pointer;font-weight:600;color:var(--brass);list-style:none;'>" + q + "</summary>"
        html += "<p style='margin-top:12px;color:var(--ink);line-height:2;'>" + a + "</p>"
        html += "</details>"
    html += "</div>"
    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/register' class='btn'>فرم ثبت‌نام</a> "
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


@app.route("/contact")
def contact():
    html = "<h1>تماس با ما</h1>"
    html += "<p class='muted'>از راه‌های زیر می‌توانید با ما در ارتباط باشید.</p>"
    html += "<div style='margin-top:24px;'>"
    html += "<p>📞 تلفن: <a href='tel:+989931783620'>۰۹۹۳۱۷۸۳۶۲۰</a></p>"
    html += "<p>✉️ ایمیل: <a href='mailto:cady1max1@gmail.com'>cady1max1@gmail.com</a></p>"
    html += "<p>📍 آدرس: [آدرس خود را اینجا بنویسید]</p>"
    html += "<p>🕐 ساعت پاسخگویی: شنبه تا پنجشنبه، ۹ صبح تا ۶ عصر</p>"
    html += "</div>"
    html += "<div style='margin-top:30px;text-align:center;'>"
    html += "<a href='/register' class='btn'>فرم ثبت‌نام</a>"
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
            return render_page("خطا", "<h1>خطا</h1><p>لطفاً فیلدهای ضروری را پر کنید.</p><p><a href='/register'>برگرد به فرم</a></p>")

        save_registration(name, age, grade, phone, notes)

        msg = "ثبت‌نام جدید در سایت\n\n"
        msg += "نام: " + name + "\n"
        msg += "سن: " + age + "\n"
        msg += "پایه: " + grade + "\n"
        msg += "تلفن: " + phone + "\n"
        if notes:
            msg += "توضیحات: " + notes

        send_to_telegram(msg)
        send_email("ثبت‌نام جدید: " + name, msg)

        return render_page("ثبت‌نام موفق", "<h1>ثبت‌نام انجام شد ✅</h1><p>ممنون " + name + " عزیز! به زودی با شما تماس می‌گیریم.</p><p><a href='/'>برگرد به خانه</a></p>")

    form = "<h1>فرم ثبت‌نام</h1>"
    form += "<p class='muted'>لطفاً اطلاعات زیر را کامل کنید تا با شما تماس بگیریم.</p>"
    form += "<form method='POST'>"
    form += "<label>نام و نام خانوادگی دانش‌آموز *</label>"
    form += "<input name='name' required>"
    form += "<label>سن *</label>"
    form += "<input name='age' type='number' min='8' max='25' required>"
    form += "<label>پایه‌ی تحصیلی *</label>"
    form += "<input name='grade' placeholder='مثلاً: دهم' required>"
    form += "<label>شماره تلفن والدین *</label>"
    form += "<input name='phone' type='tel' required>"
    form += "<label>توضیحات (اختیاری)</label>"
    form += "<textarea name='notes' placeholder='هر توضیحی دارید اینجا بنویسید'></textarea>"
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
        return render_page("پیدا نشد", "<h1>پست پیدا نشد</h1><p><a href='/blog'>برگرد به وبلاگ</a></p>"), 404
    html = "<h1>" + p[1] + "</h1><p class='muted'><a href='/blog'>← برگرد به وبلاگ</a></p><hr><p>" + p[2] + "</p>"
    return render_page(p[1], html)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["logged"] = True
            return redirect("/admin/posts")
        return render_page("خطا", "<h1>رمز اشتباهه</h1><p><a href='/admin/login'>دوباره</a></p>")
    html = "<h1>ورود مدیریت</h1><form method='POST'><input type='password' name='password' placeholder='رمز عبور' required><button type='submit' class='btn'>ورود</button></form>"
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
    html = "<h1>مدیریت پست‌ها</h1><p><a href='/admin/posts/new'>➕ پست جدید</a> | <a href='/admin/registrations'>📋 ثبت‌نام‌ها</a> | <a href='/admin/logout'>خروج</a></p><hr>"
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
    html = "<h1>ثبت‌نام‌های دریافتی</h1><p><a href='/admin/posts'>← برگرد به مدیریت</a></p><hr>"
    if not regs:
        html += "<p class='muted'>هنوز ثبت‌نامی نیومده.</p>"
    for r in regs:
        html += "<div class='post'><b>" + r[1] + "</b> (سن: " + r[2] + "، پایه: " + r[3] + ")<br>"
        html += "<span class='muted'>📞 " + r[4] + "</span><br>"
        if r[5]:
            html += "<span class='muted'>" + r[5] + "</span><br>"
        html += "<span class='muted'>تاریخ: " + str(r[6]) + "</span>"
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
    html = "<h1>پست جدید</h1><form method='POST'><input name='title' placeholder='عنوان' required><textarea name='content' placeholder='متن' required></textarea><button type='submit' class='btn'>ذخیره</button></form><p><a href='/admin/posts'>لغو</a></p>"
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
    html = "<h1>ویرایش پست</h1><form method='POST'><input name='title' value='" + p[1] + "' required><textarea name='content' required>" + p[2] + "</textarea><button type='submit' class='btn'>ذخیره</button></form><p><a href='/admin/posts'>لغو</a></p>"
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