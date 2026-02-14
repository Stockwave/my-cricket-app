import streamlit as st
import requests
from datetime import datetime, date

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Cricket Hub", page_icon="🏏", layout="centered")

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

# --- API SETUP ---
try:
    API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    API_KEY = "PASTE_YOUR_KEY_HERE" 

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

ENDPOINTS = {
    "Live": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live",
    "Recent": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent",
    "Upcoming": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
}

def fetch_matches_from_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        data = response.json()
        
        parsed_matches = []
        if 'typeMatches' in data:
            for match_type in data['typeMatches']: 
                if 'seriesMatches' in match_type:
                    for series in match_type['seriesMatches']:
                        source = series.get('seriesAdWrapper', {}).get('matches', series.get('matches', []))
                        for match in source:
                            parsed_matches.append(match)
        return parsed_matches
    except:
        return []

def get_data(category):
    if category == "All":
        all_data = []
        for key, link in ENDPOINTS.items():
            all_data.extend(fetch_matches_from_url(link))
        return all_data
    else:
        return fetch_matches_from_url(ENDPOINTS[category])

# --- DATE HELPER FUNCTION ---
def get_match_date_str(timestamp):
    """Converts API timestamp to readable date header"""
    try:
        match_date = datetime.fromtimestamp(int(timestamp) / 1000).date()
        today = date.today()
        
        if match_date == today:
            return "Today"
        elif (match_date - today).days == 1:
            return "Tomorrow"
        elif (today - match_date).days == 1:
            return "Yesterday"
        else:
            return match_date.strftime("%d %b %Y") 
    except:
        return "Date Unknown"

# --- UI HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏏 Cricket Hub")
with col2:
    if st.button("🔄"):
        st.rerun()

# --- FILTER 1: STATUS ---
status_filter = st.selectbox("Show Matches:", ["Live", "Recent", "Upcoming", "All"])

# --- FETCH DATA ---
if status_filter == "All":
    st.toast("Fetching data...")

matches = get_data(status_filter)

if not matches:
    st.info(f"No {status_filter} matches found.")
    st.stop()

# --- LOGIC FIX: REMOVE FINISHED MATCHES FROM LIVE VIEW ---
if status_filter == "Live":
    matches = [
        m for m in matches 
        if "Won" not in m['matchInfo']['status'] 
        and "Complete" not in m['matchInfo']['state']
    ]

# --- FILTER 2: SERIES ---
all_series = list(set([m['matchInfo']['seriesName'] for m in matches if 'matchInfo' in m]))
if len(all_series) > 1:
    selected_series = st.selectbox("Filter Series:", ["All"] + all_series)
    if selected_series != "All":
        matches = [m for m in matches if m['matchInfo']['seriesName'] == selected_series]

# --- GROUP BY DATE LOGIC ---
matches_by_date = {}
for m in matches:
    ts = m['matchInfo'].get('startDate', 0)
    date_header = get_match_date_str(ts)
    
    if date_header not in matches_by_date:
        matches_by_date[date_header] = []
    matches_by_date[date_header].append(m)

# --- DISPLAY MATCH CARDS ---
for date_group, match_list in matches_by_date.items():
    
    if status_filter != "Live":
        st.subheader(f"📅 {date_group}")

    for m in match_list:
        info = m['matchInfo']
        score = m.get('matchScore', {})
        mini = m.get('miniscore', {})

        with st.container():
            st.divider()
            
            status_text = info['status']
            if "Won" in status_text: icon = "🏆"
            elif "Starts" in status_text: icon = "⏰"
            else: icon = "🔴"
                
            st.caption(f"{info['seriesName']} • {info['matchFormat']}")

            t1 = info['team1']['teamName']
            t2 = info['team2']['teamName']
            
            def get_score_str(team_key):
                s = score.get(team_key, {}).get('inngs1', {})
                if s.get('runs'):
                    return f"{s.get('runs')}/{s.get('wickets', '0')} ({s.get('overs')} ov)"
                return "-" 

            c1, c2 = st.columns([2, 2])
            c1.write(f"**{t1}**")
            c2.write(f"**{get_score_str('team1Score')}**")
            
            c1, c2 = st.columns([2, 2])
            c1.write(f"**{t2}**")
            c2.write(f"**{get_score_str('team2Score')}**")

            st.info(f"{icon} {status_text}")

            if mini:
                st.markdown("---") 
                r1c1, r1c2 = st.columns(2)
                with r1c1:
                    st.caption("Striker")
                    name = mini.get('batsmanStriker', {}).get('batName', '-')
                    runs = mini.get('batsmanStriker', {}).get('batRuns', '-')
                    balls = mini.get('batsmanStriker', {}).get('batBalls', '-')
                    st.write(f"**{name}** {runs}({balls})")
                
                with r1c2:
                    st.caption("Non-Striker")
                    name = mini.get('batsmanNonStriker', {}).get('batName', '-')
                    runs = mini.get('batsmanNonStriker', {}).get('batRuns', '-')
                    balls = mini.get('batsmanNonStriker', {}).get('batBalls', '-')
                    st.write(f"**{name}** {runs}({balls})")
                
                st.write("") 
                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    st.caption("Bowler")
                    name = mini.get('bowlerStriker', {}).get('bowlName', '-')
                    figs = mini.get('bowlerStriker', {}).get('bowlWkts', '-')
                    runs = mini.get('bowlerStriker', {}).get('bowlRuns', '-')
                    st.write(f"**{name}** {figs}/{runs}")

                with r2c2:
                    st.caption("Rates")
                    crr = mini.get('crr', '-')
                    st.write(f"CRR: {crr}")

st.caption(f"Updated: {datetime.now().strftime('%H:%M')}")
