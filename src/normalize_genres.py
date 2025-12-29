
import os
import sys
import logging
from db_manager import DatabaseManager

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_text(text):
    """Normalize text for comparison (lowercase, strip)."""
    if not text:
        return ""
    return text.lower().strip()

def determine_style_and_vibe(genre):
    """
    Apply specific logic to determine Master Style and Vibe based on raw genre.
    """
    g_lower = normalize_text(genre)
    
    # Logic 1: Afro/Alte/Amapiano
    if any(x in g_lower for x in ["afro", "alté", "alte", "amapiano"]):
        return "AFROBEATS", "VIBEY"
    
    # Logic 2: Dark R&B
    if "dark r&b" in g_lower:
        return "RNB", "DARK"
    
    # Logic 3: Boom Bap / Jazz Rap
    if "boom bap" in g_lower or "jazz rap" in g_lower:
        return "BOOMBAP", "CHILL/LYRICAL"
    
    # Logic 4: Trap
    if "trap" in g_lower:
        # User did not specify vibe for TRAP, leaving None or could be 'HYPE'
        return "TRAP", None 
    
    # Logic 5: International Rap
    if "j-rap" in g_lower or "french rap" in g_lower:
        return "HIPHOP_INTL", None

    # Default fallbacks (optional, or leave as None)
    return None, None

def run_normalization():
    db = DatabaseManager()
    
    # 1. Schema Update / Reset
    logging.info("Updating schema for `genre_mappings`...")
    
    # We will drop and recreate to ensure clean state and correct columns
    drop_sql = "DROP TABLE IF EXISTS genre_mappings;"
    create_sql = """
    CREATE TABLE IF NOT EXISTS genre_mappings (
        raw_genre VARCHAR(255) PRIMARY KEY,
        master_style VARCHAR(100),
        vibe VARCHAR(100),
        is_mapped BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(drop_sql)
            cur.execute(create_sql)
            logging.info("Table `genre_mappings` (re)created successfully.")

    # 2. Extract Unique Genres from Artists
    logging.info("Fetching unique genres from `artists` table...")
    fetch_genres_sql = """
        SELECT DISTINCT unnest(raw_genres) as genre 
        FROM artists 
        WHERE raw_genres IS NOT NULL;
    """
    
    unique_genres = []
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(fetch_genres_sql)
            rows = cur.fetchall()
            unique_genres = [r[0] for r in rows if r[0]]
            
    logging.info(f"Found {len(unique_genres)} unique genres.")

    # 3. Build Mapping Dictionary
    mappings_to_insert = []
    
    for genre in unique_genres:
        style, vibe = determine_style_and_vibe(genre)
        
        # We insert even if style is None, to track that we saw this genre (is_mapped=False/True logic below)
        # Or maybe we only insert mapped ones? 
        # Usually normalization tables should contain all raw values.
        
        is_mapped = True if style else False
        mappings_to_insert.append((genre, style, vibe, is_mapped))

    # 4. Populate genre_mappings
    insert_sql = """
        INSERT INTO genre_mappings (raw_genre, master_style, vibe, is_mapped)
        VALUES %s
        ON CONFLICT (raw_genre) DO UPDATE SET
            master_style = EXCLUDED.master_style,
            vibe = EXCLUDED.vibe,
            is_mapped = EXCLUDED.is_mapped;
    """
    
    if mappings_to_insert:
        from psycopg2.extras import execute_values
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                execute_values(cur, insert_sql, mappings_to_insert)
                logging.info(f"Inserted/Updated {len(mappings_to_insert)} genre mappings.")
    else:
        logging.info("No genres to insert.")

    # Verification: Show 10 examples
    verify_output()

def verify_output():
    db = DatabaseManager()
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            logging.info("\n--- Verification: 10 Mapped Examples ---")
            query = """
                SELECT raw_genre, master_style, vibe 
                FROM genre_mappings 
                WHERE is_mapped = TRUE 
                LIMIT 10;
            """
            cur.execute(query)
            rows = cur.fetchall()
            for r in rows:
                print(f"Genre: {r[0]} | Style: {r[1]} | Vibe: {r[2]}")
                
            # Also show some unmapped ones?
            # query_unmapped = "SELECT raw_genre FROM genre_mappings WHERE is_mapped = FALSE LIMIT 5;"
            # cur.execute(query_unmapped)
            # rows_unmapped = cur.fetchall()
            # print("\nExamples of Unmapped Genres:")
            # for r in rows_unmapped:
            #     print(f"Genre: {r[0]}")

if __name__ == "__main__":
    run_normalization()
