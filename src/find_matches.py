from src.db_manager import DatabaseManager


class ArtistMatcher:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()

    def find_matches(self, style, vibe, limit=50):
        """
        Finds artists with a cascading strategy:
        1. Tier 1 (Strict): Matches both Style AND Vibe.
        2. Tier 2 (Broad): Matches Style only (if Tier 1 < 5 results).
        """
        # Tier 1: Strict Match
        query_strict = """
            SELECT
                a.spotify_id,
                a.name,
                c.handle,
                array_agg(DISTINCT gm.raw_genre) as matched_genres,
                a.popularity
            FROM artists a
            JOIN genre_mappings gm ON gm.raw_genre = ANY(a.raw_genres)
            LEFT JOIN contacts c ON c.artist_id = a.spotify_id AND c.platform = 'Instagram'
            WHERE
                UPPER(gm.master_style) = UPPER(%s)
                AND UPPER(gm.vibe) = UPPER(%s)
                AND a.tier = 'A'
            GROUP BY a.spotify_id, a.name, c.handle, a.popularity
            ORDER BY a.popularity DESC
            LIMIT %s;
        """

        # Tier 2: Broad Match (Style only), excluding already found artists
        query_broad = """
            SELECT
                a.spotify_id,
                a.name,
                c.handle,
                array_agg(DISTINCT gm.raw_genre) as matched_genres,
                a.popularity
            FROM artists a
            JOIN genre_mappings gm ON gm.raw_genre = ANY(a.raw_genres)
            LEFT JOIN contacts c ON c.artist_id = a.spotify_id AND c.platform = 'Instagram'
            WHERE
                UPPER(gm.master_style) = UPPER(%s)
                AND a.tier = 'A'
                AND a.spotify_id != ALL(%s)
            GROUP BY a.spotify_id, a.name, c.handle, a.popularity
            ORDER BY a.popularity DESC
            LIMIT %s;
        """
        
        try:
            with self.db.get_connection() as conn, conn.cursor() as cur:
                # --- Step 1: Strict Search ---
                cur.execute(query_strict, (style, vibe, limit))
                rows_strict = cur.fetchall()
                
                results = []
                found_ids = []
                
                for row in rows_strict:
                    # row structure: 0=id, 1=name, 2=handle, 3=genres, 4=popularity
                    results.append({
                        "name": row[1],
                        "handle": row[2] if row[2] else "N/A",
                        "matched_genres": row[3],
                        "popularity": row[4],
                        "match_type": "PERFECT"
                    })
                    found_ids.append(row[0])

                # --- Step 2: Broad Fallback (if needed) ---
                if len(results) < 5:
                    remaining_slots = limit - len(results)
                    # Safety: Ensure exclusion list is not empty for SQL syntax
                    exclusion_ids = found_ids if found_ids else ['']
                    
                    cur.execute(query_broad, (style, exclusion_ids, remaining_slots))
                    rows_broad = cur.fetchall()
                    
                    for row in rows_broad:
                        results.append({
                            "name": row[1],
                            "handle": row[2] if row[2] else "N/A",
                            "matched_genres": row[3],
                            "popularity": row[4],
                            "match_type": "BROAD_STYLE"
                        })
                        
                return results

        except Exception as e:
            print(f"Error querying database: {e}")
            return []

if __name__ == "__main__":
    # Test stub
    matcher = ArtistMatcher()
    print("Testing Matcher with TRAP / DARK...")
    matches = matcher.find_matches("TRAP", "DARK", limit=5)
    for m in matches:
        print(m)
