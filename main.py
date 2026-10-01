import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
import google.generativeai as genai

app = FastAPI(title="Check It AI - All-in-One AI Platform Backend")

# Google AI Studio API Key కాన్ఫిగరేషన్
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# AWS S3 సెటప్ (ఫైల్స్, ఇమేజ్‌లు, ఆడియోల స్టోరేజ్ కోసం)
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

# 'Check It AI' ఆల్-ఇన్-వన్ సిస్టమ్ ఇన్‌స్ట్రక్షన్
SYSTEM_INSTRUCTION = (
    "నువ్వు 'Check It AI' అడ్వాన్స్‌డ్ ఏఐ అసిస్టెంట్. విద్యార్థులకు మరియు డెవలపర్లకు "
    "చాటింగ్, కోడింగ్, వెబ్‌సైట్/యాప్ డెవలప్‌మెంట్, ఎడ్యుకేషన్ మరియు టెక్నికల్ సపోర్ట్ "
    "అందిస్తావు. అన్ని ప్రశ్నలకు మరియు కోడింగ్ రిక్వెస్ట్‌‌లకు తెలుగు మరియు ఆంగ్లంలో "
    "స్పష్టమైన, ఖచ్చితమైన సమాధానాలు, కోడ్ స్నిప్పెట్స్ అందించు."
)

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=SYSTEM_INSTRUCTION,
)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Check It AI All-in-One Platform Backend is live!",
        "features": ["Chat", "App/Web Code Generation", "Multimodal Analysis", "S3 Storage"]
    }

# 1. ప్రధానమైన జనరల్ & మల్టీమోడల్ ఎండ్‌పాయింట్ (చాట్, ఫైల్స్, ఇమేజ్ అనాలిసిస్)
@app.post("/check")
async def check_question(
    question: Optional[str] = Form(None),
    exam_type: str = Form("General"),
    file: Optional[UploadFile] = Form(None),
):
    try:
        prompt_text = (
            f"[Category/Mode: {exam_type}]\n"
            f"User Query: {question if question else 'దయచేసి దీనిని విశ్లేషించండి.'}"
        )

        content_parts = [prompt_text]

        if file and hasattr(file, "filename") and file.filename:
            file_bytes = await file.read()
            if len(file_bytes) > 0:
                if s3_client:
                    try:
                        unique_filename = f"uploads/{uuid.uuid4()}-{file.filename}"
                        s3_client.put_object(
                            Bucket=S3_BUCKET,
                            Key=unique_filename,
                            Body=file_bytes,
                            ContentType=file.content_type,
                        )
                    except Exception as s3_err:
                        print(f"S3 Upload Error: {s3_err}")

                mime_type = file.content_type or "application/octet-stream"
                content_parts.append({
                    "mime_type": mime_type,
                    "data": file_bytes
                })

        response = model.generate_content(content_parts)

        return {
            "status": "success",
            "category": exam_type,
            "response": response.text if response.text else "సమాధానం అందుబాటులో లేదు.",
        }

    except Exception as err:
        return {
            "status": "error",
            "error_type": str(type(err).__name__),
            "error_details": str(err),
            "traceback": traceback.format_exc(),
        }

# 2. వెబ్‌సైట్ మరియు యాప్ కోడింగ్ కోసం ప్రత్యేకమైన ఎండ్‌పాయింట్
@app.post("/generate-code")
async def generate_code(
    app_description: str = Form(...),
    platform_type: str = Form("Web") # Web లేదా Mobile App
):
    try:
        coding_prompt = (
            f"Create a complete, clean, and production-ready {platform_type} code "
            f"based on the following requirements:\n{app_description}\n"
            f"Provide proper structure, instructions, and explanation in Telugu where necessary."
        )
        
        response = model.generate_content(coding_prompt)

        return {
            "status": "success",
            "platform": platform_type,
            "generated_code": response.text
        }
    except Exception as err:
        return {
            "status": "error",
            "error_details": str(err)
        }
