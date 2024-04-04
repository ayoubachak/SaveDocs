import requests
from bs4 import BeautifulSoup
import pdfkit

# Replace 'url_of_the_documentation' with the actual URL you want to crawl
url = 'https://cucumber.io/docs/guides/overview/'

# Fetch the web page
response = requests.get(url, verify=False)
html_content = response.text

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')
# Here, you might want to clean up the content or extract specific parts

# Convert HTML to PDF - you may need to specify the full path to the wkhtmltopdf executable in pdfkit configuration
pdfkit.from_string(str(soup), 'output.pdf')

