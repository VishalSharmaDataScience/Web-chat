import requests
from cache import Cache
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright


cache = Cache()

def check_website_exists(url):
    """Check if the provided website URL is reachable."""
    try:
        # Send a HEAD request to check if the website exists
        response = requests.head(url, timeout=5)
        if response.status_code < 400:  # Status codes < 400 mean the site is reachable
            return True, f"Website is reachable: {url}"
        else:
            return False, f"Website returned status code {response.status_code}: {url}"
    except requests.RequestException as e:
        return False, f"Error accessing the website: {str(e)}"



cache = Cache()

def simulate_human_interaction(url, query):
    """
    Retrieve information from the given URL by simulating human interaction.
    Dynamically navigate to relevant sections based on the query context.
    """
    with sync_playwright() as p:
        try:
            print("Launching browser to simulate interaction...")
            browser = p.chromium.launch(headless=True)  # Use headless mode for efficiency
            context = browser.new_context()
            page = context.new_page()

            print("Navigating to the website...")
            page.goto(url, timeout=20000)

            print("Analyzing query context...")
            query_keywords = query.lower().split()  # Basic keyword extraction from query

            print("Looking for relevant links...")
            links = page.query_selector_all("a")
            relevant_links = []

            for link in links:
                text = link.inner_text().lower() if link.inner_text() else ""
                href = link.get_attribute("href")
                # Check if the link text matches any keywords in the query
                if any(keyword in text for keyword in query_keywords):
                    relevant_links.append(href)

            if not relevant_links:
                print("No relevant links found. Returning main page content.")
                page_content = page.inner_text("body")
                browser.close()
                return page_content

            # Navigate to the first relevant link and extract content
            for link in relevant_links:
                print(f"Navigating to {link}...")
                if link.startswith("http"):
                    page.goto(link)
                else:
                    page.goto(f"{url.rstrip('/')}/{link.lstrip('/')}")

                page.wait_for_load_state("domcontentloaded")

                print("Extracting content from the relevant section...")
                section_content = page.inner_text("body")  # Extract text content from the page body
                if section_content.strip():
                    browser.close()
                    return section_content

            browser.close()
            return "Unable to find detailed content for the query."
        except Exception as e:
            return f"Error during interaction: {str(e)}"
