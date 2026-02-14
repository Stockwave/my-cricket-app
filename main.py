import streamlit as st
import requests
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Cricket Live", page_icon="🏏", layout="centered")

# --- HIDE STREAMLIT BRANDING ---
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 1rem; padding-bottom: 1rem;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- API KEY SETUP ---
# We use st.secrets for safety on the cloud
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    # If you run this on your laptop without secrets, paste key here:
    API_KEY = "PASTE_YOUR_KEY_HERE" 

URL = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

def get_live_data():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=5)
        data = response.json()
        matches_list = []
        if 'typeMatches' in data:
            for match_type in data['typeMatches']: 
                if 'seriesMatches' in match_type:
                    for series in match_type['seriesMatches']:
                        source = series.get('seriesAdWrapper', {}).get('matches', series.get('matches', []))
                        for match in source:
                            matches_list.append(match)
        return matches_list
    except:
        return []

# --- HEADER ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🏏 Live Scores")
with col2:
    if st.button("🔄"):
        st.rerun()

# --- MAIN APP ---
matches = get_live_data()

if not matches:
    st.info("No matches live right now.")
else:
    # Series Filter
    all_series = list(set([m['matchInfo']['seriesName'] for m in matches]))
    if len(all_series) > 1:
        selected_series = st.selectbox("Filter:", ["All"] + all_series)
        if selected_series != "All":
            matches = [m for m in matches if m['matchInfo']['seriesName'] == selected_series]

    # Match Cards
    for m in matches:
        info = m['matchInfo']
        score = m.get('matchScore', {})
        
        def get_score(team):
            s = score.get(team, {}).get('inngs1', {})
            return f"{s.get('runs')}/{s.get('wickets','0')}" if s.get('runs') else "Batting..."

        with st.container():
            st.divider()
            st.caption(f"{info['seriesName']}")
            
            c1, c2 = st.columns([3, 2])
            c1.write(f"**{info['team1']['teamName']}**")
            c2.write(f"**{get_score('team1Score')}**")
            
            c1, c2 = st.columns([3, 2])
            c1.write(f"**{info['team2']['teamName']}**")
            c2.write(f"**{get_score('team2Score')}**")
            
            st.info(info['status'])

st.caption(f"Updated: {datetime.now().strftime('%H:%M')}")