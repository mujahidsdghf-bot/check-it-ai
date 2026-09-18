import base64
import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
import google.generativeai as genai

app = FastAPI(title="Check It AI Backend")

# Render నుండి API కీ తీసుకోవడం
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "AQ.Ab8RN6KRDiRukL3Xy21q1LnU_LP9FlC65Si8u_KpA7fWAeJ63w",
).strip()

# జెమిని కాన్ఫిగరేషన్
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. విద్యార్థుల ప్రశ్నలకు "
    "తెలుగులో స్పష్టమైన, సరైన సమాధానాలు అందించు."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
)

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
        prompt_text = (
            f"[Exam Category: {exam_type}]\n"
            f"Question: {question if question else 'దయచేసి వివరణ ఇవ్వండి.'}"
        )

        content_parts = [prompt_text]

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
                    except Exception as s3_err:
                        print(f"S3 Upload Error: {s3_err}")

                mime_type = file.content_type or "image/jpeg"
                content_parts.append(
                    {"mime_type": mime_type, "data": file_bytes}
                )

        # అధికారిక SDK కాల్
        response = model.generate_content(content_parts)

        return {
            "status": "success",
            "exam_type": exam_type,
            "answer": response.text if response.text else "సమాధానం రాలేదు.",
        }

    except Exception as err:
        return {
            "status": "error",
            "error_type": str(type(err).__name__),
            "error_details": str(err),
            "traceback": traceback.format_exc(),
        }
