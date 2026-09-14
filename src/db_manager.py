import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

class DatabaseManager:
    def __init__(self, connection_string=None):
        if connection_string:
            self.connection_string = connection_string
        else:
            # Default to environment variables or localhost default
            self.connection_string = os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:eGydmHcmYmXwAbclmUlBNeNVbCpWEwBF@postgres.railway.internal:5432/railway"
            )

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_db(self, schema_file="create_tables.sql"):
        """Reads the SQL file and executes it to create tables."""
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
            
        with open(schema_file, "r") as f:
            sql_script = f.read()
            
        with self.get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql_script)
            print("Database initialized successfully.")

    def upsert_artists(self, artists_data):
        """
        Upsert artists into the database.
        artists_data: List of tuples corresponding to columns.
        """
        query = """
            INSERT INTO artists (
                spotify_id, name, popularity, followers, country_code, raw_genres, moods, tier, outreach_status, created_at
            ) VALUES %s
            ON CONFLICT (spotify_id) DO UPDATE SET
                popularity = EXCLUDED.popularity,
                followers = EXCLUDED.followers,
                tier = EXCLUDED.tier,
                outreach_status = EXCLUDED.outreach_status,
                raw_genres = EXCLUDED.raw_genres;
        """
        with self.get_connection() as conn, conn.cursor() as cur:
            execute_values(cur, query, artists_data)
            print(f"Upserted {len(artists_data)} artists.")

    def upsert_contacts(self, contacts_data):
        """
        Upsert contacts into the database.
        contacts_data: List of tuples.
        """
        query = """
            INSERT INTO contacts (
                artist_id, platform, handle, url, validation_status, source_method, last_checked
            ) VALUES %s
            ON CONFLICT (artist_id, platform) DO UPDATE SET
                handle = EXCLUDED.handle,
                url = EXCLUDED.url,
                validation_status = EXCLUDED.validation_status,
                last_checked = CURRENT_TIMESTAMP;
        """
        with self.get_connection() as conn, conn.cursor() as cur:
            execute_values(cur, query, contacts_data)
            print(f"Upserted {len(contacts_data)} contacts.")
