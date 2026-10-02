Import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# మీ జీమెయిల్ వివరాలు ఇక్కడ ఇవ్వండి
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gyhiffss1@gmail.com"  # మీ అసలు జీమెయిల్
SENDER_PASSWORD = "tzsj nbts kvnu fsti"  # గూగుల్ 16 అంకెల యాప్ పాస్‌వర్డ్

otp_storage = {}


@app.after_request
def after_request(response):
  response.headers.add("Access-Control-Allow-Origin", "*")
  response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
  response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
  return response


@app.route("/", methods=["GET"])
def home():
  return jsonify({"status": "online", "message": "Check It AI Backend is Running!"})


@app.route("/api/send-otp", methods=["POST", "OPTIONS"])
def send_otp():
  if request.method == "OPTIONS":
    return jsonify({}), 200

  # JSON లేదా Form డేటా రెండింటినీ తీసుకునేలా
  email = None
  if request.is_json:
    email = request.json.get("email")
  else:
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
  if request.is_json:
    email = request.json.get("email")
    user_otp = request.json.get("otp")
  else:
    email = request.form.get("email")
    user_otp = request.form.get("otp")

  if otp_storage.get(email) == user_otp:
    return jsonify({"status": "success", "message": "Login successful!"})
  return jsonify({"status": "error", "message": "Invalid OTP"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
