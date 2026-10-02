import streamlit as st
import requests

st.set_page_config(
    page_title="Check It AI - Ultimate World-Class Platform",
    page_icon="🤖",
    layout="wide"
)

# మీ రెండర్ బ్యాకెండ్ లైవ్ URL
BACKEND_URL = "https://check-it-ai.onrender.com"

st.title("🚀 Check It AI - Ultimate World-Class Multi-Language Platform")
st.markdown("ప్రపంచంలో ఏఐ చేయగల సకల సేవలు (సినిమా మేకింగ్, కోడింగ్, రిపేర్లు, బిజినెస్ & ఫుడ్ ట్రిక్స్) ఏ భాషలోనైనా ఒకే చోట!")

st.sidebar.header("🛠️ Check It AI Features Menu")
choice = st.sidebar.selectbox("ఒక ఫీచర్‌ను ఎంచుకోండి:", [
    "💬 జనరల్ చాట్ & ఫైల్ విశ్లేషణ (General Chat)",
    "🎬 స్టోరీ టూ మూవీ / రీల్స్ (Story to Movie)",
    "💻 యాప్ & వెబ్‌సైట్ బిల్డింగ్ (App/Web Builder)",
    "🐍 పైథాన్ మెంటార్ & కోడింగ్ (Python Tutor)",
    "🎨 డిజైన్ & యాడ్స్ బ్యానర్స్ (Design & Ads)",
    "🎥 వీడియో క్రియేటర్ & స్క్రిప్ట్స్ (Video Creator)",
    "📈 బిజినెస్ & ఫుడ్ ట్రిక్స్ (Business & Food)",
    "🔧 రోబోటిక్స్ & లాప్‌టాప్ రిపేర్ (Repair Tech)",
    "👔 రెజ్యూమ్ & ఇంటర్వ్యూ కోచ్ (Career Coach)",
    "📝 టెక్స్ట్ సమ్మరైజర్ (Summarizer)"
])

