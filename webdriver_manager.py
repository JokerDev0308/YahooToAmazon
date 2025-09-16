from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH

import os
import platform

class WebDriverManager:
    _drivers = {}

    @classmethod
    def get_driver(cls, profile_name: str):
        """Create or return a WebDriver instance for the given profile name."""
        if profile_name not in cls._drivers:
            options = Options()

            # Use a dedicated Chrome profile directory
            user_data_dir = os.path.abspath(f"./chrome_profiles/{profile_name}")
            os.makedirs(user_data_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={user_data_dir}")

            # Headless configuration
            if HEADLESS:
                options.add_argument("--headless=new")  # modern headless mode
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-blink-features=AutomationControlled")

                # Set Chrome binary location
                if platform.system() == "Linux":
                    options.binary_location = "/usr/bin/google-chrome"
                elif platform.system() == "Windows":
                    options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

                options.add_argument("--remote-debugging-port=0")  # optional

            # Setup ChromeDriver service
            service = Service(CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(TIMEOUT)

            # Store the driver for this profile
            cls._drivers[profile_name] = driver

        return cls._drivers[profile_name]

    @classmethod
    def close_all(cls):
        """Quit and clear all WebDriver instances."""
        for name, driver in cls._drivers.items():
            try:
                driver.quit()
            except Exception:
                pass
        cls._drivers.clear()
