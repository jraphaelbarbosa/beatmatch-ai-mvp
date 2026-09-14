import json
import os
import sys
import time

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Valid Categories (Single Source of Truth)
VALID_STYLES = [
    "TRAP", "DRILL", "BOOMBAP", "AFROBEATS", "RNB", 
    "HIPHOP_INTL", "POP", "DANCEHALL", "LOFI"
]

VALID_VIBES = [
    "DARK", "CHILL", "VIBEY", "HYPE", "ENERGETIC", "SAD", "LYRICAL", "MELODIC"
]

def setup_gemini():
    """Configures the Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return None
    
    genai.configure(api_key=api_key)
    return True

def analyze_audio(file_path, mock_mode=False):
    """
    Analyzes an audio file to determine its Master Style and Vibe.
    
    Args:
        file_path (str): Path to the audio file.
        mock_mode (bool): If True, returns a dummy response.
        
    Returns:
        dict: JSON object with master_style, vibe, and description.
    """
    
    # --- MOCK MODE ---
    if mock_mode:
        print(f"[MOCK MODE] Simulating analysis for: {file_path}")
        time.sleep(1.5)
        return {
            "master_style": "TRAP",
            "vibe": "DARK",
            "description": "A dark, heavy trap beat with 808 glides (Mock Analysis).",
            "confidence": "High (Mock)"
        }
    
    # --- PROD MODE ---
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
        
    print(f"Uploading file to Gemini: {file_path}...")
    
    try:
        # 1. Upload File
        audio_file = genai.upload_file(file_path)
        
        # Wait for processing
        while audio_file.state.name == "PROCESSING":
            print("Processing file remotely...")
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)
            
        if audio_file.state.name == "FAILED":
            return {"error": "Audio file processing failed on Gemini side."}

        print("File uploaded. Generating analysis...")

        # 2. Configure Model
        # Use gemini-1.5-flash as requested for stability/quota
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert music producer. Listen to this audio track.
        Classify it strictly into ONE "master_style" and ONE "vibe" from the provided lists.
        
        ALLOWED STYLES: {json.dumps(VALID_STYLES)}
        ALLOWED VIBES: {json.dumps(VALID_VIBES)}
        
        Output must be valid JSON.
        Format:
        {{
            "master_style": "STYLE_FROM_LIST",
            "vibe": "VIBE_FROM_LIST",
            "description": "Short 1-sentence description of the sound."
        }}
        """

        # 3. Generate with JSON Strict Mode
        response = model.generate_content(
            [prompt, audio_file],
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        
        # 4. Parse Result
        result = json.loads(response.text)
        
        # Normalize keys just in case
        normalized_result = {
            "master_style": result.get("master_style", "UNKNOWN").upper(),
            "vibe": result.get("vibe", "UNKNOWN").upper(),
            "description": result.get("description", "No description.")
        }
        
        # Validate against lists (Optional fallback)
        if normalized_result["master_style"] not in VALID_STYLES:
            normalized_result["warning_style"] = f"Original: {normalized_result['master_style']}"
            # Keep it or set to closest? Let's keep it but warn.
            
        return normalized_result

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_beat.py <audio_file> [--mock]")
        return

    target_file = sys.argv[1]
    mock = "--mock" in sys.argv
    
    if setup_gemini():
        result = analyze_audio(target_file, mock_mode=mock)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
