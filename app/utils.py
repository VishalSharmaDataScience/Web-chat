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
def simulate_human_interaction(url, query, depth=3):
    """
    Dynamically navigate a website to fulfill a query, recursively exploring links as needed.

    Parameters:
        url (str): Starting URL.
        query (str): User's query.
        depth (int): Maximum depth for link exploration.

    Returns:
        str: Extracted content matching the query or an appropriate error message.
    """
    from urllib.parse import urljoin
    import re

    def match_query(content, keywords):
        """Check if the content matches the query keywords."""
        return any(keyword in content.lower() for keyword in keywords)

    with sync_playwright() as p:
        try:
            print(f"Launching browser to explore {url}...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to the main page
            page.goto(url, timeout=20000)
            page.wait_for_load_state("domcontentloaded")

            print("Extracting content from the current page...")
            page_content = page.inner_text("body").lower()
            query_keywords = query.lower().split()

            # Check if content on the current page matches the query
            if match_query(page_content, query_keywords):
                print("Matching content found on the main page.")
                return page_content

            # Stop if depth limit is reached
            if depth == 0:
                print("Depth limit reached. Stopping exploration.")
                return "Relevant information not found within the exploration depth."

            # Extract all links from the current page
            print("Extracting links for further exploration...")
            links = page.query_selector_all("a")
            sub_links = [
                urljoin(url, link.get_attribute("href"))
                for link in links if link.get_attribute("href")
            ]

            # Explore sub-links recursively
            for sub_link in sub_links:
                print(f"Exploring sub-link: {sub_link}")
                page.goto(sub_link, timeout=20000)
                page.wait_for_load_state("domcontentloaded")
                sub_content = page.inner_text("body").lower()

                if match_query(sub_content, query_keywords):
                    print("Matching content found in a sub-link.")
                    browser.close()
                    return sub_content

                # Recurse further into the sub-link
                result = simulate_human_interaction(sub_link, query, depth - 1)
                if "Relevant information not found" not in result:
                    browser.close()
                    return result

            print("No matching content found in sub-links.")
            browser.close()
            return "Could not find relevant content for your query."
        except Exception as e:
            return f"Error during interaction: {str(e)}"
