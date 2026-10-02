import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # గిహబ్ నుండి వచ్చే రిక్వెస్ట్‌లను అనుమతించడానికి

otp_storage = {}

# మీ జిమెయిల్ వివరాలు (ఇక్కడ మీ మెయిల్ మరియు App Password ఇవ్వండి)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"


@app.route("/", methods=["GET"])
def home():
  return jsonify({"status": "online", "message": "Check It AI Backend is Running!"})


@app.route("/api/send-otp", methods=["POST"])
def send_otp():
  email = request.form.get("email")
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
    # SMTP సెటప్ చేయనప్పటికీ టెస్టింగ్ కోసం ఓటీపీని రిటర్న్ చేయడానికి
    return jsonify({
        "status": "success",
        "message": (
            f"OTP generated (SMTP simulated): {otp}. (Configure SMTP in"
            " server.py for real mail)"
        ),
    })


@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
  email = request.form.get("email")
  user_otp = request.form.get("otp")

  if otp_storage.get(email) == user_otp:
    return jsonify({"status": "success", "message": "Login successful!"})
  return jsonify({"status": "error", "message": "Invalid OTP"})


@app.route("/api/chat", methods=["POST"])
def chat():
  prompt = request.form.get("prompt")
  # ఏఐ రెస్పాన్స్ జనరేషన్ లాజిక్
  return jsonify({
      "status": "success",
      "response": (
          "<!DOCTYPE html><html><body"
          " style='font-family:sans-serif;padding:20px;background:#f8fafc;'><h2>Generated"
          f" Result</h2><p>Your request: {prompt}</p><button"
          " style='background:#10b981;color:white;padding:10px"
          " 20px;border:none;border-radius:6px;'>Pay Now / Buy</button></body></html>"
      ),
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
