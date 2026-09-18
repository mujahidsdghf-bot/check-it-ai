import base64
import io
import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
import httpx
from PIL import Image

app = FastAPI(title="Check It AI Backend")

# మీ AQ API Key
GEMINI_API_KEY = (
    "AQ.Ab8RN6KOO33Z_-G5b-wUfLHQ94qaBA7SLusw9TjkKiThC7mEbw"
)

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

SYSTEM_INSTRUCTION = """
నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. 
పోటీ పరీక్షలకు (EAMCET, JEE, NEET, UPSC మొదలైనవి) విద్యార్థులకు ఖచ్చితమైన సమాధానాలు, స్టెప్-బై-స్టెప్ వివరణలు తెలుగులో స్పష్టంగా అందించు.
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
        s3_path = None
        prompt_text = (
            f"[Exam Category: {exam_type}]\n"
            f"Question: {question if question else 'దయచేసి ఈ చిత్రంలోని ప్రశ్నను వివరించండి.'}"
        )

        parts = [{"text": prompt_text}]

        # ఫోటో ఉంటే Base64 లోకి మార్చి పంపడం
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

                mime_type = file.content_type or "image/jpeg"
                encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                parts.append(
                    {"inline_data": {"mime_type": mime_type, "data": encoded_image}}
                )

        # Gemini REST API కాల్ - AQ కీలతో 100% పనిచేసే విధానం
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.3},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()

        if resp.status_code != 200:
            return {
                "status": "error",
                "http_status": resp.status_code,
                "error_details": data,
            }

        answer_text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "సమాధానం రాలేదు.")
        )

        return {
            "status": "success",
            "exam_type": exam_type,
            "s3_path": s3_path,
            "answer": answer_text,
        }

    except Exception as err:
        return {
            "status": "error",
            "error_type": str(type(err).__name__),
            "error_details": str(err),
            "traceback": traceback.format_exc(),
        }
