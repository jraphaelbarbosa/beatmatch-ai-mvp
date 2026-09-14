import os
from datetime import datetime

import pandas as pd
from db_manager import DatabaseManager

# --- Configuration ---
ARTISTS_CSV_1 = "artistas_parte1.csv"
ARTISTS_CSV_2 = "artistas_parte2.csv"
CONTACTS_CSV = "final_instagrams.csv"
SCHEMA_FILE = "create_tables.sql"

def clean_genres(genre_str):
    """Parses stringified list of genres into a Python list."""
    if pd.isna(genre_str) or genre_str == "":
        return []
    # If it's already a list (rare in CSV read), return it
    if isinstance(genre_str, list):
        return genre_str
    # If it looks like 'french r&b' (simple string), return as single item list
    # But usually in these CSVs it might be "['genre1', 'genre2']" or just comma separated
    # Based on earlier cat output: "french r&b" -> looks like raw string, maybe not a list representation.
    # The user said "genres is currently a string field (e.g., 'french r&b')".
    # We will treat it as a single-element list if it doesn't look like JSON.
    try:
        # Try evaluating as list if it looks like one
        if genre_str.strip().startswith("[") and genre_str.strip().endswith("]"):
            return eval(genre_str)
    except:
        pass
    
    # Fallback: simple string split by comma if multiple
    return [g.strip() for g in genre_str.split(",")]

def import_process():
    print("--- Starting Data Import Process ---")
    
    # 1. Load Contacts (The Filter)
    if not os.path.exists(CONTACTS_CSV):
        print(f"CRITICAL: {CONTACTS_CSV} not found.")
        return

    print(f"Loading {CONTACTS_CSV}...")
    df_contacts = pd.read_csv(CONTACTS_CSV)
    
    # Filter for valid found status only? 
    # User said: "ingest ONLY the subset of artists that have validated Instagram handles".
    # "Found (Network)" seems to be the success status from earlier `cat` output.
    # Let's be inclusive of anything that has a URL, or strictly "Found".
    # Checking CSV sample from history: "Not Found" exists.
    # We should filter for where instagram_url is NOT NULL/Empty OR status indicates success.
    
    df_contacts_valid = df_contacts[df_contacts['instagram_url'].notna() & (df_contacts['instagram_url'] != "")]
    valid_artist_ids = set(df_contacts_valid['id'].unique())
    
    print(f"Found {len(valid_artist_ids)} unique artists with Instagrams.")

    # 2. Load Artists
    print("Loading Artist CSVs...")
    dfs = []
    if os.path.exists(ARTISTS_CSV_1):
        dfs.append(pd.read_csv(ARTISTS_CSV_1))
    if os.path.exists(ARTISTS_CSV_2):
        dfs.append(pd.read_csv(ARTISTS_CSV_2))
    
    if not dfs:
        print("No artist CSVs found.")
        return

    df_artists = pd.concat(dfs, ignore_index=True)
    total_artists = len(df_artists)
    print(f"Total artists in raw CSVs: {total_artists}")

    # Create base filtering
    df_artists_filtered = df_artists[df_artists['id'].isin(valid_artist_ids)].copy()
    # Deduplicate: Ensure unique IDs before insert to avoid "ON CONFLICT" batch error
    df_artists_filtered = df_artists_filtered.drop_duplicates(subset=['id'])

    print(f"Artists to be imported (Actionable & Unique): {len(df_artists_filtered)}")
    
    if len(df_artists_filtered) == 0:
        print("No actionable artists found. Aborting import.")
        return

    # 4. Prepare Data for DB
    db = DatabaseManager()
    
    # Initialize DB (Safe to run multiple times, creates tables if missing)
    # schema path correction: it's in the parent root relative to src usually, 
    # but script runs from root? Let's assume script runs from root 'BeatMachAI_Busca_Instagram'
    db.init_db(SCHEMA_FILE)

    # --- Prepare Artists Data ---
    artists_tuples = []
    for _, row in df_artists_filtered.iterrows():
        # Schema: spotify_id, name, popularity, followers, country_code, raw_genres, moods, tier, outreach_status, created_at
        artists_tuples.append((
            row['id'],
            row['name'],
            row.get('popularity', 0),
            row.get('followers', 0),
            row.get('country_search', None), # Column was 'country_search' in csv sample
            clean_genres(row.get('genres', "")),
            [], # Moods (Empty for now)
            'A', # Tier A because they have contacts
            'Pending', # Defaults to Pending
            datetime.now()
        ))
    
    print("Upserting Artists...")
    db.upsert_artists(artists_tuples)

    # --- Prepare Contacts Data ---
    # Schema: artist_id, platform, handle, url, validation_status, source_method, last_checked
    contacts_tuples = []
    for _, row in df_contacts_valid.iterrows():
        # simple handle extraction logic or use what's there?
        # CSV has 'instagram_url'.
        url = row['instagram_url']
        handle = url.rstrip('/').split('/')[-1] if url else None
        
        status = row.get('status', 'Found')
        # Map csv status to DB enum if needed, or keep as is if it fits.
        # DB Enum: 'Verified', 'High Confidence', 'Needs Review', 'Found (Network)', 'Not Found'
        # 'Found (Network)' is in the CSV.
        
        contacts_tuples.append((
            row['id'],
            'Instagram',
            handle,
            url,
            status,
            'Playwright Interceptor', # As per user comment, marking source.
            datetime.now()
        ))

    print("Upserting Contacts...")
    db.upsert_contacts(contacts_tuples)
    
    print("--- Import Complete ---")

if __name__ == "__main__":
    import_process()
