# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

# Step1: Setup UI with streamlit (model provider, model, system prompt, web_search, query)
import streamlit as st

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")

# --- CUSTOM NEON THEME & ANIMATION CSS ---
st.markdown("""
<style>
    /* Main App Background Colour & Deep Cosmic Theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f1f5f9;
    }

    /* Input text areas ko smooth custom glass background aur borders dena */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    /* Input focus ya click hone par modern glow effect */
    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.3) !important;
    }

    /* Ask Agent Button ki flat look ko gradient neon styling dena */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        width: 100%;
    }

    /* Button par mouse laane se lift hone ka chota macro-animation */
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
    }
    
    div.stButton > button:first-child:active {
        transform: translateY(0);
    }

    /* Final Agent Response card ke liye glassmorphism style aur slide-up animation */
    .animated-response {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #818cf8;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Keyframes animation text ko fade-in aur neeche se upar chalane ke liye */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# --- END OF CUSTOM UI LAYOUT ---

st.title("🤖 AI Chatbot Agents")
st.write("Create and Interact with the AI Agents!")

# Input safe validation message handlers
system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here (e.g., Act as a python developer)...")

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider = st.radio("Select Provider:", ("Groq", "OpenAI"), horizontal=True)

if provider == "Groq":
    selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

allow_web_search = st.checkbox("🔍 Allow Web Search")

user_query = st.text_area("Enter your query: ", height=150, placeholder="Ask Anything!")

API_URL = "https://ai-agentic-chatbot-fastapi.vercel.app/chat"

if st.button("Ask Agent!"):
    if user_query.strip():
        # Step2: Connect with backend via URL
        import requests

        payload = {
            "model_name": selected_model,
            "model_provider": provider,
            "system_prompt": system_prompt.strip() if system_prompt.strip() else "You are a helpful assistant.",
            "messages": [user_query],
            "allow_search": allow_web_search
        }

        # Api response loading spinner layout trigger
        with st.spinner("🤖 Routing to backend workflow..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=45)
                if response.status_code == 200:
                    response_data = response.json()
                    if "error" in response_data:
                        st.error(response_data["error"])
                    else:
                        st.subheader("Agent Response")
                        
                        # Data dict ho ya clean string response, object parse karna
                        final_text = response_data.get("response", response_data) if isinstance(response_data, dict) else response_data
                        
                        # Output card wrapping layout with animation container injection
                        st.markdown(
                            f"""
                            <div class="animated-response">
                                <p style="color:#f8fafc; line-height:1.6; margin:0; font-size:1.05rem;">
                                    {final_text}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.error(f"❌ Server returned an error code: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Link Refused. Kindly ensure your backend.py script is active and running on port 9999.")