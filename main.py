import base64
import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Render లో ఉన్న సీక్రెట్ ఫైల్ పాత్‌ను గూగుల్ క్లౌడ్‌కు అనుసంధానించడం
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/credentials.json"

app = FastAPI(title="Check It AI Backend - Vertex AI")

# ప్రాజెక్ట్ వివరాలు మరియు రీజియన్ సెటప్ (కొత్త ప్రాజెక్ట్ పేరుతో)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "check-it-ai")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Vertex AI ఇనిషియలైజేషన్
try:
    vertexai.init(project=PROJECT_ID, location=REGION)
except Exception as e:
    print(f"Vertex Init Warning: {e}")

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

SYSTEM_INSTRUCTION = (
    "నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. విద్యార్థుల ప్రశ్నలకు "
    "తెలుగులో స్పష్టమైన, సరైన సమాధానాలు అందించు."
)

# Vertex AI లోని జెమిని మోడల్
model = GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=[SYSTEM_INSTRUCTION],
)


@app.get("/")
def root():
    return {"status": "online", "message": "Check It AI Vertex API is live!"}


@app.post("/check")
async def check_question(
    question: Optional[str] = Form(None),
    exam_type: str = Form("General"),
    file: Optional[UploadFile] = Form(None),
):
    try:
        prompt_text = (
            f"[Exam Category: {exam_type}]\n"
            f"Question: {question if question else 'దయచేసి వివరణ ఇవ్వండి.'}"
        )

        content_parts = [prompt_text]

        if file and hasattr(file, "filename") and file.filename:
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
                image_part = Part.from_data(data=file_bytes, mime_type=mime_type)
                content_parts.append(image_part)

        # Vertex AI ద్వారా కంటెంట్ జనరేట్ చేయడం
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
