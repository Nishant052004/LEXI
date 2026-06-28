import streamlit as st
import os
import tempfile
import json
from sqlalchemy import desc

# DB Models and Core Modules
from models.db_models import User, Conversation, Entity, ChatLog, CustomEntityMapping
from coordinator import decide_agent
from memory import add_memory
from database.connection import SessionLocal
from memory.memory_manager import memory_manager
from ner.ner_module import ner_extractor

# Page configurations
st.set_page_config(
    page_title="MJ",
    page_icon="🤖",
    layout="wide"  # Wide layout for dual-panel interface
)

# Core Minimal Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Restore Streamlit's built-in icon font */
    [data-testid="stIcon"],
    [class*="material-symbols"],
    [class*="material-icons"],
    .material-icons,
    i {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1117 0%, #07090e 100%);
        color: #c9d1d9;
    }
    
    /* Elegant Title Card */
    .welcome-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.6) 0%, rgba(13, 17, 23, 0.8) 100%);
        border: 1px solid rgba(56, 139, 253, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        text-align: left;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    .welcome-title {
        background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 8px 0;
    }
    
    .welcome-subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Custom chat container */
    .chat-bubble {
        padding: 14px 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        max-width: 85%;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    .chat-user {
        background: linear-gradient(135deg, #1f6feb 0%, #094cb5 100%);
        color: #ffffff;
        margin-left: auto;
        border-bottom-right-radius: 2px;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.15);
    }
    .chat-assistant {
        background: rgba(22, 27, 34, 0.8);
        color: #c9d1d9;
        margin-right: auto;
        border-bottom-left-radius: 2px;
        border: 1px solid rgba(56, 139, 253, 0.1);
    }

    /* Card Panels */
    .intel-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .intel-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #58a6ff;
        margin-top: 0;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(240, 246, 252, 0.08);
        padding-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Entity Tag Styling */
    .entity-tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .tag-person { background-color: rgba(56, 139, 253, 0.15); color: #58a6ff; border-color: rgba(56, 139, 253, 0.3); }
    .tag-organization { background-color: rgba(46, 160, 67, 0.15); color: #3fb950; border-color: rgba(46, 160, 67, 0.3); }
    .tag-location { background-color: rgba(240, 136, 62, 0.15); color: #ff9d5c; border-color: rgba(240, 136, 62, 0.3); }
    .tag-date { background-color: rgba(210, 153, 34, 0.15); color: #d29922; border-color: rgba(210, 153, 34, 0.3); }
    .tag-email { background-color: rgba(219, 97, 162, 0.15); color: #db61a2; border-color: rgba(219, 97, 162, 0.3); }
    .tag-phone_number { background-color: rgba(57, 199, 185, 0.15); color: #39c7b9; border-color: rgba(57, 199, 185, 0.3); }
    .tag-custom { background-color: rgba(188, 140, 255, 0.15); color: #bc8cff; border-color: rgba(188, 140, 255, 0.3); }

    /* Indicator Badge */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 12px;
        text-align: center;
    }
    .badge-success {
        background-color: rgba(46, 160, 67, 0.2);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
    }
    .badge-primary {
        background-color: rgba(56, 139, 253, 0.2);
        color: #58a6ff;
        border: 1px solid rgba(56, 139, 253, 0.4);
    }

    /* Pulsing Green Dot */
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #3fb950;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7);
        animation: pulse 1.6s infinite;
        vertical-align: middle;
        margin-right: 6px;
    }
    @keyframes pulse {
        0 {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 6px rgba(46, 160, 67, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(46, 160, 67, 0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "Nishant"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = "admin"
if "preferences" not in st.session_state:
    st.session_state.preferences = {"theme": "dark", "temperature": 0.7}
if "active_convo_id" not in st.session_state:
    st.session_state.active_convo_id = None

# Open Database Session
db = SessionLocal()

# Load/Verify default user on page load
default_user = memory_manager.get_or_create_user(db, username="Nishant", role="admin")
st.session_state.user_id = default_user.id
st.session_state.username = default_user.username
st.session_state.role = default_user.role

# Load active conversation ID
if not st.session_state.active_convo_id:
    # Try fetching the latest conversation, or create one
    latest_convo = db.query(Conversation).filter(
        Conversation.user_id == default_user.id
    ).order_by(desc(Conversation.created_at)).first()
    
    if not latest_convo:
        latest_convo = memory_manager.get_or_create_conversation(db, user_id=default_user.id)
    st.session_state.active_convo_id = latest_convo.id
    # Pre-populate session message history if we just connected
    st.session_state.messages = memory_manager.get_conversation_history(db, latest_convo.id)

# Divide UI Layout into Chat panel and Live Intelligence Dashboard
col_chat, col_intel = st.columns([0.65, 0.35], gap="large")

# 1. CHAT PANEL (LEFT SIDE)
with col_chat:
    # Main Title Greeting Card
    st.markdown(f"""
    <div class="welcome-card">
        <h1 class="welcome-title">Hi {st.session_state.username} 👋, Welcome to LEXI </h1>
        <p class="welcome-subtitle"></p>
    </div>
    """, unsafe_allow_html=True)

    # Chat Room Container
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                st.markdown(f'<div class="chat-bubble chat-user">{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble chat-assistant">{content}</div>', unsafe_allow_html=True)

    # Input Prompt Box
    prompt = st.chat_input("Ask something to the LEXI...")

    if prompt:
        # Update session chat history with the user's message
        add_memory(st.session_state.messages, "user", prompt)

        # Run master coordinator once for the submitted prompt
        with st.spinner("Processing request..."):
            response = decide_agent(st.session_state.messages, prompt)

        # Append response to memory and rerun to update the UI
        add_memory(st.session_state.messages, "assistant", response)
        st.rerun()

# 2. INTELLIGENCE DASHBOARD (RIGHT SIDE)
with col_intel:
    # Session Details card
    st.markdown(f"""
    <div class="intel-card">
        <div class="intel-header">
            👤 Session & Profile
        </div>
        <p style="margin-bottom:8px;"><strong>User Profile:</strong> {st.session_state.username}</p>
        <p style="margin-bottom:8px;"><strong>Permission Role:</strong> <span class="badge badge-primary">{st.session_state.role.upper()}</span></p>
        <p style="margin-bottom:0px;"><strong>Status:</strong> <span class="pulse-dot"></span><span style="color:#3fb950; font-weight:600;">Secure Connected Session</span></p>
    </div>
    """, unsafe_allow_html=True)

    # New Chat Actions
    if st.button("🔄 Clear History & Start New Chat", use_container_width=True):
        st.session_state.messages = []
        new_convo = memory_manager.get_or_create_conversation(db, user_id=st.session_state.user_id)
        st.session_state.active_convo_id = new_convo.id
        st.success("New conversation initialized.")
        st.rerun()

    # Dynamic Custom Entity Mapper
    st.markdown("""
    <div class="intel-card">
        <div class="intel-header">
            🏷️ Dynamic Custom Entity Mapper
        </div>
        <p style="font-size:0.85rem; color:#8b949e; margin-bottom:15px;">
            Define custom literal patterns (e.g. "Antigravity" ➔ "PROJECT") dynamically at runtime.
            The NER extractor will immediately tag these patterns in conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display success toast/message if pending
    if "mapping_success" in st.session_state:
        st.success(st.session_state.mapping_success)
        del st.session_state.mapping_success

    # Form to add custom mappings
    with st.expander(" New Entity Mapping",
                      expanded=False):
        with st.form("add_mapping_form", 
                     clear_on_submit=True):
            map_text = st.text_input("Literal Text (e.g. Antigravity)", placeholder="Text to map")
            map_label = st.text_input("Label Category (e.g. PROJECT)", placeholder="Label category")
            submitted = st.form_submit_button("Register Custom Mapping", use_container_width=True)
            
            if submitted:
                if map_text.strip() and map_label.strip():
                    lbl_clean = map_label.strip().upper()
                    txt_clean = map_text.strip()
                    ner_extractor.add_custom_entity_label(lbl_clean, txt_clean)
                    st.session_state.mapping_success = f"Registered: '{txt_clean}' ➔ '{lbl_clean}'"
                    st.rerun()
                else:
                    st.error("Please fill in both fields.")

    # List current custom mappings
    with st.expander("📋Current Mapped Custom Entities", expanded=True):
        mappings = []
        if isinstance(ner_extractor.custom_literal_patterns, list):
            for item in ner_extractor.custom_literal_patterns:
                if not isinstance(item, dict):
                    continue
                pattern = item.get("pattern") or item.get("literal_text")
                label = item.get("label")
                if isinstance(pattern, (list, tuple)):
                    pattern = ", ".join(str(v) for v in pattern if v is not None)
                if not isinstance(pattern, str) or not isinstance(label, str):
                    continue
                pattern = pattern.strip()
                label = label.strip().upper()
                if not pattern or not label or label == "EMAIL":
                    continue
                mappings.append({"pattern": pattern, "label": label})

        if mappings:
            # Header
            col_h1, col_h2, col_h3 = st.columns([0.45, 0.35, 0.2])
            col_h1.markdown("**Pattern**")
            col_h2.markdown("**Label**")
            col_h3.markdown("**Action**")
            st.markdown('<hr style="margin: 4px 0 10px 0; border-color: rgba(240,246,252,0.1);"/>', unsafe_allow_html=True)
            
            for i, m in enumerate(mappings):
                pat = m["pattern"]
                lbl = m["label"]
                col_m1, col_m2, col_m3 = st.columns([0.45, 0.35, 0.2])
                col_m1.markdown(f"`{pat}`")
                col_m2.markdown(f"<span class='badge badge-primary'>{lbl}</span>", unsafe_allow_html=True)
                if col_m3.button("🗑️", key=f"del_{i}", help="Delete mapping"):
                    ner_extractor.remove_custom_entity_label(pat)
                    st.toast(f"Deleted mapping for '{pat}'")
                    st.rerun()
        else:
            st.info("No custom entity mappings registered yet.")

    # Live Named Entity Extraction visualizer
    st.markdown("""
    <div class="intel-card">
        <div class="intel-header">
            🔍 Live Session Named Entities (NER)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch extracted entities from the DB
    extracted_entities = db.query(Entity).filter(
        Entity.conversation_id == st.session_state.active_convo_id
    ).order_by(desc(Entity.extracted_at)).all()

    # Unique-ify extracted entities
    seen_entities = set()
    unique_entities = []
    for ent in extracted_entities:
        key = (ent.entity_value.lower(), ent.entity_type.upper())
        if key not in seen_entities:
            seen_entities.add(key)
            unique_entities.append(ent)

    if unique_entities:
        entity_html = '<div style="margin-bottom: 20px;">'
        for ent in unique_entities:
            lbl = ent.entity_type.lower()
            if lbl == "gpe" or lbl == "location":
                cls = "tag-location"
                display_lbl = "LOCATION"
            elif lbl == "org" or lbl == "organization":
                cls = "tag-organization"
                display_lbl = "ORGANIZATION"
            elif lbl == "person":
                cls = "tag-person"
                display_lbl = "PERSON"
            elif lbl == "date":
                cls = "tag-date"
                display_lbl = "DATE"
            elif lbl == "email":
                cls = "tag-email"
                display_lbl = "EMAIL"
            elif lbl == "phone_number":
                cls = "tag-phone_number"
                display_lbl = "PHONE"
            else:
                cls = "tag-custom"
                display_lbl = ent.entity_type.upper()
                
            entity_html += f'<span class="entity-tag {cls}">{ent.entity_value} &middot; {display_lbl}</span>'
        entity_html += '</div>'
        st.markdown(entity_html, unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:0.9rem; color:#8b949e;'>No entities extracted in this conversation yet.</p>", unsafe_allow_html=True)

    # Intent and Sentiment visualizer
    st.markdown("""
    <div class="intel-card">
        <div class="intel-header">
            🧠 Sentiment & Intent Metrics
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch the last conversation chat log
    last_log = db.query(ChatLog).filter(
        ChatLog.conversation_id == st.session_state.active_convo_id
    ).order_by(desc(ChatLog.logged_at)).first()

    if last_log:
        intent_map = {
            "coding": ("💻 Coding / Programming", "rgba(56, 139, 253, 0.2)", "#58a6ff"),
            "research": ("🔍 Web Research", "rgba(188, 140, 255, 0.2)", "#bc8cff"),
            "memory": ("🧠 System Memory", "rgba(57, 199, 185, 0.2)", "#39c7b9"),
            "general": ("💬 General Chat", "rgba(110, 118, 129, 0.2)", "#8b949e")
        }
        
        sentiment_map = {
            "positive": "😊 Positive Sentiment",
            "neutral": "😐 Neutral Sentiment",
            "negative": "😠 Negative Sentiment"
        }

        # Intent
        intent_resolved = last_log.intent.lower() if last_log.intent else "general"
        intent_text, intent_bg, intent_fg = intent_map.get(intent_resolved, (f"💬 {last_log.intent.upper()}", "rgba(110, 118, 129, 0.2)", "#8b949e"))
        
        # Sentiment
        sentiment_resolved = last_log.sentiment.lower() if last_log.sentiment else "neutral"
        sentiment_text = sentiment_map.get(sentiment_resolved, f"😐 {last_log.sentiment}")

        st.markdown(f"""
        <div style="font-size:0.9rem; line-height:1.6;">
            <p style="margin-bottom:8px;"><strong>Classified Intent:</strong> 
                <span class="badge" style="background-color: {intent_bg}; color: {intent_fg}; border: 1px solid {intent_fg}44;">{intent_text}</span>
            </p>
            <p style="margin-bottom:8px;"><strong>Sentiment Tone:</strong> 
                <span class="badge" style="background-color: rgba(240, 246, 252, 0.05); color: #c9d1d9; border: 1px solid rgba(240,246,252,0.15);">{sentiment_text}</span>
            </p>
            <p style="margin-bottom:8px;"><strong>Specialist Executed:</strong> <code style="color:#ff7b72;">{last_log.agent_name}</code></p>
            <p style="margin-bottom:0px;"><strong>Response Time:</strong> <span style="color:#58a6ff; font-weight:600;">{last_log.execution_time_s:.2f}s</span></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:0.9rem; color:#8b949e;'>Metrics will populate after the first query response.</p>", unsafe_allow_html=True)

# Close DB Connection
db.close()