if choice == "💬 జనరల్ చాట్ & ఫైల్ విశ్లేషణ (General Chat)":
    st.header("💬 General AI Chat & Multimodal Analysis")
    question = st.text_area("మీ ప్రశ్నను టైప్ చేయండి (ఏ భాషలోనైనా):")
    exam_type = st.selectbox("కేటగిరీ:", ["General", "Education", "Technical", "Science"])
    uploaded_file = st.file_uploader("ఫోటో లేదా డాక్యుమెంట్ అప్‌లోడ్ చేయండి:", type=["jpg", "png", "jpeg", "pdf", "txt"])
    
    if st.button("ప్రశ్న పంపు"):
        with st.spinner("ఏఐ సమాధానం ఇస్తోంది..."):
            files = {"file": uploaded_file.getvalue()} if uploaded_file else None
            data = {"question": question, "exam_type": exam_type}
            try:
                res = requests.post(f"{BACKEND_URL}/check", data=data, files=files)
                if res.status_code == 200:
                    st.success("సమాధానం:")
                    st.write(res.json().get("response"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "🎬 స్టోరీ టూ మూవీ / రీల్స్ (Story to Movie)":
    st.header("🎬 Story to Movie & Reels Generator")
    story_plot = st.text_area("మీ కథ లేదా ప్లాట్‌ను ఇక్కడ చెప్పండి (సినిమా లేదా రీల్స్ కోసం):")
    output_format = st.selectbox("ఫార్మాట్:", ["Full Movie Script & Scene Breakdown", "Short Film", "Instagram Reels Plan"])
    
    if st.button("సినిమా/రీల్స్ స్క్రిప్ట్ తయారు చేయి"):
        with st.spinner("సినిమా స్క్రిప్ట్ రూపొందించబడుతోంది..."):
            data = {"story_plot": story_plot, "output_format": output_format}
            try:
                res = requests.post(f"{BACKEND_URL}/story-to-movie", data=data)
                if res.status_code == 200:
                    st.success("ప్రొడక్షన్ ప్లాన్ & స్క్రిప్ట్:")
                    st.write(res.json().get("cinematic_production_plan"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "💻 యాప్ & వెబ్‌సైట్ బిల్డింగ్ (App/Web Builder)":
    st.header("💻 App & Website Code Generator")
    project_desc = st.text_area("మీకు కావలసిన యాప్ లేదా వెబ్‌సైట్ వివరాలు తెలపండి:")
    target_platform = st.selectbox("ప్లాట్‌ఫారమ్:", ["Web Website", "Mobile App (Android/iOS)", "FastAPI Backend"])
    
    if st.button("కోడ్ జనరేట్ చేయి"):
        with st.spinner("కోడ్ తయారవుతోంది..."):
            data = {"project_description": project_desc, "target_platform": target_platform}
            try:
                res = requests.post(f"{BACKEND_URL}/build-app-web", data=data)
                if res.status_code == 200:
                    st.success("జనరేట్ చేయబడిన కోడ్ & గైడ్:")
                    st.code(res.json().get("generated_solution"), language="python")
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "🐍 పైథాన్ మెంటార్ & కోడింగ్ (Python Tutor)":
    st.header("🐍 Python Programming & Learning Tutor")
    topic_error = st.text_area("పైథాన్ టాపిక్ పేరు లేదా మీ కోడ్ ఎర్రర్‌ని ఇక్కడ ఇవ్వండి:")
    mode = st.selectbox("మోడ్:", ["Learn Topic", "Fix Bug", "Write Code"])
    
    if st.button("సహాయం పొందండి"):
        with st.spinner("పైథాన్ మెంటార్ పరిశీలిస్తున్నారు..."):
            data = {"learning_topic_or_code_error": topic_error, "mode": mode}
            try:
                res = requests.post(f"{BACKEND_URL}/python-mentor", data=data)
                if res.status_code == 200:
                    st.success("పైథాన్ గైడెన్స్:")
                    st.write(res.json().get("python_guidance"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "🎨 డిజైన్ & యాడ్స్ బ్యానర్స్ (Design & Ads)":
    st.header("🎨 Image, Drawing & Ad Design Concepts")
    concept = st.text_area("మీకు కావలసిన డిజైన్ లేదా యాడ్ కాన్సెప్ట్ గురించి రాయండి:")
    category = st.selectbox("రకం:", ["Social Media Ad Banner", "Logo Design", "Drawing Concept", "Product Packaging"])
    
    if st.button("డిజైన్ ప్లాన్ పొందండి"):
        with st.spinner("డిజైన్ గైడ్ రూపొందుతోంది..."):
            data = {"design_concept": concept, "category": category}
            try:
                res = requests.post(f"{BACKEND_URL}/design-ads", data=data)
                if res.status_code == 200:
                    st.success("డిజైన్ గైడ్:")
                    st.write(res.json().get("design_guide"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "🎥 వీడియో క్రియేటర్ & స్క్రిప్ట్స్ (Video Creator)":
    st.header("🎥 Video Editor & YouTube Script Creator")
    v_topic = st.text_area("వీడియో టాపిక్ లేదా టైటిల్ ఇవ్వండి:")
    v_type = st.selectbox("వీడియో రకం:", ["YouTube Video Script & Editing Plan", "Reels/Shorts Plan", "Cinematic Storyboard"])
    
    if st.button("వీడియో ప్లాన్ సృష్టించు"):
        with st.spinner("స్క్రిప్ట్ తయారవుతోంది..."):
            data = {"video_topic": v_topic, "video_type": v_type}
            try:
                res = requests.post(f"{BACKEND_URL}/video-creator", data=data)
                if res.status_code == 200:
                    st.success("వీడియో & స్క్రిప్ట్ ప్లాన్:")
                    st.write(res.json().get("video_plan"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "📈 బిజినెస్ & ఫుడ్ ట్రిక్స్ (Business & Food)":
    st.header("📈 Business Growth & Food Industry Tricks")
    b_idea = st.text_area("మీ బిజినెస్ లేదా ఫుడ్ ప్రొడక్ట్ ఐడియా (ఉదాహరణకు: మిల్ట్-బేస్డ్ స్నాక్స్) గురించి రాయండి:")
    goal = st.selectbox("లక్ష్యం:", ["Growth and Marketing", "Packaging & Branding", "Revenue Roadmap"])
    
    if st.button("స్ట్రాటజీ పొందండి"):
        with st.spinner("బిజినెస్ ప్లాన్ రూపొందుతోంది..."):
            data = {"business_idea": b_idea, "goal": goal}
            try:
                res = requests.post(f"{BACKEND_URL}/business-tricks", data=data)
                if res.status_code == 200:
                    st.success("బిజినెస్ & మార్కెటింగ్ స్ట్రాటజీ:")
                    st.write(res.json().get("business_strategy"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "🔧 రోబోటిక్స్ & లాప్‌టాప్ రిపేర్ (Repair Tech)":
    st.header("🔧 Robotics, Computer & Laptop Repair Guide")
    issue = st.text_area("సమస్య లేదా డివైైస్ పేరు (లేదా రోబోటిక్స్ ప్రాజెక్ట్ వివరాలు) తెలపండి:")
    domain = st.selectbox("డొమైన్:", ["Laptop/Computer Repair", "Robotics Making", "Software Troubleshooting"])
    
    if st.button("ట్రబుల్‌షూటింగ్ గైడ్ పొందండి"):
        with st.spinner("పరిష్ారం వెతుకుతోంది..."):
            data = {"issue_or_device": issue, "domain": domain}
            try:
                res = requests.post(f"{BACKEND_URL}/repair-tech", data=data)
                if res.status_code == 200:
                    st.success("టెక్నికల్ రిపేర్ గైడ్:")
                    st.write(res.json().get("repair_solution"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "👔 రెజ్యూమ్ & ఇంటర్వ్యూ కోచ్ (Career Coach)":
    st.header("👔 Resume Builder & Interview Preparation")
    role = st.text_area("ఉద్యోగ హోదా (Job Role) ఇవ్వండి:")
    req_type = st.selectbox("కావలసిన సేవ:", ["Interview Questions & Answers", "Resume Summary & Highlights", "Career Roadmap"])
    
    if st.button("గైడెన్స్ పొందండి"):
        with st.spinner("కెరీర్ గైడ్ తయారవుతోంది..."):
            data = {"job_role": role, "request_type": req_type}
            try:
                res = requests.post(f"{BACKEND_URL}/career-coach", data=data)
                if res.status_code == 200:
                    st.success("కెరీర్ సలహాలు:")
                    st.write(res.json().get("career_guidance"))
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

elif choice == "📝 టెక్స్ట్ సమ్మరైజర్ (Summarizer)":
    st.header("📝 Document & Long Text Summarizer")
    text_data = st.text_area("పెద్ద ఆర్టికల్ లేదా టెక్స్ట్ ని ఇక్కడ పేస్ట్ చేయండి:")
    
    if st.button("సారాంశం తయారు చేయి"):
        with st.spinner("సారాంశం రూపొందుతోంది..."):
            data = {"long_text": text_data}
            try:
                res = requests.post(f"{BACKEND_URL}/summarizer", data=data)
                if res.status_code == 200:
                    st.success("ముఖ్యమైన ముఖ్యాంశాలు (Summary):")
                    st.write(res.json().get("summary"))
            except Exception as e:
                    st.error(f"ఎర్రర్: {e}")
