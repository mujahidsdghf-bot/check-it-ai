import io
import os
import uuid
import boto3
from fastapi import FastAPI, File, Form, UploadFile
from google import genai
from google.genai import types
from PIL import Image

app = FastAPI(title="Check It AI Backend")

# 1. Gemini AI సెటప్ (Render Environment Variables నుండి API కీ తీసుకుంటుంది)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# 2. AWS S3 సెటప్ (ఐచ్ఛికం - కీలు ఉంటేనే రన్ అవుతుంది, లేకపోతే సర్వర్ ఆగదు)
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
        print(f"S3 Client Warning: {e}")

SYSTEM_PROMPT = """
నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. 
విద్యార్థులకు EAMCET, JEE, NEET, CA, Groups, UPSC వంటి అన్ని రకాల పోటీ పరీక్షలకు ఖచ్చితమైన సమాధానాలు, స్టెప్-బై-స్టెప్ సొల్యూషన్స్ మరియు కెరీర్ గైడెన్స్ అందించాలి.
- విద్యార్థి సొల్యూషన్ రాసి ఫోటో పెడితే: అందులో తప్పు ఎక్కడ జరిగిందో గుర్తించి, సరైన పద్ధతిని వివరించు.
- నేరుగా ప్రశ్న అడిగితే: సులభమైన వివరణతో పాటు ముఖ్యమైన కాన్సెప్ట్ మరియు ఫార్ములాను స్పష్టంగా రాయి.
- సమాధానం విద్యార్థికి సులభంగా అర్థమయ్యేలా అందించు.
"""


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Check It AI API is live and running successfully!",
    }


@app.post("/check")
async def check_question(
    question: str = Form(None),
    exam_type: str = Form("General"),
    file: UploadFile = File(None),
):
    if not ai_client:
        return {
            "status": "error",
            "message": "Gemini API Key ఇంకా సెట్ చేయలేదు. దయచేసి Render Environment Variables చెక్ చేయండి.",
        }

    contents = []
    user_prompt = f"[Exam Category: {exam_type}]\n"

    if question:
        user_prompt += f"Question: {question}\n"
    else:
        user_prompt += "దయచేసి ఈ ఫోటోలోని ప్రశ్నను విశ్లేషించి, పూర్తి సమాధానం మరియు వివరణ ఇవ్వండి."

    contents.append(user_prompt)
    s3_path = None

    # ఫోటో ఉంటే ప్రాసెస్ చేయడం
    if file:
        file_bytes = await file.read()

        # S3 సెటప్ ఉంటే ఫోటోను సేవ్ చేయడం
        if s3_client:
            try:
                unique_filename = f"questions/{uuid.uuid4()}-{file.filename}"
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=unique_filename,
                    Body=file_bytes,
                    ContentType=file.content_type,
                )
                s3_path = unique_filename
            except Exception as e:
                print(f"S3 Upload Warning: {e}")

        # AI కోసం ఇమేజ్ సిద్ధం చేయడం
        image = Image.open(io.BytesIO(file_bytes))
        contents.append(image)

    # Gemini మోడల్ ద్వారా విశ్లేషణ
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
