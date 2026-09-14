import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

print(f"✅ API Key found: {api_key[:5]}...{api_key[-4:]}")
print("Listing available models that support generateContent:")

try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f" - {m.name}")
            
    target_model = "models/gemini-1.5-flash"
    if target_model in available_models:
        print(f"\n✅ Target model '{target_model}' is AVAILABLE.")
    else:
        print(f"\n⚠️ Target model '{target_model}' NOT found in list. Check region or API key type.")

except Exception as e:
    print(f"❌ API Error: {e}")
