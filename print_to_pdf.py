from selenium import webdriver
import json

chrome_options = webdriver.ChromeOptions()
settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')
CHROMEDRIVER_PATH = 'drivers/chromedriver'
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://google.com")
driver.execute_script('window.print();')
driver.quit()