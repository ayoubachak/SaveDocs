import asyncio
import os

PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch


async def generate_pdf(url, pdf_path):
    browser = await launch(headless=False)  # Set headless option to False
    page = await browser.newPage()

    await page.goto(url, {'waitUntil': 'networkidle0'})  # Wait for the network to be idle
    print("Page loaded successfully.")

    await page.pdf({'path': pdf_path, 'format': 'A4'})

    await browser.close()

# Run the function
asyncio.get_event_loop().run_until_complete(generate_pdf('https://cucumber.io', 'cucumber.pdf'))
