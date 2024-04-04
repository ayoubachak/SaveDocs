import asyncio
import requests  # Import requests library
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
import os


PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch

async def fetch_and_save_html(url, html_path):
    # Fetch HTML content using requests
    response = requests.get(url, verify=False)
    html_content = response.text

    # Save HTML content to a local file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML content saved to {html_path}")
async def generate_pdf(html_path, pdf_path):
    browser = await launch(headless=False)  # Set headless option to False
    page = await browser.newPage()

    # Load the local HTML file
    await page.goto(f'file:///C:/Users/aachak/Work/Tools/SaveDocs/{html_path}', {'waitUntil': 'networkidle0'})  # Wait for the network to be idle
    print("Page loaded successfully.")

    # Generate PDF from the rendered HTML
    await page.pdf({'path': pdf_path, 'format': 'A4'})

    await browser.close()

async def main(url, html_path, pdf_path):
    await fetch_and_save_html(url, html_path)
    await generate_pdf(html_path, pdf_path)

url = 'https://cucumber.io'
html_path = 'html/cucumber.html'
pdf_path = 'pdfs/cucumber.pdf'

# Run the function
asyncio.get_event_loop().run_until_complete(main(url, html_path, pdf_path))