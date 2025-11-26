import pandas as pd
import time
import random
import os
from playwright.sync_api import sync_playwright

# Configuration
INPUT_FILES = ["artistas_parte1.csv", "artistas_parte2.csv"]
OUTPUT_FILE = "final_instagrams.csv"
AUTH_FILE = "spotify_auth.json"

def load_artists():
    dfs = []
    for f in INPUT_FILES:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                # Ensure columns exist, normalize if needed
                if 'id' in df.columns and 'name' in df.columns:
                    dfs.append(df[['id', 'name']])
                else:
                    print(f"Warning: File {f} missing 'id' or 'name' columns.")
            except Exception as e:
                print(f"Error reading {f}: {e}")
        else:
            print(f"Warning: File {f} not found.")
    
    if not dfs:
        return pd.DataFrame(columns=['id', 'name'])
    
    return pd.concat(dfs, ignore_index=True)

def get_processed_ids():
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            if 'id' in df.columns:
                return set(df['id'].astype(str).tolist())
        except:
            pass
    return set()

def save_result(data):
    df = pd.DataFrame([data])
    # Append to CSV, write header only if file doesn't exist
    header = not os.path.exists(OUTPUT_FILE)
    df.to_csv(OUTPUT_FILE, mode='a', header=header, index=False)

from datetime import datetime

def run():
    # 1. Load Data
    artists_df = load_artists()
    if artists_df.empty:
        print("No artists found to process. Please check input CSV files.")
        return

    processed_ids = get_processed_ids()
    print(f"Total artists: {len(artists_df)}")
    print(f"Already processed: {len(processed_ids)}")

    # Filter out processed
    artists_to_process = artists_df[~artists_df['id'].astype(str).isin(processed_ids)]
    total_to_process = len(artists_to_process)
    print(f"Remaining to process: {total_to_process}")

    if artists_to_process.empty:
        print("All artists processed!")
        return

    # 2. Initialize Playwright
    if not os.path.exists(AUTH_FILE):
        print(f"Error: {AUTH_FILE} not found. Please run setup_auth.py first.")
        return

    with sync_playwright() as p:
        # Headless=False to monitor execution
        browser = p.chromium.launch(headless=False)
        
        # Helper to create fresh context
        def create_context_page():
            ctx = browser.new_context(storage_state=AUTH_FILE)
            pg = ctx.new_page()
            return ctx, pg

        context, page = create_context_page()

        # Use enumerate to track progress count for memory management
        for i, (index, row) in enumerate(artists_to_process.iterrows()):
            # Memory Management: Recycle context every 100 items
            if i > 0 and i % 100 == 0:
                print(f"[{datetime.now()}] 🧹 Recycling browser context to free memory...")
                try:
                    context.close()
                except:
                    pass
                context, page = create_context_page()

            artist_id = str(row['id'])
            artist_name = row['name']
            url = f"https://open.spotify.com/artist/{artist_id}"
            
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] [Progresso {i+1}/{total_to_process}] Processando: {artist_name} ({artist_id})")

            instagram_url = None
            status = "Not Found"
            
            try:
                # Container for found links in this session
                found_links = []

                # Define response handler
                def handle_response(response):
                    try:
                        if "application/json" in response.headers.get("content-type", ""):
                            text = response.text()
                            if "instagram.com" in text:
                                import re
                                matches = re.findall(r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+', text)
                                for match in matches:
                                    if match not in found_links:
                                        found_links.append(match)
                    except Exception:
                        pass

                # Attach listener
                page.on("response", handle_response)

                try:
                    page.goto(url, timeout=30000) # Reduced timeout for faster failure in marathon
                    page.wait_for_load_state("networkidle", timeout=30000)
                    
                    page.mouse.wheel(0, 1000)
                    time.sleep(3) # Wait for responses

                    if found_links:
                        instagram_url = found_links[0]
                        status = "Found (Network)"
                        print(f"  -> Found Instagram: {instagram_url}")
                    else:
                        print("  -> No Instagram link found.")

                except Exception as nav_e:
                    # Navigation specific errors
                    print(f"  -> Navigation Error: {nav_e}")
                    status = "Nav Error"
                finally:
                    page.remove_listener("response", handle_response)

            except Exception as e:
                # Global error handler for the artist loop
                print(f"[{datetime.now()}] ⚠️ CRITICAL ERROR processing {artist_name}: {e}")
                status = "ERRO_MARATONA"
                time.sleep(10) # Wait before retrying next

            # Save result
            save_result({
                "id": artist_id,
                "name": artist_name,
                "instagram_url": instagram_url,
                "status": status,
                "spotify_url": url,
                "processed_at": datetime.now().isoformat()
            })

            # Anti-blocking sleep
            sleep_time = random.uniform(2, 4)
            time.sleep(sleep_time)

        browser.close()
        print("Extraction complete.")

if __name__ == "__main__":
    run()
