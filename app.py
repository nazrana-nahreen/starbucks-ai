import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime, date
import time
import folium
from streamlit_folium import st_folium

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="মনের কথা | Moner Kotha",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STYLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@300;400;500;600;700&display=swap');

* { font-family: 'Hind Siliguri', sans-serif; }

.main { background: #0f1117; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f2e 0%, #0f1117 100%);
    border-right: 1px solid #2d3748;
}

/* Nav buttons */
.nav-btn {
    width: 100%;
    padding: 12px 16px;
    margin: 4px 0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    color: #a0aec0;
    text-align: left;
    cursor: pointer;
    font-size: 15px;
    transition: all 0.2s;
}
.nav-btn:hover, .nav-btn.active {
    background: rgba(99, 179, 237, 0.1);
    border-color: #63b3ed;
    color: #63b3ed;
}

/* Cards */
.card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
}

/* Chat bubbles */
.user-bubble {
    background: linear-gradient(135deg, #3182ce, #2b6cb0);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    max-width: 75%;
    margin-left: auto;
    text-align: right;
}
.bot-bubble {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    color: #e2e8f0;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    max-width: 75%;
}

/* Mood buttons */
.mood-btn {
    font-size: 28px;
    padding: 10px;
    cursor: pointer;
    border-radius: 50%;
    transition: transform 0.2s;
}
.mood-btn:hover { transform: scale(1.3); }

/* Doctor card */
.doctor-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    transition: border-color 0.2s;
}
.doctor-card:hover { border-color: #63b3ed; }

/* Crisis banner */
.crisis-banner {
    background: linear-gradient(135deg, #c53030, #9b2c2c);
    border-radius: 12px;
    padding: 16px 20px;
    color: white;
    margin: 8px 0;
}

/* Breathing circle */
@keyframes breathe {
    0%, 100% { transform: scale(1); opacity: 0.7; }
    50% { transform: scale(1.4); opacity: 1; }
}
.breath-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, #63b3ed, #2b6cb0);
    animation: breathe 8s ease-in-out infinite;
    margin: 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
    text-align: center;
}

/* Title */
.app-title {
    font-size: 28px;
    font-weight: 700;
    color: #63b3ed;
    text-align: center;
    padding: 10px 0;
}
.app-subtitle {
    font-size: 14px;
    color: #718096;
    text-align: center;
    margin-bottom: 20px;
}

/* Metric cards */
.metric-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.metric-number { font-size: 32px; font-weight: 700; color: #63b3ed; }
.metric-label { font-size: 12px; color: #718096; }

/* Journal */
.journal-entry {
    background: #1a1f2e;
    border-left: 3px solid #63b3ed;
    border-radius: 0 12px 12px 0;
    padding: 16px;
    margin: 8px 0;
    color: #e2e8f0;
}

/* Section header */
.section-header {
    font-size: 22px;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2d3748;
}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def init_db():
    conn = sqlite3.connect("moner_kotha.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS mood_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mood_score INTEGER,
        mood_emoji TEXT,
        note TEXT,
        log_date DATE DEFAULT CURRENT_DATE
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_message(session_id, role, message):
    conn = sqlite3.connect("moner_kotha.db")
    c = conn.cursor()
    c.execute("INSERT INTO chats (session_id, role, message) VALUES (?,?,?)",
              (session_id, role, message))
    conn.commit()
    conn.close()

def get_messages(session_id):
    conn = sqlite3.connect("moner_kotha.db")
    df = pd.read_sql("SELECT role, message FROM chats WHERE session_id=? ORDER BY timestamp",
                     conn, params=(session_id,))
    conn.close()
    return df

def get_recent_sessions():
    conn = sqlite3.connect("moner_kotha.db")
    df = pd.read_sql("""SELECT DISTINCT session_id, MIN(message) as preview, MAX(timestamp) as last_time
                        FROM chats WHERE role='user'
                        GROUP BY session_id ORDER BY last_time DESC LIMIT 5""", conn)
    conn.close()
    return df

def save_mood(score, emoji, note):
    conn = sqlite3.connect("moner_kotha.db")
    c = conn.cursor()
    c.execute("INSERT INTO mood_logs (mood_score, mood_emoji, note) VALUES (?,?,?)",
              (score, emoji, note))
    conn.commit()
    conn.close()

def get_mood_history():
    conn = sqlite3.connect("moner_kotha.db")
    df = pd.read_sql("SELECT * FROM mood_logs ORDER BY log_date DESC LIMIT 14", conn)
    conn.close()
    return df

def save_journal(title, content):
    conn = sqlite3.connect("moner_kotha.db")
    c = conn.cursor()
    c.execute("INSERT INTO journals (title, content) VALUES (?,?)", (title, content))
    conn.commit()
    conn.close()

def get_journals():
    conn = sqlite3.connect("moner_kotha.db")
    df = pd.read_sql("SELECT * FROM journals ORDER BY created_at DESC", conn)
    conn.close()
    return df

init_db()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚠️ MODEL LOADING — এখানে তোমার model বসাও
# Fine-tuning শেষে এই অংশ uncomment করো
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# @st.cache_resource
# def load_model():
#     import torch
#     from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
#     from peft import PeftModel
#
#     MODEL_PATH = "./bangla-mental-health-model"  # ← তোমার model folder
#     BASE_MODEL  = "meta-llama/Meta-Llama-3.1-8B"
#
#     bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
#     base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb, device_map="auto")
#     model = PeftModel.from_pretrained(base, MODEL_PATH)
#     model.eval()
#     return tokenizer, model
#
# tokenizer, model = load_model()
#
# def get_ai_response(user_input):
#     SYSTEM = "আপনি একজন সহানুভূতিশীল মানসিক স্বাস্থ্য পরামর্শদাতা।"
#     prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{SYSTEM}<|eot_id|>\n<|start_header_id|>user<|end_header_id|>\n{user_input}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n"
#     inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
#     with torch.no_grad():
#         output = model.generate(**inputs, max_new_tokens=300, temperature=0.7, do_sample=True)
#     decoded = tokenizer.decode(output[0], skip_special_tokens=True)
#     return decoded.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()

# Model না থাকলে এই demo response ব্যবহার করো
def get_ai_response(user_input):
    responses = [
        "আপনার কথা শুনে আমি বুঝতে পারছি আপনি এখন কঠিন সময়ের মধ্যে আছেন। আপনি একা নন, আমি আপনার পাশে আছি। 💙",
        "আপনার অনুভূতি সম্পূর্ণ স্বাভাবিক। এই কষ্ট সাময়িক। আমরা একসাথে এর সমাধান খুঁজে বের করতে পারি।",
        "আপনি অনেক সাহসী যে আপনার মনের কথা শেয়ার করছেন। এটা প্রথম ও সবচেয়ে গুরুত্বপূর্ণ পদক্ষেপ।",
    ]
    import random
    return random.choice(responses)

# Crisis keywords
CRISIS_WORDS = ["মরতে চাই", "আত্মহত্যা", "বাঁচতে চাই না", "শেষ করতে চাই", "মরে যেতে চাই"]

def is_crisis(text):
    return any(word in text for word in CRISIS_WORDS)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOCTOR DATA (Bangladesh)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOCTORS = {
    "ঢাকা": [
        {"নাম": "ডা. মোহিত কামাল", "hospital": "জাতীয় মানসিক স্বাস্থ্য ইন্সটিটিউট (NIMH)", "phone": "02-9113456", "address": "শেরেবাংলা নগর, ঢাকা", "lat": 23.7749, "lon": 90.3668},
        {"নাম": "ডা. হেলাল উদ্দিন আহমেদ", "hospital": "বঙ্গবন্ধু শেখ মুজিব মেডিকেল", "phone": "02-9661060", "address": "শাহবাগ, ঢাকা", "lat": 23.7394, "lon": 90.3964},
        {"নাম": "ডা. মেখলা সরকার", "hospital": "স্কয়ার হাসপাতাল", "phone": "02-8159457", "address": "পান্থপথ, ঢাকা", "lat": 23.7516, "lon": 90.3856},
        {"নাম": "ডা. সালাহউদ্দিন কাউসার বিপ্লব", "hospital": "ইউনাইটেড হাসপাতাল", "phone": "02-8836000", "address": "গুলশান, ঢাকা", "lat": 23.7957, "lon": 90.4125},
    ],
    "চট্টগ্রাম": [
        {"নাম": "ডা. আরাফাত আজিম", "hospital": "চট্টগ্রাম মেডিকেল কলেজ", "phone": "01706-333677", "address": "পাঁচলাইশ, চট্টগ্রাম", "lat": 22.3569, "lon": 91.7832},
        {"নাম": "ডা. ফারহানা রহমান", "hospital": "মনোনিবাশ মানসিক হাসপাতাল", "phone": "031-2551234", "address": "নাসিরাবাদ, চট্টগ্রাম", "lat": 22.3475, "lon": 91.8123},
        {"নাম": "ডা. শাহজাহান কবীর", "hospital": "চট্টগ্রাম জেনারেল হাসপাতাল", "phone": "031-615213", "address": "আন্দরকিল্লা, চট্টগ্রাম", "lat": 22.3355, "lon": 91.8345},
    ],
    "সিলেট": [
        {"নাম": "ডা. রেজাউল করিম", "hospital": "সিলেট ওসমানী মেডিকেল কলেজ", "phone": "0821-716474", "address": "আম্বরখানা, সিলেট", "lat": 24.8949, "lon": 91.8687},
        {"নাম": "ডা. নাজনীন আক্তার", "hospital": "নর্থ ইস্ট মেডিকেল কলেজ", "phone": "0821-2830022", "address": "বন্দরবাজার, সিলেট", "lat": 24.9045, "lon": 91.8611},
    ],
    "রাজশাহী": [
        {"নাম": "ডা. মাহবুবুল হক", "hospital": "রাজশাহী মেডিকেল কলেজ", "phone": "0721-772150", "address": "লক্ষ্মীপুর, রাজশাহী", "lat": 24.3745, "lon": 88.6042},
        {"নাম": "ডা. শিরীন সুলতানা", "hospital": "পপুলার ডায়াগনস্টিক", "phone": "0721-811600", "address": "সাহেব বাজার, রাজশাহী", "lat": 24.3636, "lon": 88.5954},
    ],
    "কুমিল্লা": [
        {"নাম": "ডা. আনোয়ার হোসেন", "hospital": "কুমিল্লা মেডিকেল কলেজ", "phone": "081-76222", "address": "কোটবাড়ি, কুমিল্লা", "lat": 23.4607, "lon": 91.1809},
        {"নাম": "ডা. রোকেয়া বেগম", "hospital": "কুমিল্লা জেনারেল হাসপাতাল", "phone": "081-72019", "address": "কান্দিরপাড়, কুমিল্লা", "lat": 23.4589, "lon": 91.1772},
    ],
    "খুলনা": [
        {"নাম": "ডা. শেখ রাসেল", "hospital": "খুলনা মেডিকেল কলেজ", "phone": "041-760029", "address": "মুজগুন্নি, খুলনা", "lat": 22.8456, "lon": 89.5403},
    ],
    "ময়মনসিংহ": [
        {"নাম": "ডা. আবুল কাশেম", "hospital": "ময়মনসিংহ মেডিকেল কলেজ", "phone": "091-66602", "address": "চরপাড়া, ময়মনসিংহ", "lat": 24.7471, "lon": 90.4203},
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "page" not in st.session_state:
    st.session_state.page = "চ্যাট"
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown('<div class="app-title">💙 মনের কথা</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Moner Kotha — AI Mental Health Support</div>', unsafe_allow_html=True)
    st.markdown("---")

    pages = ["💬 চ্যাট", "😊 মুড ট্র্যাকার", "🧘 শ্বাস-প্রশ্বাস", "📔 জার্নাল", "🗺️ মনের ডাক্তার", "🆘 জরুরি সাহায্য"]
    for p in pages:
        name = p.split(" ", 1)[1]
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = name

    st.markdown("---")

    # Recent chats
    st.markdown("**🕐 সাম্প্রতিক চ্যাট**")
    sessions = get_recent_sessions()
    if not sessions.empty:
        for _, row in sessions.iterrows():
            preview = str(row["preview"])[:30] + "..."
            if st.button(f"💬 {preview}", key=row["session_id"], use_container_width=True):
                st.session_state.session_id = row["session_id"]
                msgs = get_messages(row["session_id"])
                st.session_state.messages = msgs.to_dict("records")
                st.session_state.page = "চ্যাট"

    if st.button("➕ নতুন চ্যাট", use_container_width=True):
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.session_state.page = "চ্যাট"

    st.markdown("---")
    st.markdown("📞 **কান পেতে রই:** 01779-554391")
    st.markdown("📞 **NIMH:** 16789")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
page = st.session_state.page

# ── 1. CHAT ──────────────────────────────────
if page == "চ্যাট":
    st.markdown('<div class="section-header">💬 AI মানসিক স্বাস্থ্য সহায়তা</div>', unsafe_allow_html=True)
    st.warning("⚠️ এটি পেশাদার চিকিৎসার বিকল্প নয়। গুরুতর সমস্যায় বিশেষজ্ঞের পরামর্শ নিন।")

    # Messages display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="bot-bubble">
            আস্সালামু আলাইকুম! আমি আপনার মানসিক স্বাস্থ্য সহায়তাকারী। 
            আপনার মনের কথা আমাকে বলুন, আমি সবসময় আপনার পাশে আছি। 💙
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{msg["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-bubble">{msg["message"]}</div>', unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("আপনার মনের কথা বলুন... (বাংলায় লিখুন)")

    if user_input:
        # Crisis check
        if is_crisis(user_input):
            st.markdown("""
            <div class="crisis-banner">
            ⚠️ আপনি এখন অনেক কঠিন সময়ে আছেন। দয়া করে এখনই সাহায্য নিন:<br>
            📞 কান পেতে রই: <b>01779-554391</b><br>
            📞 NIMH হেল্পলাইন: <b>16789</b>
            </div>
            """, unsafe_allow_html=True)

        # Save & display user message
        st.session_state.messages.append({"role": "user", "message": user_input})
        save_message(st.session_state.session_id, "user", user_input)

        # Get AI response
        with st.spinner("ভাবছি..."):
            response = get_ai_response(user_input)

        st.session_state.messages.append({"role": "bot", "message": response})
        save_message(st.session_state.session_id, "bot", response)
        st.rerun()

# ── 2. MOOD TRACKER ───────────────────────────
elif page == "মুড ট্র্যাকার":
    st.markdown('<div class="section-header">😊 মুড ট্র্যাকার</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### আজকে আপনি কেমন আছেন?")

        moods = [("😭", "খুব খারাপ", 1), ("😢", "খারাপ", 3), ("😐", "ঠিকঠাক", 5), ("🙂", "ভালো", 7), ("😄", "খুব ভালো", 10)]

        selected_mood = None
        cols = st.columns(5)
        for i, (emoji, label, score) in enumerate(moods):
            with cols[i]:
                if st.button(emoji, key=f"mood_{i}", help=label):
                    selected_mood = (emoji, label, score)

        note = st.text_area("কেন এরকম অনুভব করছেন? (ঐচ্ছিক)", height=100)

        if selected_mood and st.button("✅ সেভ করুন", use_container_width=True):
            save_mood(selected_mood[2], selected_mood[0], note)
            st.success(f"{selected_mood[0]} মুড সেভ হয়েছে!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 গত ১৪ দিনের মুড")
        mood_data = get_mood_history()
        if not mood_data.empty:
            mood_data["log_date"] = pd.to_datetime(mood_data["log_date"])
            st.line_chart(mood_data.set_index("log_date")["mood_score"])
        else:
            st.info("এখনো কোনো মুড লগ নেই। আজকের মুড যোগ করুন!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    mood_data = get_mood_history()
    if not mood_data.empty:
        st.markdown("### 📊 আপনার মুড সারসংক্ষেপ")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{mood_data["mood_score"].mean():.1f}</div><div class="metric-label">গড় মুড স্কোর</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{len(mood_data)}</div><div class="metric-label">মোট লগ এন্ট্রি</div></div>', unsafe_allow_html=True)
        with c3:
            best = mood_data.loc[mood_data["mood_score"].idxmax(), "mood_emoji"]
            st.markdown(f'<div class="metric-card"><div class="metric-number">{best}</div><div class="metric-label">সেরা দিনের মুড</div></div>', unsafe_allow_html=True)

# ── 3. BREATHING ──────────────────────────────
elif page == "শ্বাস-প্রশ্বাস":
    st.markdown('<div class="section-header">🧘 শ্বাস-প্রশ্বাস ব্যায়াম</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        technique = st.selectbox("কৌশল বেছে নিন:", [
            "4-7-8 (ঘুমের জন্য)",
            "বক্স ব্রিদিং (মনোযোগের জন্য)",
            "৪-৪ (স্ট্রেস কমাতে)"
        ])

        if technique == "4-7-8 (ঘুমের জন্য)":
            steps = [("শ্বাস নিন", 4), ("ধরে রাখুন", 7), ("ছাড়ুন", 8)]
            desc = "৪ সেকেন্ড শ্বাস নিন → ৭ সেকেন্ড ধরুন → ৮ সেকেন্ড ছাড়ুন"
        elif technique == "বক্স ব্রিদিং (মনোযোগের জন্য)":
            steps = [("শ্বাস নিন", 4), ("ধরুন", 4), ("ছাড়ুন", 4), ("ধরুন", 4)]
            desc = "৪-৪-৪-৪ pattern — মনোযোগ বাড়ায়"
        else:
            steps = [("শ্বাস নিন", 4), ("ছাড়ুন", 4)]
            desc = "৪ সেকেন্ড নিন → ৪ সেকেন্ড ছাড়ুন"

        st.info(desc)
        rounds = st.slider("কতবার করবেন?", 1, 10, 3)

    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 30px;">
            <div class="breath-circle">শ্বাস<br>নিন</div>
            <p style="color:#718096; margin-top:20px;">Circle এর সাথে শ্বাস নিন</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("▶️ শুরু করুন", use_container_width=True):
        progress = st.empty()
        instruction = st.empty()
        for r in range(rounds):
            for action, secs in steps:
                for i in range(secs, 0, -1):
                    instruction.markdown(f"### {action} — {i} সেকেন্ড")
                    progress.progress((secs - i + 1) / secs)
                    time.sleep(1)
            if r < rounds - 1:
                instruction.markdown("### বিরতি...")
                time.sleep(1)
        instruction.markdown("### ✅ সম্পন্ন! অনেক ভালো করেছেন! 🌟")
        st.balloons()

# ── 4. JOURNAL ────────────────────────────────
elif page == "জার্নাল":
    st.markdown('<div class="section-header">📔 মনের ডায়েরি</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### নতুন এন্ট্রি লিখুন")
        title = st.text_input("শিরোনাম", placeholder="আজকের অনুভূতি...")
        content = st.text_area("আপনার মনের কথা লিখুন...", height=250,
                               placeholder="আজকে আমি...")
        if st.button("💾 সেভ করুন", use_container_width=True):
            if content:
                save_journal(title or "শিরোনামহীন", content)
                st.success("✅ ডায়েরি সেভ হয়েছে!")
                st.rerun()
            else:
                st.error("কিছু লিখুন!")

    with col2:
        st.markdown("### 📚 আগের এন্ট্রি")
        journals = get_journals()
        if not journals.empty:
            for _, j in journals.iterrows():
                date_str = pd.to_datetime(j["created_at"]).strftime("%d %b %Y")
                st.markdown(f"""
                <div class="journal-entry">
                    <strong>{j['title']}</strong>
                    <small style="color:#718096; float:right">{date_str}</small><br>
                    <span style="color:#a0aec0">{j['content'][:150]}...</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("এখনো কোনো এন্ট্রি নেই।")

# ── 5. DOCTOR FINDER ──────────────────────────
elif page == "মনের ডাক্তার":
    st.markdown('<div class="section-header">🗺️ মনের ডাক্তার খুঁজুন</div>', unsafe_allow_html=True)
    st.info("আপনার জেলা বেছে নিন — সেই এলাকার মানসিক স্বাস্থ্য বিশেষজ্ঞদের তথ্য দেখাবে।")

    district = st.selectbox("জেলা বেছে নিন:", list(DOCTORS.keys()))

    if district:
        doctors = DOCTORS[district]

        # Map
        center_lat = doctors[0]["lat"]
        center_lon = doctors[0]["lon"]
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13,
                       tiles="CartoDB dark_matter")

        for doc in doctors:
            folium.Marker(
                location=[doc["lat"], doc["lon"]],
                popup=folium.Popup(f"<b>{doc['নাম']}</b><br>{doc['hospital']}<br>📞 {doc['phone']}", max_width=200),
                tooltip=doc["নাম"],
                icon=folium.Icon(color="blue", icon="plus-sign")
            ).add_to(m)

        st_folium(m, width=700, height=400)

        # Doctor cards
        st.markdown(f"### 👨‍⚕️ {district} এর বিশেষজ্ঞ ডাক্তার")
        cols = st.columns(2)
        for i, doc in enumerate(doctors):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="doctor-card">
                    <h4 style="color:#63b3ed; margin:0">{doc['নাম']}</h4>
                    <p style="color:#a0aec0; margin:4px 0">🏥 {doc['hospital']}</p>
                    <p style="color:#a0aec0; margin:4px 0">📍 {doc['address']}</p>
                    <p style="color:#68d391; margin:4px 0; font-size:18px">📞 {doc['phone']}</p>
                </div>
                """, unsafe_allow_html=True)

# ── 6. CRISIS ─────────────────────────────────
elif page == "জরুরি সাহায্য":
    st.markdown('<div class="section-header">🆘 জরুরি সাহায্য</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="crisis-banner">
    <h3>⚠️ আপনি কি এখন বিপদে আছেন?</h3>
    <p>যদি আপনি নিজেকে বা অন্যকে কষ্ট দেওয়ার কথা ভাবছেন, এখনই সাহায্য নিন।</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    helplines = [
        ("🟢", "কান পেতে রই", "01779-554391", "২৪/৭ emotional support"),
        ("🔵", "NIMH হেল্পলাইন", "16789", "জাতীয় মানসিক স্বাস্থ্য"),
        ("🟡", "জাতীয় হেল্পলাইন", "999", "জরুরি সেবা"),
        ("🔴", "Kaan Pete Roi", "01779-554391", "বাংলাদেশ সুইসাইড প্রিভেনশন"),
    ]

    cols = st.columns(2)
    for i, (color, name, number, desc) in enumerate(helplines):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <div style="font-size:40px">{color}</div>
                <h3 style="color:#e2e8f0">{name}</h3>
                <h2 style="color:#63b3ed">{number}</h2>
                <p style="color:#718096">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💙 মনে রাখুন:")
    reminders = [
        "আপনি একা নন — সাহায্য চাওয়া সাহসের কাজ",
        "এই কষ্ট সাময়িক — ভালো সময় আসবে",
        "আপনার জীবন অমূল্য — আপনাকে ভালোবাসার মানুষ আছে",
        "পেশাদার সাহায্য নেওয়া দুর্বলতা নয়, বুদ্ধিমানের কাজ",
    ]
    for r in reminders:
        st.markdown(f"✨ {r}")
