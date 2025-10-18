import os
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
import html2text

def save_sites(urls, output_dir="saved_md"):
    os.makedirs(output_dir, exist_ok=True)
    visited = set()

    def crawl(url, base_domain):
        # Handle fragments by ignoring them for visited check
        url_to_check = url.split('#')[0]
        if url_to_check in visited:
            return
        visited.add(url_to_check)

        print(f"📥 Fetching: {url}")

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            return

        # convert to Markdown
        html = resp.text
        markdown = html2text.html2text(html)

        # save filename based on URL path
        parsed = urllib.parse.urlparse(url)
        
        # Create a directory structure based on the URL
        path = parsed.path.strip('/')
        if not path:
            path = 'index.html'
        
        if path.endswith('/'):
            path += 'index.html'

        # Separate path and filename
        path, filename = os.path.split(path)
        filename, _ = os.path.splitext(filename)
        filename += '.md'
        
        # Create directories
        dir_path = os.path.join(output_dir, parsed.netloc, path)
        os.makedirs(dir_path, exist_ok=True)
        
        filepath = os.path.join(dir_path, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {url}\n\n")
            f.write(markdown)

        # extract internal links
        soup = BeautifulSoup(html, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", href=True)]

        for link in links:
            full = urllib.parse.urljoin(url, link)
            if urllib.parse.urlparse(full).netloc == base_domain:
                crawl(full, base_domain)

    for u in urls:
        base_domain = urllib.parse.urlparse(u).netloc
        crawl(u, base_domain)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawl.py <url1> <url2> ...")
        print("       python crawl.py --file <file_with_urls>")
        sys.exit(1)

    urls_to_crawl = []
    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("Usage: python crawl.py --file <file_with_urls>")
            sys.exit(1)
        try:
            with open(sys.argv[2], 'r') as f:
                urls_to_crawl = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File not found: {sys.argv[2]}")
            sys.exit(1)
    else:
        urls_to_crawl = sys.argv[1:]

    if urls_to_crawl:
        save_sites(urls_to_crawl)
    else:
        print("No URLs to crawl.")
