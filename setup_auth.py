import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser in headful mode so user can see and interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to Spotify login page...")
        page.goto("https://accounts.spotify.com/login")

        print("Please log in manually in the browser window.")
        print("Waiting for redirect to open.spotify.com...")

        # Wait until we are redirected to the main player page
        # We increase timeout to 300 seconds (5 minutes) to give user plenty of time
        try:
            page.wait_for_url("https://open.spotify.com/**", timeout=300000)
            print("Login detected!")
        except Exception as e:
            print(f"Timeout or error waiting for login: {e}")
            browser.close()
            return

        # Wait a bit to ensure cookies are fully set
        time.sleep(5)

        # Save storage state
        auth_file = "spotify_auth.json"
        context.storage_state(path=auth_file)
        print(f"Authentication state saved to {auth_file}")

        browser.close()

if __name__ == "__main__":
    run()
