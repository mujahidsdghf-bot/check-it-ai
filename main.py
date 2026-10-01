import os
import traceback
import uuid
from typing import Optional
import boto3
from fastapi import FastAPI, File, Form, UploadFile
import google.generativeai as genai

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

# అల్టిమేట్ మాస్టర్ సిస్టమ్ ఇన్‌స్ట్రక్షన్ (మల్టీ-లాంగ్వేజ్ & ఆల్-ఇన్-వన్ సపోర్ట్)
SYSTEM_INSTRUCTION = (
    "You are 'Check It AI', the ultimate world-class multi-language AI assistant. "
    "You can generate apps/websites, teach Python, design images/ads, create movies/videos from stories (Story to Movie/Reels), "
    "provide business and food industry strategies, guide robotics and laptop/computer repairs, and solve any technical or educational doubts. "
    "CRITICAL RULE: Always reply in the EXACT SAME LANGUAGE that the user uses to ask the question (whether it is Telugu, Hindi, English, Spanish, French, etc.). "
    "Provide clear, professional, and comprehensive responses."
)

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=SYSTEM_INSTRUCTION,
)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Check It AI Ultimate Multi-Language Platform is live!",
        "supported_languages": "All World Languages (Auto-detect based on user input)",
        "all_capabilities": [
            "Story to Movie & Reels Generator (/story-to-movie)",
            "General Chat & Multimodal File/Image Analysis (/check)",
            "App & Website Code Generation (/build-app-web)",
            "Python Programming & Learning Tutor (/python-mentor)",
            "Image, Drawing & Ad Design Concepts (/design-ads)",
            "Video Editing & YouTube/Reels Content Creation (/video-creator)",
            "Business Strategies & Food Industry Tricks (/business-tricks)",
            "Robotics, Computer & Laptop Repair Guide (/repair-tech)",
            "Resume Builder & Interview Prep (/career-coach)",
            "Document & Text Summarization (/summarizer)"
        ]
    }

