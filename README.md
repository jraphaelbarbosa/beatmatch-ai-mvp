# 🎧 BeatMatchAI (MVP)

> **[ 🇧🇷 Ler em Português ](README.pt-br.md)**

**Sonic Identity Matching System for Music Producers**

BeatMatchAI is an intelligent tool designed to streamline the music outreach process. It uses advanced AI Agents to listen to your beats, analyze their "Sonic DNA", and match them with the most suitable artists from your database.

Stop sending DMs in the dark. Let AI find the perfect match for your sound.

## 🚀 Key Features

* **Sonic DNA Analysis:**
    * Uses **Google Gemini 2.5 Flash** (via LangChain) to listen to audio files.
    * Extracts Style (Trap, Drill, Boombap, etc.), Vibe (Dark, Chill, Hype), and BPM.
    * Generates a rich musical description of the track.
* **Smart Artist Matching:**
    * Matches the analyzed "Sonic DNA" against your artist database/CRM.
    * (MVP) Filters artists based on Style and Vibe compatibility.
* **Outreach Helper:**
    * Automatically generates personalized pitch messages (Instagram DMs/Emails) based on the beat's characteristics.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **AI Engine:** LangChain + Google Gemini 2.5 Flash (`langchain-google-genai`)
* **Language:** Python 3.10+

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jraphaelbarbosa/beatmatch-ai-mvp.git
    cd beatmatch-ai-mvp
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root directory and add your Google AI Studio key:
    ```env
    AUDIO_AGENT_API_KEY=your_google_api_key_here
    ```

4.  **Run the App:**
    ```bash
    streamlit run src/app.py
    ```

## ⚠️ Important Note
This project uses the **Gemini 2.5 Flash** model. Ensure your API Key has access to the latest Google Generative AI models.
