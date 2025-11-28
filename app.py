# Updated SafeURL Predictor Streamlit App (Calls Space URL /predict)

import streamlit as st
import re
import pandas as pd
from datetime import date
import time 
import warnings
import requests
from urllib.parse import urlparse

warnings.filterwarnings("ignore")

# -------------------------------------------------------------
#            CONFIG: SPACE URL
# -------------------------------------------------------------
SPACE_API_URL = "https://nayds004-url-predictor-space.hf.space/predict"  # replace with actual Space URL

# -------------------------------------------------------------
#            URL VALIDATION
# -------------------------------------------------------------
def is_valid_url(url):
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https:// or ftp://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ipv4
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_regex, url) is not None

# -------------------------------------------------------------
#            STREAMLIT PAGE CONFIG
# -------------------------------------------------------------
def set_page_config():
    st.set_page_config(
        page_title="SafeURL Predictor",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# -------------------------------------------------------------
#            INFO PAGE
# -------------------------------------------------------------
def info_page():
    st.title("🛡️ SafeURL Predictor: Project Overview")
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1e90ff;">
        <h2 style="color: #1e90ff;">Project Mission</h2>
        <p>
        This application is designed to analyze and classify URLs in real-time to determine if they are safe or malicious.
        It uses a machine learning model hosted on HuggingFace Spaces.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎓 Student Information")
    st.info("**Name:** Chinedu Egbuna")
    st.info("**Course:** Data Science Project")
    st.info(f"**Date:** {date.today().strftime('%B %d, %Y')}")

# -------------------------------------------------------------
#            PREDICTION PAGE
# -------------------------------------------------------------
def prediction_page():
    st.title("🔗 URL Safety Checker")
    st.subheader("Enter a URL to check if it’s safe.")

    st.markdown("---")

    url_input = st.text_input(
        "URL to Analyze",
        value="https://www.google.com/search?q=safeurl",
        help="Paste a full URL"
    )

    if st.button("Analyze URL", type="primary"):

        # if not is_valid_url(url_input):
        #     st.error("❌ Invalid URL format. Please enter a complete URL starting with http:// or https://.")
        #     pass
        #     return

        with st.spinner("Sending URL to Space API for prediction..."):
            time.sleep(1)

            try:
                response = requests.post(SPACE_API_URL, json={"url": url_input})
                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get("prediction", None)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    return
            except Exception as e:
                st.error(f"Request failed: {str(e)}")
                return

        st.toast("Analysis complete!")
        st.markdown("### Result")

        if prediction == 1:
            st.error("🚨 **MALICIOUS URL**")
        elif prediction == 0:
            st.success("✅ **BENIGN URL**")
        else:
            st.warning("⚠️ Prediction unavailable.")

        st.markdown("### Submitted URL")
        st.json({"url": url_input})

# -------------------------------------------------------------
#            MAIN APP
# -------------------------------------------------------------
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Project Info"

    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to:", ("Project Info", "URL Prediction"))
        st.session_state.page = page
        st.markdown("---")
        st.caption(f"App Version 1.0 | {date.today().year}")

    if st.session_state.page == "Project Info":
        info_page()
    else:
        prediction_page()

# -------------------------------------------------------------
#            RUN APP
# -------------------------------------------------------------
if __name__ == "__main__":
    set_page_config()
    main()
