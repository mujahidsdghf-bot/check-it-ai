import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# అన్ని రకాల ఒరిజిన్స్ మరియు మెథడ్స్‌ని అనుమతించడానికి
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gyhiffss1@gmail.com"
SENDER_PASSWORD = "tzsj nbts kvnu fsti"

otp_storage = {}


@app.after_request
def add_cors_headers(response):
  response.headers["Access-Control-Allow-Origin"] = "*"
  response.headers["Access-Control-Allow-Headers"] = (
      "Content-Type,Authorization,X-Requested-With"
  )
  response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
  return response


@app.route("/", methods=["GET"])
def home():
  return jsonify({"status": "online", "message": "Check It AI Backend is Running!"})


@app.route("/api/send-otp", methods=["POST", "OPTIONS"])
def send_otp():
  if request.method == "OPTIONS":
    return jsonify({}), 200

  email = None
  try:
    if request.is_json:
      data = request.get_json(silent=True)
      if data:
        email = data.get("email")
  except Exception:
    pass

  if not email:
    email = request.form.get("email") or request.args.get("email")

  if not email:
    return jsonify({"status": "error", "message": "Email is required"})

  otp = str(random.randint(100000, 999999))
  otp_storage[email] = otp

  try:
    msg = MIMEText(
        f"Your verification OTP for Check It AI is: {otp}\nValid for 10"
        " minutes."
    )
    msg["Subject"] = "Check It AI - Login OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, email, msg.as_string())
    server.quit()

    return jsonify({"status": "success", "message": "OTP sent to your email successfully!"})
  except Exception as e:
    return jsonify({
        "status": "error",
        "message": f"SMTP Error: {str(e)}. Check your Gmail App Password.",
    })


@app.route("/api/verify-otp", methods=["POST", "OPTIONS"])
def verify_otp():
  if request.method == "OPTIONS":
    return jsonify({}), 200

  email = None
  user_otp = None
  try:
    if request.is_json:
      data = request.get_json(silent=True)
      if data:
        email = data.get("email")
        user_otp = data.get("otp")
  except Exception:
    pass

  if not email:
    email = request.form.get("email") or request.args.get("email")
  if not user_otp:
    user_otp = request.form.get("otp") or request.args.get("otp")

  if otp_storage.get(email) == user_otp:
    return jsonify({"status": "success", "message": "Login successful!"})
  return jsonify({"status": "error", "message": "Invalid OTP"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
