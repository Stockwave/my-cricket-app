import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Debug Mode", layout="centered")
st.title("🛠️ Cricket Debugger")

# --- 1. SETUP ---
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = "PASTE_YOUR_KEY_HERE" 

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

URL = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

# --- 2. THE TEST ---
if st.button("🔴 Run Diagnostic Test", type="primary"):
    st.write("1. Attempting to connect...")
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        
        # SHOW THE STATUS CODE (200 is Good, 401/403 is Key Error, 429 is Limit Reached)
        st.write(f"**Status Code:** {response.status_code}")
        
        # SHOW THE RAW DATA
        data = response.json()
        st.write("**Raw API Response:**")
        st.json(data)
        
        # CHECK FOR SPECIFIC ERRORS
        if response.status_code == 401:
            st.error("❌ Error 401: Unauthorized. Your API Key is wrong or missing.")
        elif response.status_code == 429:
            st.error("❌ Error 429: Too Many Requests. You have used all your free credits for today.")
        elif "message" in data:
            st.warning(f"⚠️ API Message: {data['message']}")
            
    except Exception as e:
        st.error(f"❌ Connection Failed completely: {e}")

else:
    st.info("Click the button above to test your connection.")
