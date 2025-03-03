# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 1  # Selenium wait timeout
CHROMEDRIVER_PATH = "drivers/chromedriver-linux64/chromedriver"
JANCODE_SCV = 'data/jan_codes.csv'
SCRAPED_XLSX = 'data/scraped_data.xlsx'

RUNNING = "tmp/running"
WAITING = False
CURRENT_USER = None
LOGIN_STATE = {}