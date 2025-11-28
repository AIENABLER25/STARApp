import streamlit as st
import pandas as pd
import time

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="StratAI: Executive GenAI Training", layout="wide")

# Mock CSS for a more professional, "Boardroom" aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #002b36;
        color: white;
    }
    h1 { color: #002b36; }
    h3 { color: #586e75; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENT DATABASE (MOCK) ---
# In a real app, this would be an SQL database or Vector DB
def get_industry_content(industry):
    data = {
        "Finance": {
            "risk": "Data Privacy & Regulatory Compliance (SEC/GDPR)",
            "opportunity": "Automated Fraud Detection & Personalized Wealth Management",
            "use_case": "JP Morgan's 'IndexGPT' for thematic investment analysis.",
            "scenario": "A junior trader wants to use ChatGPT to draft market reports using client data."
        },
        "Healthcare": {
            "risk": "HIPAA Compliance & Diagnostic Hallucinations",
            "opportunity": "Drug Discovery Acceleration & Patient Triage Bots",
            "use_case": "Mayo Clinic partnering with Google for Med-PaLM 2.",
            "scenario": "Your R&D head wants to feed patient genomic data into an open-source LLM."
        },
        "Retail": {
            "risk": "Brand Reputation & Biased Marketing Copy",
            "opportunity": "Hyper-personalized Marketing & Supply Chain Optimization",
            "use_case": "Carrefour using GenAI for shopping assistants.",
            "scenario": "Marketing wants to replace product photographers with Midjourney generated images."
        },
        "Manufacturing": {
            "risk": "IP Leakage of Schematics",
            "opportunity": "Predictive Maintenance & Generative Design",
            "use_case": "Siemens using GenAI for industrial automation code.",
            "scenario": "Engineers are pasting proprietary code into GitHub Copilot without an enterprise license."
        }
    }
    return data.get(industry, data["Finance"])

# --- SESSION STATE MANAGEMENT ---
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'progress' not in st.session_state:
    st.session_state.progress = 0

# --- APP MODULES ---

def sidebar_profile():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.header("Executive Profile")
        name = st.text_input("Name", "Alex Mercer")
        role = st.selectbox("Role", ["CEO", "CTO", "CFO", "CMO", "COO"])
        industry = st.selectbox("Industry Sector", ["Finance", "Healthcare", "Retail", "Manufacturing"])

        st.divider()
        st.metric("Strategy Score", f"{st.session_state.xp} pts")
        st.progress(st.session_state.progress / 100)
        return name, role, industry

def module_the_basics():
    st.subheader("Module 1: The 3-Minute GenAI Briefing")
    st.write("Target: Understand the capabilities without the jargon.")

    col1, col2 = st.columns(2)
    with col1:
        st.info("**Discriminative AI (Old)**")
        st.write("Classifies data. (e.g., 'Is this a cat?')")
        st.write("*Used for: Spam filters, Fraud detection.*")
    with col2:
        st.success("**Generative AI (New)**")
        st.write("Creates new data. (e.g., 'Draw a cat in the style of Van Gogh')")
        st.write("*Used for: Content creation, Coding, Synthesis.*")

    st.markdown("### Key Terminology for the Boardroom")
    terms = {
        "LLM (Large Language Model)": "The engine behind tools like ChatGPT. It predicts the next word based on massive training data.",
        "Hallucination": "When an AI confidently asserts a fact that is completely false.",
        "RAG (Retrieval-Augmented Generation)": "Connecting AI to your *private* company data so it doesn't make things up."
    }
    for term, definition in terms.items():
        with st.expander(term):
            st.write(definition)

    if st.button("Mark Module 1 Complete"):
        st.session_state.progress = 50
        st.balloons()

def module_industry_implications(industry):
    content = get_industry_content(industry)
    st.subheader(f"Module 2: Strategic Impact in {industry}")

    tab1, tab2, tab3 = st.tabs(["ROI Opportunities", "Critical Risks", "Real World Case"])

    with tab1:
        st.success(f"**Top Opportunity:** {content['opportunity']}")
        st.write("Executive Action: Mandate a task force to identify low-hanging fruit in this area within 30 days.")

    with tab2:
        st.error(f"**Primary Risk:** {content['risk']}")
        st.write("Executive Action: Review data governance policies before deploying any public-facing AI.")

    with tab3:
        st.info(f"**Case Study:** {content['use_case']}")

def module_simulation(industry):
    content = get_industry_content(industry)
    st.subheader("Module 3: The War Room (Simulation)")
    st.markdown("*> You are faced with a strategic decision. Choose wisely.*")

    st.warning(f"**Scenario:** {content['scenario']}")

    choice = st.radio("What is your directive?",
                      ["A. Block access immediately to all AI tools.",
                       "B. Deploy an Enterprise Sandbox environment and training.",
                       "C. Do nothing, let innovation happen naturally."])

    if st.button("Submit Decision"):
        if choice.startswith("B"):
            st.success("Correct Strategy. Blocking creates 'Shadow AI' (people using it secretly). Doing nothing risks IP leaks. A Sandbox balances innovation with security.")
            st.session_state.xp += 100
        elif choice.startswith("A"):
            st.error("Too Conservative. While safe, your competitors will outpace you. Employees will likely find workarounds using personal devices.")
        else:
            st.error("Dangerous. You have just exposed company secrets to the public domain.")

# --- MAIN APP LOGIC ---

def main():
    name, role, industry = sidebar_profile()

    st.title(f"Welcome, {name}")
    st.markdown(f"**{role} Track | {industry} Sector**")
    st.write("This platform is designed to move you from 'AI Awareness' to 'AI Governance' in under 15 minutes.")

    st.divider()

    # Navigation Tabs
    nav = st.radio("Select Training Module:", ["1. GenAI Fundamentals", "2. Industry Impact", "3. Strategic Simulator"], horizontal=True)

    st.divider()

    if "1." in nav:
        module_the_basics()
    elif "2." in nav:
        module_industry_implications(industry)
    elif "3." in nav:
        module_simulation(industry)

if __name__ == "__main__":
    main()
