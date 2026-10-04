import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1 style='color: purple; text-align: center; margin-top: 100px;'>سلام! سایت کار می‌کنه</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)