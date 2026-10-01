import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

app = FastAPI(title="Check It AI - Ultimate World-Class Multi-Language Super Platform")

# Google AI Studio API Key కాన్ఫిగరేషన్
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# AWS S3 స్టోరేజ్ సెటప్
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

# అల్టిమేట్ మాస్టర్ సిస్టమ్ ఇన్‌స్ట్రక్షన్
SYSTEM_INSTRUCTION = (
    "You are 'Check It AI', the ultimate world-class multi-language AI assistant. "
    "You can generate apps/websites, teach Python, design images/ads, create movies/videos from stories (Story to Movie/Reels), "
    "provide business and food industry strategies, guide robotics and laptop/computer repairs, and solve any technical or educational doubts. "
    "CRITICAL RULE: Always reply in the EXACT SAME LANGUAGE that the user uses to ask the question. "
    "Provide clear, professional, and comprehensive responses."
)

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=SYSTEM_INSTRUCTION,
)

# సురక్షితమైన జనరేషన్ మరియు కోటా ఎర్రర్ హ్యాండ్లర్
def safe_generate(content_parts):
    try:
        response = model.generate_content(content_parts)
        return response.text if response.text else "సమాధానం అందుబాటులో లేదు."
    except ResourceExhausted:
        return "⚠️ గమనించండి: ప్రస్తుత ఏఐ కీ యొక్క ఉచిత కోటా (Limit) తాత్కాలికంగా ముగిసింది. దయచేసి కొద్దిసేపు ఆగి ప్రయత్నించండి."
    except Exception as e:
        return f"సమస్య ఏర్పడింది: {str(e)}"

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Check It AI Ultimate Multi-Language Platform is live!",
        "supported_languages": "All World Languages (Auto-detect based on user input)",
    }

# 1. సాధారణ డౌట్స్ మరియు మల్టీమోడల్ విశ్లేషణ
@app.post("/check")
async def check_question(
    question: Optional[str] = Form(None),
    exam_type: str = Form("General"),
    file: Optional[UploadFile] = Form(None),
):
    try:
        prompt_text = f"[Category/Mode: {exam_type}]\nUser Query: {question if question else 'Please analyze this.'}"
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
                content_parts.append({"mime_type": mime_type, "data": file_bytes})

        result_text = safe_generate(content_parts)
        return {"status": "success", "category": exam_type, "response": result_text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 2. కథ చెప్తే సినిమా/రీల్స్ రెడీ చేసే విధానం (Story to Movie / Story to Reels)
@app.post("/story-to-movie")
async def story_to_movie(
    story_plot: str = Form(...),
    output_format: str = Form("Full Movie Script & Scene Breakdown")
):
    prompt = (
        f"Act as a world-class Director and Screenwriter. Convert this story into a {output_format}:\n"
        f"Story Plot: {story_plot}\nProvide scene descriptions, dialogues, camera angles, and reply in the story's language."
    )
    return {"status": "success", "format": output_format, "cinematic_production_plan": safe_generate(prompt)}

# 3. యాప్ మరియు వెబ్‌సైట్ బిల్డింగ్
@app.post("/build-app-web")
async def build_app_web(
    project_description: str = Form(...),
    target_platform: str = Form("Web Website")
):
    prompt = f"Create production-ready code structure and guide for {target_platform}: {project_description}"
    return {"status": "success", "platform": target_platform, "generated_solution": safe_generate(prompt)}

# 4. పైథాన్ కోడింగ్ మరియు లెర్నింగ్ ట్యుటోరియల్స్
@app.post("/python-mentor")
async def python_mentor(
    learning_topic_or_code_error: str = Form(...),
    mode: str = Form("Learn Topic")
):
    prompt = f"Act as Python mentor. Mode: {mode}. Topic/Error: {learning_topic_or_code_error}"
    return {"status": "success", "mode": mode, "python_guidance": safe_generate(prompt)}

# 5. ఇమేజెస్, డ్రాయింగ్ మరియు అడ్వర్టైజ్‌‌మెంట్ డిజైనింగ్
@app.post("/design-ads")
async def design_ads(
    design_concept: str = Form(...),
    category: str = Form("Social Media Ad Banner")
):
    prompt = f"Provide design prompts, color schemes, and ad copy for {category}: {design_concept}"
    return {"status": "success", "category": category, "design_guide": safe_generate(prompt)}

# 6. వీడియోస్, యూట్యూబ్ స్క్రిప్ట్స్ & ఎడిటింగ్ గైడ్
@app.post("/video-creator")
async def video_creator(
    video_topic: str = Form(...),
    video_type: str = Form("YouTube Video Script & Editing Plan")
):
    prompt = f"Create script, storyboard, and editing guide for {video_type}: {video_topic}"
    return {"status": "success", "video_type": video_type, "video_plan": safe_generate(prompt)}

# 7. బిజినెస్ గ్రోత్, మార్కెటింగ్ & ఫుడ్ ఇండస్ట్రీ ట్రిక్స్
@app.post("/business-tricks")
async def business_tricks(
    business_idea: str = Form(...),
    goal: str = Form("Growth and Marketing")
):
    prompt = f"Provide business strategies, packaging ideas, and marketing roadmap for: {business_idea}"
    return {"status": "success", "business_strategy": safe_generate(prompt)}

# 8. రోబోటిక్స్, కంప్యూటర్, లాప్టాప్ రిపేర్ & సాఫ్ట్‌వేర్ ట్రబుల్‌షూటింగ్
@app.post("/repair-tech")
async def repair_tech(
    issue_or_device: str = Form(...),
    domain: str = Form("Laptop/Computer Repair")
):
    prompt = f"Provide step-by-step troubleshooting and repair guide for {domain}: {issue_or_device}"
    return {"status": "success", "domain": domain, "repair_solution": safe_generate(prompt)}

# 9. రెజ్యూమ్ బిల్డింగ్ & ఇంటర్వ్యూ ప్రిపరేషన్
@app.post("/career-coach")
async def career_coach(
    job_role: str = Form(...),
    request_type: str = Form("Interview Questions")
):
    prompt = f"Provide professional {request_type} for job role: {job_role} with guidelines."
    return {"status": "success", "role": job_role, "career_guidance": safe_generate(prompt)}

# 10. పెద్ద డాక్యుమెంట్లు లేదా టెక్స్ట్ సమ్మరైజేషన్
@app.post("/summarizer")
async def summarizer(
    long_text: str = Form(...)
):
    prompt = f"Summarize the following text into key bullet points and clear takeaways:\n\n{long_text}"
    return {"status": "success", "summary": safe_generate(prompt)}
