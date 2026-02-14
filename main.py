import streamlit as st
from pycricbuzz import Cricbuzz
from datetime import datetime

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Cricket Live (Free)", page_icon="🏏", layout="centered")

# --- CSS FOR MOBILE LOOK ---
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 1rem; padding-bottom: 2rem;}
    [data-testid="stMetricValue"] {font-size: 1.2rem !important;}
    h3 {font-size: 1.1rem !important; margin-top: 1rem !important; color: #444;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- INIT CRICBUZZ ---
c = Cricbuzz()

def get_matches(status_filter):
    matches = c.matches()
    filtered_data = []
    
    for match in matches:
        # The library returns a dictionary for each match
        # We filter based on the user's selection
        m_state = match.get('mchstate', '').lower()
        m_status = match.get('status', '').lower()
        
        if status_filter == "Live":
            if m_state == "inprogress" or m_state == "tea" or m_state == "lunch":
                filtered_data.append(match)
                
        elif status_filter == "Recent":
            if m_state == "mom" or m_state == "complete":
                filtered_data.append(match)
                
        elif status_filter == "Upcoming":
            if m_state == "preview" or m_state == "next":
                filtered_data.append(match)
                
        elif status_filter == "All":
            filtered_data.append(match)
            
    return filtered_data

def get_score_details(match_id):
    try:
        # Fetch detailed score for a specific match
        info = c.livescore(match_id)
        return info
    except:
        return {}

# --- UI HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏏 Cricket Hub")
with col2:
    if st.button("🔄"):
        st.rerun()

# --- FILTER ---
status_filter = st.selectbox("Show Matches:", ["Live", "Recent", "Upcoming", "All"])

# --- FETCH DATA ---
try:
    matches_list = get_matches(status_filter)
except Exception as e:
    st.error("⚠️ Cricbuzz is blocking the connection. Try again in 1 minute.")
    st.stop()

if not matches_list:
    st.info(f"No {status_filter} matches found.")
    st.stop()

# --- DISPLAY CARDS ---
for m in matches_list:
    match_id = m['id']
    series = m.get('srs', 'Unknown Series')
    t1 = m.get('team1', {}).get('name', '')
    t2 = m.get('team2', {}).get('name', '')
    status = m.get('status', '')
    state = m.get('mchstate', '')

    # Fetch live details ONLY if the match is Live
    score_data = {}
    if state == "inprogress":
        score_data = get_score_details(match_id)

    with st.container():
        st.divider()
        
        # Icon Logic
        if "won" in status.lower(): icon = "🏆"
        elif "starts" in status.lower(): icon = "⏰"
        else: icon = "🔴"

        st.caption(f"{series} • {m.get('type', '')}")

        # Teams & Scores
        # The library structure is slightly different for scores
        # We try to get it from the detailed 'score_data' if available
        
        t1_s = "-"
        t2_s = "-"
        
        if score_data:
            t1_s = score_data.get('batting', {}).get('score', [])
            if t1_s: t1_s = f"{t1_s[0].get('runs')}/{t1_s[0].get('wickets')} ({t1_s[0].get('overs')})"
            else: t1_s = "-"
            
            t2_s = score_data.get('bowling', {}).get('score', [])
            if t2_s: t2_s = f"{t2_s[0].get('runs')}/{t2_s[0].get('wickets')} ({t2_s[0].get('overs')})"
            else: t2_s = "-"

        # If not live, just show names
        c1, c2 = st.columns([2, 2])
        c1.write(f"**{t1}**")
        c1.write(f"**{t2}**")
        
        c2.write(f"**{t1_s}**")
        c2.write(f"**{t2_s}**")

        st.info(f"{icon} {status}")
        
        # Show Batman/Bowler only if available
        if score_data and 'batsman' in score_data:
            st.markdown("---")
            batsman = score_data.get('batsman', [])
            bowler = score_data.get('bowler', [])
            
            col_a, col_b = st.columns(2)
            if batsman:
                with col_a:
                    st.caption("Batting")
                    for b in batsman:
                        st.write(f"**{b['name']}**: {b['runs']}({b['balls']})")
            
            if bowler:
                with col_b:
                    st.caption("Bowling")
                    for b in bowler:
                        st.write(f"**{b['name']}**: {b['wickets']}/{b['runs']}")

st.caption(f"Updated: {datetime.now().strftime('%H:%M')}")
