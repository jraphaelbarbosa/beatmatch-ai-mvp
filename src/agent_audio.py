import json
import os
import time

import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load env vars
load_dotenv()

# Valid Categories (Single Source of Truth)
VALID_STYLES = [
    "TRAP", "DRILL", "BOOMBAP", "AFROBEATS", "RNB", 
    "HIPHOP_INTL", "POP", "DANCEHALL", "LOFI"
]

VALID_VIBES = [
    "DARK", "CHILL", "VIBEY", "HYPE", "ENERGETIC", "SAD", "LYRICAL", "MELODIC"
]

def clean_json_string(json_str):
    """
    Cleans markdown code blocks from the string to ensure valid JSON parsing.
    """
    cleaned = json_str.strip()
    # Remove markdown code blocks if present
    cleaned = cleaned.removeprefix("```json")
    cleaned = cleaned.removeprefix("```")
    cleaned = cleaned.removesuffix("```")
    return cleaned.strip()

def analyze_audio_with_langchain(file_path, mock_mode=False):
    """
    Analyzes audio using LangChain + Google GenAI (Gemini 1.5 Flash).
    
    Args:
        file_path (str): Path to the audio file.
        mock_mode (bool): If True, returns a dummy response.
        
    Returns:
        dict: JSON object with master_style, vibe, bpm, and description.
    """
    
    # --- MOCK MODE ---
    if mock_mode:
        print(f"[MOCK MODE] Simulating analysis for: {file_path}")
        time.sleep(1.5)
        return {
            "master_style": "TRAP",
            "vibe": "DARK",
            "bpm": 140,
            "description": "A dark, heavy trap beat with 808 glides (Mock Analysis).",
            "confidence": "High (Mock)"
        }

    # --- PROD MODE ---
    api_key = os.getenv("AUDIO_AGENT_API_KEY")
    if not api_key:
        return {"error": "AUDIO_AGENT_API_KEY not found in .env"}

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    print(f"Uploading file to Gemini: {file_path}...")
    
    try:
        # Note: We still use the genai SDK for file upload as LangChain 
        # doesn't handle the media upload to Gemini directly in the same way yet for multimodal
        # or we can pass the file uri if we had it. 
        # Standard pattern: upload via SDK, pass file object to prompt or reference.
        
        # Configure genai just for the upload part if needed or rely on the agent key if same.
        # Ideally we should use the same key.
        genai.configure(api_key=api_key)
        
        audio_file = genai.upload_file(file_path)
        
        # Wait for processing
        while audio_file.state.name == "PROCESSING":
            print("Processing file remotely...")
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)
            
        if audio_file.state.name == "FAILED":
            return {"error": "Audio file processing failed on Gemini side."}

        print("File uploaded. Initializing LangChain Agent...")

        # Initialize LangChain Model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0
        )

        prompt_text = f"""
        You are a music producer expert. Listen to this audio.
        Classify it strictly into ONE Style from: {json.dumps(VALID_STYLES)}
        And ONE Vibe from: {json.dumps(VALID_VIBES)}.
        Also estimate the BPM.
        
        Return ONLY a valid JSON object: {{ 'master_style': '...', 'vibe': '...', 'bpm': 123, 'description': '...' }}
        """

        # For multimodal in LangChain with Gemini, we can pass the message content as a list
        # containing text and the media reference.
        # However, ChatGoogleGenerativeAI supports passing media if we format the message correctly.
        # Alternatively, since we have the file URI from `audio_file.uri`, prompt handling might vary.
        # simpler approach: The standard `genai` method is reliable for file injection. 
        # But we are asked to use LangChain. 
        # LangChain's HumanMessage can take content list.
        
        from langchain_core.messages import HumanMessage
        
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt_text
                },
                {
                    "type": "media",
                    "mime_type": audio_file.mime_type,
                    "file_uri": audio_file.uri
                }
            ]
        )
        
        response = llm.invoke([message])
        content = response.content
        
        # Clean and Parse
        cleaned_content = clean_json_string(content)
        result = json.loads(cleaned_content)
        
        # Normalize keys
        result["master_style"] = result.get("master_style", "UNKNOWN").upper()
        result["vibe"] = result.get("vibe", "UNKNOWN").upper()
        
        return result

    except Exception as e:
        print(f"Agent Error: {e}")
        return {"error": str(e)}
