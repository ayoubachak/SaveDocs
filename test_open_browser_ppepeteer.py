import asyncio
import os
from time import sleep


PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch

async def open_url(url):
    # Launch the browser in non-headless mode to make it visible
    browser = await launch(headless=False, executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', userDataDir="C:\\Users\\aachak\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 4")
    page = await browser.newPage()
    await page.goto(url)
    print(f"Opened {url}")
    # Keep the script running to prevent the browser from closing
    await page.waitForSelector('body')  # This is just to ensure the page loaded
    print("Browser will remain open. Close it manually when done.")

url = 'https://cucumber.io'  # Change this to your desired URL

# Run the function
asyncio.get_event_loop().run_until_complete(open_url(url))