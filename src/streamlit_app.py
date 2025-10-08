# src/streamlit_app.py
import streamlit as st
import soundfile as sf
from scraper import run as scrape
from versioning import add_version
from agents.voice_api import speech_to_text
from agents.ai_reviewer import ReviewerAgent
from agents.ai_writer import WriterAgent
from rl_reward import calculate_text_reward
from rl_search import rl_based_search
from audio_recorder_streamlit import audio_recorder
import asyncio, edge_tts, base64, tempfile, base64, shutil, sys, os
sys.path.append(os.path.abspath(os.path.join(__file__,"..","..")))


async def synthesize(text):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save("output.mp3")

def text_to_speech(text):
    asyncio.run(synthesize(text))
    with open("output.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

def convert_audio(path):
    data, sr = sf.read(path)          
    mono = data.mean(axis=1) if data.ndim > 1 else data
    out  = path.replace(".wav", "_mono.wav")
    sf.write(out, mono, 16000)
    return out

iconpath = r"https://github.com/Kratugautam99/Scriptoria-Project/blob/main/data/logo/icon.png?raw=true"
col_icon, col_title = st.columns([1, 8], gap="small")

with col_icon:
    st.image(iconpath, width=100)        

with col_title:
    st.markdown(
        "<h1 style='margin: 0; color: white;'>"
        "Scriptoria: Automated Book Publication Workflow"
        "</h1>",
        unsafe_allow_html=True
    )


css = """
<style>
  /* 1. Background: stripes over red→black */
  .stApp {
    background-image:
      repeating-linear-gradient(
        45deg,
        rgba(255, 255, 255, 0.1) 0,
        rgba(255, 255, 255, 0.1) 10px,
        transparent 10px,
        transparent 20px
      ),
      linear-gradient(to bottom right, #b30000, #000000);
    background-attachment: fixed !important;
  }

  /* 2. Sidebar: same background + black overlay for panels */
  [data-testid="stSidebar"] {
    background-image:
      repeating-linear-gradient(
        45deg,
        rgba(255, 255, 255, 0.1) 0,
        rgba(255, 255, 255, 0.1) 10px,
        transparent 10px,
        transparent 20px
      ),
      linear-gradient(to bottom right, #b30000, #000000) !important;
  }
  [data-testid="stSidebar"] .css-1d391kg {
    background-color: rgba(0, 0, 0, 0.85) !important;
  }

  /* 3. Buttons: deep black with white text */
  .stButton button,
  .stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
  }

  /* 4. Text inputs & areas: deep black fields */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stNumberInput"] input {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
  }

  /* 5. Selectboxes & multiselects: black dropdown panels */
  [data-testid="stSelectbox"] .css-1hynsfm,
  [data-testid="stMultiselect"] .css-1hynsfm {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
  }

  /* 6. Optional: dark scrollbar (WebKit) */
  .stApp ::-webkit-scrollbar {
    width: 8px;
  }
  .stApp ::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.7) !important;
    border-radius: 4px;
  }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

WA = WriterAgent(api_key=os.getenv("GEMINI_API_KEY"))
RA = ReviewerAgent(api_key=os.getenv("GEMINI_API_KEY"))

if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.content = ""        
    st.session_state.screenshot = ""     
    st.session_state.review = ""         
    st.session_state.score = 0.0         
    st.session_state.writer_out = ""
    st.session_state.humantxt = ""
    st.session_state.tts_pid = None
    st.session_state.raw = ""
    st.session_state.query = ""
    st.session_state.version = 1
    st.session_state.rlresult = ""


# STEP 1: Ask for URL + chapter name
if st.session_state.step == 1:
    url = st.text_input("1. Enter URL", key="url1")
    name = st.text_input("2. Enter Name/ID", key="name1")
    rlvar = st.text_input("3. RL Search Query", key="rlvar1")
    if st.button("▶️ Start Workflow",key="start1"):
        if not url or not name or not rlvar:
            st.error("Please provide URL, Name and RL Variable.")
        else:
            with st.spinner("🔍 Scraping & Screenshotting…"):
                st.session_state.content = scrape(url, name)
                st.session_state.raw = scrape(url, name, lol="html")
                st.session_state.query = rlvar
                add_version("original", st.session_state.content)
                st.session_state.rlresult = rl_based_search(url, name, rlvar, 2)
            st.session_state.screenshot = f"data/screenshots/{name}.png"
            st.session_state.step = 2
            st.rerun()

# STEP 2: Show screenshot only
elif st.session_state.step == 2:
    st.subheader("🌄 Scraped Screenshot")
    st.image(st.session_state.screenshot, use_container_width=True)
    st.subheader("**RL Based Search Result:**")
    result = st.session_state.rlresult
    st.write(result["final_answer"])
    st.subheader("Query Attempts")
    for attempt in result["query_attempts"]:
        st.markdown(f"**Round {attempt['round']}** | Query: `{attempt['query']}`")
        st.write(attempt["result"][:200] + "...")
    if st.button("▶️ Continue to Review", key="cont2"):
        st.session_state.step = 3
        st.rerun()

# STEP 3: AI Reviewer + RL reward
elif st.session_state.step == 3:
    st.subheader("🤖 AI Review & Scoring")
    with st.spinner("Reviewing…"):
        st.session_state.review = RA.review_chapter(st.session_state.content)
        add_version(f"Review-Version-{st.session_state.version}", st.session_state.review)
        if st.session_state.humantxt:
            st.session_state.score = calculate_text_reward(original=st.session_state.content, rewritten=st.session_state.writer_out)
        else:
            st.session_state.score = calculate_text_reward(original=st.session_state.content)
    if st.session_state.humantxt:
        st.markdown("**AI Review of Previously Generated Content:**\n\n")
    else:
        st.markdown("**AI Review of Original Content:**\n\n")
    st.write(st.session_state.review)
    st.markdown(f"**Content Score:** `{st.session_state.score:.3f}`")
    if st.button("▶️ Rewrite Beautifully",key="rewrite3"):
        st.session_state.step = 4
        st.rerun()

# STEP 4: AI Writer + TTS button
elif st.session_state.step == 4:
    st.subheader("✍️ AI-Writer Output")
    with st.spinner("Loading function from button…"):
        base = st.session_state.writer_out or st.session_state.content
        st.session_state.writer_out = WA.spin_chapter(base, human_feedback=st.session_state.humantxt)
        add_version(f"Writer-Version-{st.session_state.version}", st.session_state.writer_out)
        st.session_state.version += 1
        text_to_speech(st.session_state.writer_out)
    if st.session_state.humantxt:
        st.write("📝 Rewritten Text from Human Input:\n\n", st.session_state.writer_out)
    else:
        st.write("📝 Rewritten Text from Original Content:\n\n" , st.session_state.writer_out)
    st.session_state.score = calculate_text_reward(original=st.session_state.content, rewritten=st.session_state.writer_out)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Content Score:** `{st.session_state.score:.3f}`")
    with col2:
        if st.button("▶️ Provide Human Edits", key="edit4"):
            st.session_state.step = 5
            st.rerun()

# STEP 5: Human-in-the-loop iteration
elif st.session_state.step == 5:
    st.subheader("🖊️ Human Feedback")
    st.markdown("""
        <style>
            /* Container for the radio group */
            div[role="radiogroup"] {
                background: transparent;
                border-radius: 10px;
                padding: 10px;
            }

            /* Make each label full-width and consistent size */
            div[role="radiogroup"] > label {
                display: block;
                width: 100% !important;
                min-height: 60px;
                background: linear-gradient(135deg, #660000, #000000);
                color: #fff;
                padding: 15px 20px;
                margin: 10px 0;
                border-radius: 12px;
                cursor: pointer;
                font-size: 18px;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                transition: transform 0.2s ease, background 0.3s ease;
                text-align: center;
            }

            /* Hover effect */
            div[role="radiogroup"] > label:hover {
                transform: scale(1.02);
                background: linear-gradient(135deg, #990000, #111111);
            }

            /* Selected button styling */
            div[role="radiogroup"] > label[data-selected="true"] {
                background: linear-gradient(135deg, #e8b62c, #8B0000);
                color: black !important;
                transform: scale(1.03);
            }
        </style>
    """, unsafe_allow_html=True)
    choice = st.radio("How would you like to edit?", 
                    ("Enter Text", "Record Audio", "No more edits"))


    
    if choice == "Enter Text":
        st.session_state.humantxt = st.text_area("Please edit the AI text:", st.session_state.humantxt, key="textarea5")
        if st.button("✅ Submit Text Edits", key="submit5"):
            st.session_state.step = 3
            st.rerun()

    elif choice == "Record Audio":
        st.markdown("<p style='font-size:18px; font-weight:bold;'>Click to Record (Microphone, Earphone, Headphone Recommended)</p>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="",                            
            icon_name="microphone-alt",         
            icon_size="2x",                     
            neutral_color="#B7F115",           
            recording_color="#0aaffc",         
            sample_rate=16000,                  
            pause_threshold=1,                  
            key="recorder")
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                temp_path = f.name

            st.audio(audio_bytes, format="audio/wav")

            try:
                converted_path = convert_audio(temp_path)
                transcript = speech_to_text(converted_path)
                st.text_area("Transcript", transcript)
                if st.button("✅ Submit Audio Edits", key="submit_audio5"):
                    st.session_state.humantxt = transcript
                    st.session_state.step = 3
                    st.rerun()
            except Exception as e:
                st.error(f"Speech recognition failed: {e}")


    else:
        if st.button("🏁 Finish & Exit", key="finish5"):
            st.session_state.step = 6      
            st.rerun()

elif st.session_state.step == 6:
    st.markdown("<h2 style='text-align: center;'>🎉 Thank You for using Scriptoria!! 🎉</h2>", unsafe_allow_html=True)
    st.button("🔄 Restart Workflow", on_click=lambda: st.session_state.clear(), key="restart6")
    folder_path = "chromadb"
    if os.path.exists(folder_path):
        if st.button("💀 Delete Versioning Folder"):
            try:
                shutil.rmtree(folder_path)
                st.success(f"✅ Folder deleted: {folder_path}")
            except Exception as e:
                st.error(f"❌ Folder in Use")
    else:
        st.warning("⚠️ Folder does not exist.")