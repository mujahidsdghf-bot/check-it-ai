import io
import os
from fastapi import FastAPI, File, Form, UploadFile
from google import genai
from google.genai import types
from PIL import Image

app = FastAPI(title="Check It AI Backend")

# Gemini Client సెటప్ (API key ఎన్విరాన్‌మెంట్ వేరియబుల్ నుంచి తీసుకుంటుంది)
# export GEMINI_API_KEY="your_api_key_here"
client = genai.Client()

SYSTEM_PROMPT = """
నువ్వు 'Check It AI' ఎడ్యుకేషన్ అండ్ కెరీర్ మెంటార్. 
విద్యార్థులకు EAMCET, JEE, NEET, CA, Groups వంటి వివిధ పోటీ పరీక్షలకు సంబంధించి ఖచ్చితమైన సమాధానాలు, స్టెప్-బై-స్టెప్ సొల్యూషన్స్ మరియు కెరీర్ గైడెన్స్ అందించాలి.
- విద్యార్థి సొల్యూషన్ రాసి ఫోటో పెడితే: అందులో తప్పు ఎక్కడ జరిగిందో వివరించి, సరైన పద్ధతిని చూపించు.
- డైరెక్ట్ ప్రశ్న అడిగితే: సులభమైన వివరణతో పాటు ముఖ్యమైన కాన్సెప్ట్, ఫార్ములాను హైలైట్ చేయి.
- స్పష్టమైన తెలుగు లేదా ఇంగ్లీష్‌తో జవాబు ఇవ్వు.
"""


@app.post("/check")
async def check_query(
    question: str = Form(
        None
    ),  # విద్యార్థి టెక్స్ట్ ప్రశ్న (ఆప్షనల్ లేదా ఫోటోతో కలిపి)
    exam_type: str = Form(
        "General"
    ),  # ఉదా: NEET, JEE, EAMCET, Groups, CA etc.
    file: UploadFile = File(None),  # ప్రశ్న లేదా సొల్యూషన్ ఫోటో (ఆప్షనల్)
):
    contents = []

    # యూజర్ పంపిన పరీక్ష రకం మరియు ప్రశ్న ప్రాంప్ట్
    user_prompt = f"[Exam Category: {exam_type}]\n"
    if question:
        user_prompt += f"Question/Query: {question}\n"
    else:
        user_prompt += "దయచేసి ఈ ఫోటోలోని ప్రశ్నను గుర్తించి, పూర్తి పరిష్కారం మరియు వివరణ అందించండి."

    contents.append(user_prompt)

    # ఫోటో అప్‌లోడ్ చేస్తే దానిని ప్రాసెస్ చేయడం
    if file:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        contents.append(image)

    # Gemini 2.5 Flash మోడల్ ద్వారా విశ్లేషణ
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,  # ఖచ్చితమైన ఎకడమిక్ సమాధానాల కోసం తక్కువ టెంపరేచర్
        ),
    )

    return {
        "status": "success",
        "exam_type": exam_type,
        "answer": response.text,
    }
