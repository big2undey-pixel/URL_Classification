import streamlit as st
import requests
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import re
import math
from collections import Counter
from datetime import date

# -----------------------------
# Configuration
# -----------------------------
SPACE_API_URL = "https://big2undey-url_prediction.hf.space/predict"  # <- replace with your Space API endpoint

# -----------------------------
# Helper / Feature extraction
# -----------------------------
KEYWORDS = ["login", "secure", "account", "update", "bank", "verify", "confirm", "payment"]

def count_digits(url: str) -> int:
    return sum(c.isdigit() for c in url)

def count_special(url: str) -> int:
    # count non-alphanumeric characters
    return sum(1 for c in url if not c.isalnum())

def count_letters(url: str) -> int:
    return sum(c.isalpha() for c in url)

def has_https(url: str) -> int:
    return int(url.lower().startswith("https://"))

def num_subdomains(url: str) -> int:
    hostname = urlparse(url).hostname
    if hostname:
        parts = hostname.split('.')
        # subtract domain + tld (approximation)
        return max(0, len(parts) - 2)
    return 0

def path_depth(url: str) -> int:
    path = urlparse(url).path
    # count meaningful path separators
    if not path or path == '/':
        return 0
    return max(0, path.count('/'))

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    prob = [n_x / len(s) for _, n_x in Counter(s).items()]
    return -sum(p * math.log2(p) for p in prob)

def contains_ip(url: str) -> int:
    host = urlparse(url).netloc
    if host and re.search(r"^(\d{1,3}\.){3}\d{1,3}$", host):
        return 1
    # also search anywhere in URL
    return int(bool(re.search(r"(\d{1,3}\.){3}\d{1,3}", url)))

def rare_tld_flag(url: str) -> int:
    hostname = urlparse(url).hostname
    common = {"com","org","net","edu","gov","io","co"}
    if hostname and '.' in hostname:
        tld = hostname.split('.')[-1].lower()
        return int(tld not in common)
    return 1

def keyword_flags(url: str) -> dict:
    low = url.lower()
    return {f"has_{k}": int(k in low) for k in KEYWORDS}

def extract_features_single(url: str) -> dict:
    feats = {}
    feats["url_length"] = len(url)
    feats["num_digits"] = count_digits(url)
    feats["num_special"] = count_special(url)
    feats["num_letters"] = count_letters(url)
    feats["has_https"] = has_https(url)
    feats["num_subdomains"] = num_subdomains(url)
    feats["path_depth"] = path_depth(url)
    feats["entropy"] = shannon_entropy(url)
    feats["contains_ip"] = contains_ip(url)
    feats["rare_tld_flag"] = rare_tld_flag(url)
    feats.update(keyword_flags(url))
    return feats

# -----------------------------
# Streamlit UI
# -----------------------------

def set_page_config():
    st.set_page_config(page_title="SafeURL Predictor", page_icon="🛡️", layout="wide")

set_page_config()

if 'passport' not in st.session_state:
    st.session_state['passport'] = None

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ("Project Info", "URL Prediction"))
    st.markdown("---")
    st.caption(f"App Version 1.1 | {date.today().year}")

# -----------------------------
# Project Info Page
# -----------------------------
if page == "Project Info":
    st.title("🧾 Project Info")
    st.markdown("Upload student passport photo and fill project metadata.")

    col1, col2 = st.columns([1,2])
    with col1:
        uploaded = st.file_uploader("Upload Passport Photo (jpg, png)", type=["png","jpg","jpeg"]) 
        if uploaded:
            st.session_state['passport'] = uploaded
            st.image(uploaded, caption="Passport preview", use_column_width=True)
            st.success("Passport uploaded")
        elif st.session_state['passport']:
            st.image(st.session_state['passport'], caption="Passport (saved in session)", use_column_width=True)

    with col2:
        student_name = st.text_input("Student Name", value="Chinedu Egbuna")
        student_course = st.text_input("Course", value="Data Science Project")
        student_id = st.text_input("Student ID / Matric No.")
        supervisor = st.text_input("Supervisor / Lecturer")
        st.markdown("---")
        st.write("**Project description (short):**")
        proj_desc = st.text_area("", height=120)

    if st.button("Save Info"):
        st.success("Project info saved in session (temporary).")
        # optionally persist to a file or external storage here

# -----------------------------
# URL Prediction Page
# -----------------------------
else:
    st.title("🔗 URL Safety Checker")
    st.markdown("Enter a URL to check if it’s safe. After prediction, key KPIs and explanations will be shown.")

    url_input = st.text_input("URL to Analyze", value="https://www.google.com/search?q=safeurl")

    colA, colB = st.columns([3,1])
    with colA:
        analyze = st.button("Analyze URL")
    with colB:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.info("Model endpoint:")
        st.caption(SPACE_API_URL)

    if analyze:
        if not url_input.strip():
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Sending URL to Space API for prediction..."):
                try:
                    # call the space API
                    resp = requests.post(SPACE_API_URL, json={"url": url_input}, timeout=15)
                    resp.raise_for_status()
                    result = resp.json()
                    # Expecting {'prediction': 0} or similar
                    prediction_raw = result.get("prediction")
                except Exception as e:
                    st.error(f"API request failed: {e}")
                    prediction_raw = None

            # derive features on frontend for display
            feats = extract_features_single(url_input)

            # RESULT CARD
            st.markdown("---")
            col1, col2 = st.columns([2,3])
            with col1:
                st.subheader("Result")
                if prediction_raw is None:
                    st.warning("Prediction unavailable")
                elif int(prediction_raw) == 1:
                    st.error("🚨 MALICIOUS URL")
                else:
                    st.success("✅ BENIGN URL")

                st.markdown("**Submitted URL:**")
                st.write(url_input)

            # KPI CARDS - 5 cards
            with col2:
                k1, k2, k3, k4, k5 = st.columns(5)
                k1.metric("URL Length", feats['url_length'])
                k2.metric("Special Chars", feats['num_special'])
                k3.metric("Subdomains", feats['num_subdomains'])
                k4.metric("Contains IP", "Yes" if feats['contains_ip'] else "No")
                k5.metric("Entropy", f"{feats['entropy']:.2f}")

            # Explanations & feature list
            st.markdown("---")
            st.subheader("Why this result?")
            expl_col1, expl_col2 = st.columns(2)
            with expl_col1:
                st.write("**Keyword flags:**")
                for k in KEYWORDS:
                    st.write(f"{k}: {feats[f'has_{k}']}")

            with expl_col2:
                st.write("**Other features:**")
                other_df = pd.DataFrame({k: [v] for k, v in feats.items() if k not in [f'has_{x}' for x in KEYWORDS]})
                st.table(other_df.T.rename(columns={0:"value"}))

            # Raw API response
            st.markdown("---")
            st.subheader("Raw API Response")
            st.json(result)

            # footer guidance
            st.markdown("---")
            st.caption("Tip: High entropy, many special characters, presence of keywords like 'login' and use of IPs are common indicators of malicious URLs.")
