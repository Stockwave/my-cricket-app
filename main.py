import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Cricket Live (RSS)", page_icon="🏏", layout="centered")

# --- CSS FOR MOBILE LOOK ---
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 1rem; padding-bottom: 2rem;}
    .stAlert {padding: 0.5rem;}
    h3 {font-size: 1rem !important; margin: 0 !important;}
    p {font-size: 0.9rem !important;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- RSS FEED URL (Google News Cricket) ---
RSS_URL = "https://news.google.com/rss/search?q=cricket+live+score&hl=en-IN&gl=IN&ceid=IN:en"

def get_cricket_feed():
    # Parse the feed
    feed = feedparser.parse(RSS_URL)
    return feed.entries

# --- HELPER TO EXTRACT INFO ---
def parse_title(title):
    # Google RSS titles usually look like: "India vs Australia Live Score: IND 120/2..."
    # We want to split this to make it look nice
    try:
        parts = title.split(":")
        if len(parts) > 1:
            teams = parts[0].strip()
            score = parts[1].strip()
            return teams, score
        else:
            return title, "Click for details"
    except:
        return title, ""

# --- UI HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏏 Google Scores")
with col2:
    if st.button("🔄"):
        st.rerun()

# --- FETCH & DISPLAY ---
try:
    entries = get_cricket_feed()
    
    if not entries:
        st.info("No live updates found on Google RSS right now.")
        st.stop()
        
    st.caption(f"Source: Google News • {len(entries)} updates found")

    for entry in entries:
        # Filter: Only show relevant match updates
        # We skip generic news articles to focus on scores
        if "Live" in entry.title or "Score" in entry.title or "vs" in entry.title:
            
            teams, score = parse_title(entry.title)
            
            with st.container():
                st.divider()
                
                # Header (Teams)
                st.markdown(f"### {teams}")
                
                # Score (Highlighted)
                if score and score != "Click for details":
                    st.info(f"📊 {score}")
                
                # Time (Published)
                published = entry.published_parsed
                if published:
                    dt = datetime(*published[:6]) + timedelta(hours=5, minutes=30)
                    time_str = dt.strftime("%I:%M %p")
                    st.caption(f"Updated: {time_str} • [View on Google]({entry.link})")
                else:
                    st.caption(f"[View on Google]({entry.link})")
                    
except Exception as e:
    st.error(f"Error fetching feed: {e}")

# Footer
now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
st.caption(f"Last Sync: {now_ist.strftime('%I:%M %p')} IST")
