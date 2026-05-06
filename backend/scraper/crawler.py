import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

class AdvancedCrawler:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.to_visit = [self.base_url]
        self.documents = []
        
        # Robots.txt parser
        self.rp = RobotFileParser()
        self.rp.set_url(urljoin(self.base_url, "robots.txt"))
        try:
            self.rp.read()
        except:
            print("Could not read robots.txt, proceeding with caution.")

    def can_fetch(self, url):
        return self.rp.can_fetch("InkieBot", url)

    def is_internal(self, url):
        parsed = urlparse(url)
        return parsed.netloc == '' or parsed.netloc == self.domain

    def clean_url(self, url):
        return url.split('#')[0].split('?')[0].rstrip('/')

    def get_category(self, url):
        path = urlparse(url).path.lower()
        if any(x in path for x in ['services', 'sap-', 'oracle-']): return "services"
        if 'industries' in path: return "industries"
        if 'careers' in path: return "careers"
        if 'contact' in path: return "contact"
        if any(x in path for x in ['blog', 'news', 'media']): return "blog"
        return "general"

    def scrape_page(self, url):
        if not self.can_fetch(url):
            print(f"Skipping (Robots.txt): {url}")
            return []

        try:
            headers = {
                'User-Agent': 'InkieBot/4.0 (Granular Chunking Upgrade)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")

            # Page Title
            page_title = soup.title.string.strip() if soup.title else "INK IT SOLUTIONS"
            
            # Remove junk
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            # GRANULAR CHUNKING: Split by headings
            # This ensures we get specific answers for specific topics
            chunks = []
            current_heading = page_title
            current_text = []

            # We iterate through all potential content tags in order
            for el in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'span']):
                if el.name in ['h1', 'h2', 'h3', 'h4']:
                    # Save the previous chunk if it has content
                    if current_text:
                        chunks.append({
                            "title": f"{page_title} - {current_heading}",
                            "content": " ".join(current_text)
                        })
                        current_text = []
                    current_heading = el.get_text().strip()
                else:
                    txt = el.get_text().strip()
                    if len(txt) > 20:
                        current_text.append(txt)
            
            # Add final chunk
            if current_text:
                chunks.append({
                    "title": f"{page_title} - {current_heading}",
                    "content": " ".join(current_text)
                })

            # Create documents from chunks
            for chunk in chunks:
                if len(chunk["content"]) < 30: continue
                
                doc = {
                    "id": f"chunk_{len(self.documents) + 1:04d}",
                    "title": chunk["title"],
                    "content": chunk["content"],
                    "url": url,
                    "category": self.get_category(url)
                }
                self.documents.append(doc)

            print(f"Logged {len(chunks)} chunks for URL: {url}")

            # Discover internal links
            new_links = []
            for a in soup.find_all('a', href=True):
                full_url = urljoin(url, a['href'])
                clean_url = self.clean_url(full_url)
                
                if self.is_internal(clean_url) and clean_url not in self.visited_urls:
                    if not any(x in clean_url.lower() for x in ['.pdf', '.jpg', '.png', '.zip', 'tel:', 'mailto:']):
                        new_links.append(clean_url)
            
            return new_links

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def run(self):
        print(f"--- Starting Full Website Crawl: {self.base_url} ---")
        
        # Discover sitemap
        try:
            sitemap_url = urljoin(self.base_url, "sitemap.xml")
            r = requests.get(sitemap_url, timeout=10)
            if r.status_code == 200:
                urls = re.findall(r'<loc>(.*?)</loc>', r.text)
                for u in urls:
                    self.to_visit.append(self.clean_url(u))
                print(f"Sitemap loaded: Found {len(urls)} potential pages.")
        except:
            pass

        while self.to_visit:
            url = self.to_visit.pop(0)
            if url in self.visited_urls: continue
            
            self.visited_urls.add(url)
            discovered = self.scrape_page(url)
            
            for link in discovered:
                if link not in self.visited_urls and link not in self.to_visit:
                    self.to_visit.append(link)
            
            time.sleep(0.3) # Faster crawl, still respectful
            
            # Safety cap (Increased for granular chunking)
            if len(self.documents) >= 1000:
                print("Crawl limit reached (1000 chunks).")
                break

        print("\n" + "="*30)
        print(f"Total chunks indexed: {len(self.documents)}")
        print("="*30)
        
        self.save()

    def save(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        path = os.path.join(data_dir, "website_data.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        print(f"Website content indexed successfully at: {path}")

if __name__ == "__main__":
    crawler = AdvancedCrawler("https://www.inkitsolutions.com.au/")
    crawler.run()
