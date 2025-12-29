import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import pandas as pd
import sys

# 1. Setup & Imports
# Add project root to Python path to resolve 'src' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables IMMEDIATELY (before any other logic)
load_dotenv()

# Explicitly retrieve API Key for validation
api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Page Config (Must be first Streamlit command)
st.set_page_config(
    page_title="BeatMatchAI",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import backend logic (AFTER loading env vars)
# Import backend logic (AFTER loading env vars)
# Changed: Using new LangChain agent
from src.agent_audio import analyze_audio_with_langchain as analyze_audio
from src.find_matches import ArtistMatcher

# Explicitly retrieve API Key for validation
# Changed: Check for AUDIO_AGENT_API_KEY
audio_api_key = os.getenv("AUDIO_AGENT_API_KEY")

def save_uploaded_file(uploaded_file):
    """Helper to save uploaded file to a temp path for processing."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def main():
    # 2. Visual Layout - Sidebar
    with st.sidebar:
        st.title("🎧 BeatMatchAI")
        st.caption("Sonic Identity Matching System")
        
        st.divider()
        
        # Debug Check for API Key
        if not audio_api_key:
            st.sidebar.error("⚠️ AUDIO_AGENT_API_KEY not found in environment!")

        # Mock Mode Toggle
        mock_mode = st.toggle("Mock Mode (No API Cost)", value=False)
        if mock_mode:
            st.info("⚠️ Mock Mode Active: Using dummy data.")
            
        st.divider()
        
        # Outreach Helper
        st.subheader("📢 Outreach Helper")
        default_pitch = """Hey i have a beat for you!!
This beat was sent to you via BeatMatchAI.
BeatMatchAI is an app that uses AI to find the perfect match between the beatmaker > a new beat > to the perfect artists for it.
Try this beat at... [LINK]
"""
        st.text_area("Pitch Template", value=default_pitch, height=200, help="Copy this to your clipboard.")
        st.caption("💡 Tip: Copy this to your clipboard when reaching out!")

    # 3. Main Area - Hero Section
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1>🎧 BeatMatchAI</h1>
        <p style='font-size: 1.2rem; color: #888;'>Sonic Identity Matching System</p>
    </div>
    """, unsafe_allow_html=True)

    # File Uploader
    uploaded_file = st.file_uploader("Upload your beat", type=['mp3', 'wav'])

    if uploaded_file is not None:
        # Display Audio Player
        st.audio(uploaded_file)
        
        # Center the Analyze button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_btn = st.button("Analyze Sonic DNA 🧬", use_container_width=True, type="primary")

        if analyze_btn:
            with st.spinner("Extracting Vibe & Style..."):
                # Save file efficiently
                temp_path = save_uploaded_file(uploaded_file)
                
                if temp_path:
                    # Call Backend: Analyze Audio
                    result = analyze_audio(temp_path, mock_mode=mock_mode)
                    
                    # Cleanup temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass # Best effort cleanup

                    # Handle Analysis Results
                    if "error" in result:
                        st.error(f"Analysis Failed: {result['error']}")
                    else:
                        master_style = result.get("master_style", "UNKNOWN")
                        vibe = result.get("vibe", "UNKNOWN")
                        description = result.get("description", "No description available.")

                        # Display Metrics
                        st.markdown("### 📊 Sonic Analysis")
                        m_col1, m_col2 = st.columns(2)
                        with m_col1:
                            st.metric(label="Master Style", value=master_style)
                        with m_col2:
                            st.metric(label="Vibe", value=vibe)
                        
                        st.info(f"📝 **AI Description:** {description}")

                        # Find Matches
                        st.divider()
                        st.markdown("### 🤝 Artist Matches")
                        
                        matcher = ArtistMatcher()
                        with st.spinner(f"Searching database for {master_style} / {vibe} artists..."):
                            matches = matcher.find_matches(master_style, vibe)
                        
                        if matches:
                            # 4. Results Table (The "Wow" Factor)
                            # Convert to clean format for display
                            display_data = []
                            for m in matches:
                                match_badge = "🔥 Perfect" if m['match_type'] == 'PERFECT' else "⚡ Related"
                                # Format genres: join list or take first few
                                genres_str = ", ".join(m['matched_genres'][:3]) 
                                if len(m['matched_genres']) > 3:
                                    genres_str += "..."
                                
                                handle = m.get('handle', 'N/A')
                                if handle and handle != 'N/A':
                                    # Create clickable link
                                    link = f"[{' @' + handle + ' ↗'}](https://instagram.com/{handle})"
                                else:
                                    link = "N/A"

                                display_data.append({
                                    "Artist": m['name'],
                                    "Match Badge": match_badge,
                                    "Why (Genres)": genres_str,
                                    "Instagram": link
                                })
                            
                            # Use st.dataframe with column config for links? 
                            # Or simpler: use markdown table construction or iteration for cards.
                            # User requested "Card-like rows or a clean DataFrame display"
                            # Let's try iteration for a more premium look, or a nice dataframe.
                            # Streamlit dataframe supports links in markdown!
                            
                            df = pd.DataFrame(display_data)
                            st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
                            
                            # Alternative: Use st.dataframe for interactivity if preferred, 
                            # but markdown table is often cleaner for simple "Link" display without column config complexity.
                            # Let's stick to markdown table or simple iteration if markdown table doesn't render links clickable in all versions.
                            # Better approach for "Wow": Custom Loop
                            
                            for _, row in df.iterrows():
                                with st.container():
                                    c1, c2, c3, c4 = st.columns([2, 1.5, 3, 1.5])
                                    c1.markdown(f"**{row['Artist']}**")
                                    c2.markdown(f"`{row['Match Badge']}`")
                                    c3.caption(f"{row['Why (Genres)']}")
                                    c4.markdown(row['Instagram'])
                                    st.divider()
                                    
                        else:
                            st.warning("No direct matches found. Try a different style or vibe manually!")
    
    else:
        # Empty State
        st.info("👋 Upload an audio file to get started!")

if __name__ == "__main__":
    main()