# 1. సాధారణ డౌట్స్ మరియు మల్టీమోడల్ (ఫైల్/ఫోటో) విశ్లేషణ
@app.post("/check")
async def check_question(
    question: Optional[str] = Form(None),
    exam_type: str = Form("General"),
    file: Optional[UploadFile] = Form(None),
):
    try:
        prompt_text = (
            f"[Category/Mode: {exam_type}]\n"
            f"User Query: {question if question else 'Please analyze this.'}"
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
            "response": response.text if response.text else "No response generated.",
        }
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 2. కథ చెప్తే సినిమా/రీల్స్ రెడీ చేసే విధానం (Story to Movie / Story to Reels) - కొత్తది
@app.post("/story-to-movie")
async def story_to_movie(
    story_plot: str = Form(...),
    output_format: str = Form("Full Movie Script & Scene Breakdown") # Full Movie Script, Short Film, Instagram Reels
):
    try:
        prompt = (
            f"Act as a world-class Hollywood/Tollywood Director, Screenwriter, and Storyboard Artist. "
            f"Convert the following story plot into a complete {output_format}:\n"
            f"Story Plot: {story_plot}\n"
            f"Provide scene descriptions, character dialogues, camera angles, background music cues, "
            f"and visual prompt ideas for AI video generators. IMPORTANT: Reply in the language of the input story."
        )
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "format": output_format,
            "cinematic_production_plan": response.text
        }
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 3. యాప్ మరియు వెబ్‌సైట్ బిల్డింగ్
@app.post("/build-app-web")
async def build_app_web(
    project_description: str = Form(...),
    target_platform: str = Form("Web Website")
):
    try:
        prompt = (
            f"Create a complete, production-ready code structure and implementation "
            f"guide for the following {target_platform}:\nRequirements: {project_description}\n"
            f"Provide clean code snippets and explanations in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "platform": target_platform, "generated_solution": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 4. పైథాన్ కోడింగ్ మరియు లెర్నింగ్ ట్యుటోరియల్స్
@app.post("/python-mentor")
async def python_mentor(
    learning_topic_or_code_error: str = Form(...),
    mode: str = Form("Learn Topic")
):
    try:
        prompt = (
            f"Act as an expert Python programming mentor. Mode: {mode}\n"
            f"Query/Topic/Error: {learning_topic_or_code_error}\n"
            f"Explain concepts clearly, provide working Python code, and explain in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "mode": mode, "python_guidance": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 5. ఇమేజెస్, డ్రాయింగ్ మరియు అడ్వర్టైజ్‌‌మెంట్ డిజైనింగ్ గైడ్
@app.post("/design-ads")
async def design_ads(
    design_concept: str = Form(...),
    category: str = Form("Social Media Ad Banner")
):
    try:
        prompt = (
            f"Act as a professional Creative Director and Graphic Designer. Provide detailed "
            f"design prompts, color schemes, layout structures, and marketing ad copy for: {design_concept}\n"
            f"Category: {category}\nExplain the visual creation strategy in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "category": category, "design_guide": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 6. వీడియోస్, యూట్యూబ్ స్క్రిప్ట్స్ & ఎడిటింగ్ గైడ్
@app.post("/video-creator")
async def video_creator(
    video_topic: str = Form(...),
    video_type: str = Form("YouTube Video Script & Editing Plan")
):
    try:
        prompt = (
            f"Act as an expert Video Producer and Editor. Create a complete script, "
            f"storyboard breakdown, and video editing guide for: {video_topic}\n"
            f"Type: {video_type}\nProvide catchy hooks, visual cues, and explanation in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "video_type": video_type, "video_plan": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 7. బిజినెస్ గ్రోత్, మార్కెటింగ్ & ఫుడ్ ఇండస్ట్రీ ట్రిక్స్
@app.post("/business-tricks")
async def business_tricks(
    business_idea: str = Form(...),
    goal: str = Form("Growth and Marketing")
):
    try:
        prompt = (
            f"Provide powerful business strategies, marketing tricks, packaging ideas, "
            f"and a revenue roadmap for this business or food product idea:\n"
            f"Business/Food Idea: {business_idea}\nGoal: {goal}\n"
            f"Give practical, actionable steps explained in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "business_strategy": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 8. రోబోటిక్స్, కంప్యూటర్, లాప్టాప్ రిపేర్ & సాఫ్ట్‌వేర్ ట్రబుల్‌షూటింగ్
@app.post("/repair-tech")
async def repair_tech(
    issue_or_device: str = Form(...),
    domain: str = Form("Laptop/Computer Repair")
):
    try:
        prompt = (
            f"Act as an expert Hardware Engineer, Robotics Technician, and Software Specialist. "
            f"Diagnose and provide step-by-step troubleshooting, repair instructions, or building guide for:\n"
            f"Domain: {domain}\nIssue/Device: {issue_or_device}\n"
            f"Give safe, accurate technical solutions explained in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "domain": domain, "repair_solution": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 9. రెజ్యూమ్ బిల్డింగ్ & ఇంటర్వ్యూ ప్రిపరేషన్
@app.post("/career-coach")
async def career_coach(
    job_role: str = Form(...),
    request_type: str = Form("Interview Questions")
):
    try:
        prompt = (
            f"Act as an expert career coach. Provide professional {request_type} "
            f"for the job role: {job_role}.\nGive helpful guidelines in the user's language."
        )
        response = model.generate_content(prompt)
        return {"status": "success", "role": job_role, "career_guidance": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}

# 10. పెద్ద డాక్యుమెంట్లు లేదా టెక్స్ట్ సమ్మరైజేషన్
@app.post("/summarizer")
async def summarizer(
    long_text: str = Form(...)
):
    try:
        prompt = (
            f"Summarize the following text into key bullet points and clear takeaways, "
            f"explaining the summary in the user's language:\n\n{long_text}"
        )
        response = model.generate_content(prompt)
        return {"status": "success", "summary": response.text}
    except Exception as err:
        return {"status": "error", "error_details": str(err)}
