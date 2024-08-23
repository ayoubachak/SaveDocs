import asyncio
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging

PYPPETEER_CHROMIUM_REVISION = '1263111'
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from pyppeteer import launch
import argparse

class WebCrawler:
    def __init__(self, max_concurrent_browsers=5):
        self.visited_urls = set()
        self.results_dir = "crawler_results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.current_website_name = None
        self.max_concurrent_browsers = max_concurrent_browsers
        self.semaphore = asyncio.Semaphore(max_concurrent_browsers)
        self.browser_pool = []
        self.url_queue = asyncio.Queue()
        self.active_tasks = 0
        self.logger = self.setup_logger()
        
    def setup_logger(self):
        logger = logging.getLogger('web_crawler')
        logger.setLevel(logging.DEBUG)

        # Create console handler and set level to INFO
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        logger.addHandler(ch)
        return logger
    
    async def launch_browser_instance(self, headless=False):
        browser = await launch(headless=headless)
        self.browser_pool.append(browser)
        try:
            while True:
                await asyncio.sleep(0.5)  # Prevents tight loop when waiting for URLs.
                if self.url_queue.empty() and self.active_tasks == 0:
                    break  # Exit if no more URLs are expected.
                if not self.url_queue.empty():
                    url = await self.url_queue.get()
                    await self.process_url(browser, url)
                    self.url_queue.task_done()
        finally:
            await browser.close()
            self.browser_pool.remove(browser)
                
    def extract_website_name(self, url):
        # Remove protocol and www from URL
        clean_url = re.sub(r'^https?://(www\.)?', '', url)
        # Extract the domain name
        domain = clean_url.split('/')[0]
        # Replace special characters with underscores
        clean_domain = re.sub(r'[^\w\s-]', '_', domain)
        # Replace whitespace with underscores and convert to lowercase
        clean_domain = clean_domain.strip().lower().replace(' ', '_')
        return clean_domain
    
    async def fetch_and_save_html(self, url, html_path):
        try:
            # Fetch HTML content using requests
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Raise an exception for HTTP errors
            html_content = response.text

            # Save HTML content to a local file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"HTML content saved to {html_path}")
            return html_path
        except Exception as e:
            self.logger.error(f"Error fetching HTML from {url}: {e}")
            return None
        
    def sanitize_directory_name(self, url):
        # Remove protocol and www from URL
        clean_url = re.sub(r'^https?://(www\.)?', '', url)

        # Replace special characters with underscores
        clean_url = re.sub(r'[^\w\s-]', '_', clean_url)

        # Replace whitespace with underscores and convert to lowercase
        clean_url = clean_url.strip().lower().replace(' ', '_')

        return clean_url
    async def generate_pdf(self, browser, html_path, pdf_path):
        try:
            page = await browser.newPage()
            # Load the local HTML file
            print(f'file:///{os.path.join(os.getcwd(), html_path)}')
            await page.goto(f'file:///{os.path.join(os.getcwd(), html_path)}', {'waitUntil': 'networkidle0'})
            self.logger.info("Page loaded successfully.")
            # Generate PDF from the rendered HTML
            await page.pdf({'path': pdf_path, 'format': 'A4'})
        except Exception as e:
            self.logger.error(f"Error generating PDF from {html_path}: {e}")
        finally:
            await page.close()  # Consider closing the page instead of the entire browser

                
    async def process_url(self, browser, url):
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        self.active_tasks += 1

        website_name = self.extract_website_name(url)
        if self.current_website_name is None:
            self.current_website_name = website_name
        
        website_dir = os.path.join(self.results_dir, self.current_website_name, self.sanitize_directory_name(url))
        os.makedirs(website_dir, exist_ok=True)
        
        html_filename = os.path.join(website_dir, "index.html")
        html_path = await self.fetch_and_save_html(url, html_filename)

        if html_path:
            pdf_filename = os.path.join(website_dir, "index.pdf")
            await self.generate_pdf(browser, html_path, pdf_filename)

            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    # print('Found : \n' + a_tag['href'] + " in " + url)
                    next_url = urljoin(url, a_tag['href'])
                    next_url_base = next_url.split('#')[0]
                    if next_url_base.startswith(url) and next_url_base not in self.visited_urls:
                        await self.url_queue.put(next_url_base)

        self.active_tasks -= 1

    async def crawl_website(self, start_url, headless=False):
        await self.url_queue.put(start_url)
        workers = [asyncio.create_task(self.launch_browser_instance(headless=headless)) for _ in range(self.max_concurrent_browsers)]
        await asyncio.gather(*workers)

async def main():
    # Example Command : python webcrawler.py --url https://example.com --num_workers 5 --headless
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True, help="URL to Crawl")
    parser.add_argument("--num_workers", type=int, default=5, help="Number of workers")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode") # will either show the browsers or not 
    args = parser.parse_args()
    start_url = args.url
    num_workers = args.num_workers
    headless = args.headless
    print("Starting %d workers on %s using %s headless mode"%(num_workers, start_url, headless) )
    
    crawler = WebCrawler(max_concurrent_browsers=num_workers)
    try:
        await crawler.crawl_website(start_url, headless=headless)
    finally:
        for browser in crawler.browser_pool:
            await browser.close()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())