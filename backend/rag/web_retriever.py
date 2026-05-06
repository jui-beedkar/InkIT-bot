import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def search_website(query):
    """
    Dynamically searches the INK IT Solutions website for the query.
    It checks key pages and scrapes them live to find relevant content.
    """
    base_url = "https://www.inkitsolutions.com.au/"
    
    # Key pages to check dynamically
    pages_to_check = [
        "",
        "services",
        "about-us",
        "contact-us",
        "industries",
        "careers",
        "sap-s4-hana-implementation-and-support-services",
        "sap-successfactors-implementation-support-services"
    ]
    
    results = []
    query_words = set(re.findall(r'\w+', query.lower()))
    
    print(f"Web Retriever: Searching live for '{query}'...")

    for path in pages_to_check:
        url = urljoin(base_url, path)
        try:
            headers = {'User-Agent': 'InkieBot/LiveSearch'}
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            # Extract meaningful text
            text_blocks = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                block_text = tag.get_text().strip()
                if len(block_text) > 40:
                    # Check if query matches block
                    block_words = set(re.findall(r'\w+', block_text.lower()))
                    if query_words & block_words: # Intersection
                        text_blocks.append(block_text)
            
            if text_blocks:
                combined_content = " ".join(text_blocks[:5]) # Take top 5 blocks
                results.append({
                    "content": combined_content,
                    "url": url,
                    "title": soup.title.string.strip() if soup.title else "INK IT Solutions"
                })
                
                # If we found a very good match, we can stop early
                if len(results) >= 2:
                    break
                    
        except Exception as e:
            print(f"Web Retriever Error on {url}: {e}")
            continue
            
    return results