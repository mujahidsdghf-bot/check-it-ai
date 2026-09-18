import io
import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
from google import genai
from google.genai import types
from PIL import Image

app = FastAPI(title="Check It AI Backend")

# మీ కొత్త Gemini API Key
GEMINI_API_KEY = (
    "AQ.Ab8RN6KOO33Z_-G5b-wUfLHQ94qaBA7SLusw9TjkKiThC7mEbw"
)

try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    ai_client = None
    print(f"Client Init Error: {e}")

# AWS S3 సెటప్ (ఐచ్ఛికం)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("AWS_S3_BUCKET", "check-it-ai-uploads")

s3_client = None
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )
    except Exception as e:
        print(f"S3 Warning: {e}")

SYSTEM_PROMPT = """
నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. 
పోటీ పరీక్షలకు విద్యార్థులకు ఖచ్చితమైన సమాధానాలు, వివరణలు తెలుగులో అందించు.
"""


@app.get("/")
def root():
    return {"status": "online", "message": "Check It AI API is live!"}


@app.post("/check")
async def check_question(
    question: Optional[str] = Form(None),
    exam_type: str = Form("General"),
    file: Optional[UploadFile] = File(None),
):
    try:
        if not ai_client:
            return {
                "status": "error",
                "message": "AI Client ప్రారంభం కాలేదు. API Key చెక్ చేయండి.",
            }

        contents = []
        user_prompt = f"[Exam Category: {exam_type}]\n"

        if question:
            user_prompt += f"Question: {question}\n"
        else:
            user_prompt += "దయచేసి ఈ ప్రశ్నకు పూర్తి వివరణ ఇవ్వండి."

        contents.append(user_prompt)
        s3_path = None

        if file and file.filename:
            file_bytes = await file.read()
            if len(file_bytes) > 0:
                if s3_client:
                    try:
                        unique_filename = (
                            f"questions/{uuid.uuid4()}-{file.filename}"
                        )
                        s3_client.put_object(
                            Bucket=S3_BUCKET,
                            Key=unique_filename,
                            Body=file_bytes,
                            ContentType=file.content_type,
                        )
                        s3_path = unique_filename
                    except Exception as s3_err:
                        print(f"S3 Upload Error: {s3_err}")

                try:
                    image = Image.open(io.BytesIO(file_bytes))
                    contents.append(image)
                except Exception as img_err:
                    print(f"Image Error: {img_err}")

        # Gemini కాల్
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            ),
        )

        return {
            "status": "success",
            "exam_type": exam_type,
            "s3_path": s3_path,
            "answer": response.text,
        }

    except Exception as err:
        return {
            "status": "error",
            "error_type": str(type(err).__name__),
            "error_details": str(err),
            "traceback": traceback.format_exc(),
        }
