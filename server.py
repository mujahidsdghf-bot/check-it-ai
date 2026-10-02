import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify, request

app = Flask(__name__)

# తాత్కాలికంగా OTPలను స్టోర్ చేయడానికి
otp_storage = {}

# మీ Gmail వివరాలు (ఇక్కడ మీ మెయిల్ మరియు App Password ఇవ్వండి)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Google App Password ఇవ్వాలి


@app.route("/api/send-otp", methods=["POST"])
def send_otp():
  email = request.form.get("email")
  if not email:
    return jsonify({"status": "error", "message": "Email is required"})

  otp = str(random.randint(100000, 999900))
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

    return jsonify({"status": "success", "message": "OTP sent to email successfully!"})
  except Exception as e:
    # ఒకవేళ SMTP సెటప్ చేయకపోతే టెస్టింగ్ కోసం డిస్ప్లే చేయడానికి
    return jsonify({
        "status": "success",
        "message": f"OTP generated (SMTP simulated): {otp}",
    })


@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
  email = request.form.get("email")
  user_otp = request.form.get("otp")

  if otp_storage.get(email) == user_otp:
    return jsonify({"status": "success", "message": "Login successful!"})
  return jsonify({"status": "error", "message": "Invalid OTP"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
