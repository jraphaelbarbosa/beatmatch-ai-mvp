# Spotify Artist ➡️ Instagram Extractor 📸

> **Turn a list of Spotify Artists into a list of official Instagram contacts.**

[Ler em Português](README.pt-br.md)

## 🎯 What this tool does
If you have a list of musicians on Spotify, you often need to contact them. This tool automates the process of finding their **official Instagram profile** linked in their Spotify bio.

It does **not** guess usernames. It extracts the exact link the artist pinned on their profile.

## ⚙️ How it works (The "Magic")
Traditional scrapers fail on Spotify because of "Lazy Loading" (buttons don't exist until you click them).
**This tool uses Network Interception.** It listens to the hidden JSON traffic between the Spotify Web Player and their API. When you visit an artist page, the tool "steals" the social links from the data stream before the page even loads.

**Input:** A CSV with Spotify Artist IDs.
**Output:** A CSV with verified Instagram URLs.

## 🚀 Key Features
* **100% Verified Links:** Only gets links provided by the artist themselves.
* **Network Interception:** Bypasses UI bugs and layout changes.
* **Batch Processing:** Handles 50k+ artists with session persistence.

## 📦 Installation & Usage
1. `pip install -r requirements.txt`
2. `playwright install chromium`
3. `python src/setup_auth.py` (Login once manually)
4. `python src/extract_instagrams.py` (Run the extractor)

## ⚠️ Disclaimer
For educational and portfolio purposes (BeatMachAI Project).