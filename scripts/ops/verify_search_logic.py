import sys
import os

# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.find_matches import ArtistMatcher
from src.db_manager import DatabaseManager

def test_search(matcher, style, vibe, test_name):
    print(f"\n{'='*60}")
    print(f"--- {test_name} ---")
    print(f"Searching for Style: '{style}' | Vibe: '{vibe}'")
    
    results = matcher.find_matches(style, vibe, limit=10)
    
    print(f"Total Found: {len(results)}")
    
    tier1_count = sum(1 for r in results if r['match_type'] == 'PERFECT')
    tier2_count = sum(1 for r in results if r['match_type'] == 'BROAD_STYLE')
    
    print(f"Tier 1 (Strict/Perfect): {tier1_count}")
    print(f"Tier 2 (Broad/Fallback): {tier2_count}")
    
    # Show first few results details
    print("Top Results:")
    for i, res in enumerate(results[:10]):
        badge = "🔥" if res['match_type'] == 'PERFECT' else "⚡"
        print(f"  {i+1}. {badge} [{res['match_type']}] {res['name']} ({res['handle']})")

def main():
    try:
        db = DatabaseManager()
        matcher = ArtistMatcher(db)
        
        # 1. Test Strict Success
        # Assuming TRAP / DARK is a common combination in the DB
        test_search(matcher, "TRAP", "DARK", "TEST CASE 1: STRICT SUCCESS (Expected: Mostly Perfect)")
        
        # 2. Test Forced Fallback
        # TRAP is valid, 'NON_EXISTENT' vibe forces strict match to fail
        test_search(matcher, "TRAP", "NON_EXISTENT_VIBE_12345", "TEST CASE 2: FORCED FALLBACK (Expected: All Broad)")
        
    except Exception as e:
        print(f"An error occurred during verification: {e}")

if __name__ == "__main__":
    main()
