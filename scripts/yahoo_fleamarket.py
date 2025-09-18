from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from config import TIMEOUT
from webdriver_manager import WebDriverManager

import logging
from time import sleep
from random import randint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YahooFleamarketScraper:
    def run(self, url, profile_name):
        """Scrape product details from a Yahoo Flea Market product page."""
        data = {}
        logger.info(f"Scraping Yahoo Flea Market URL: {url} (Profile: {profile_name})")

        driver = None
        sleep(randint(0, 20))  # Initial wait to ensure any previous operations are settled

        try:
            # Use unique Chrome profile per session
            driver = WebDriverManager.get_driver(profile_name)
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".kKVxMl"))
            )

            # Product Name
            product_name = self._safe_find(driver, '.cbMEDL')
            if product_name == "N/A":
                product_name = self._safe_find(driver, 'h1')

            # Price
            raw_price = self._safe_find(driver, '.eZCKPx')
            if raw_price == "N/A":
                raw_price = self._safe_find(driver, '.Price__value')
            price = self.clean_price(raw_price)

            # Product Condition
            condition = self._safe_find(driver, '.fxgRfG')
            if condition == "N/A":
                condition = self._safe_find(driver, '.ProductCondition__value')

            # Seller ID
            seller_href = self._safe_find(driver, '.bPwzBk a', "href")
            if seller_href == "N/A":
                seller_href = self._safe_find(driver, 'a[href*="user/"]', "href")
            seller_id = self._extract_id(seller_href, 'user')

            # Product Images
            image_selectors = [
                '.sc-9b33bf35-3.bDgrAu',
                '.bDgrAu',
                'img'
            ]

            image_elements = []
            for selector in image_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    image_elements = elements
                    break

            unique_image_urls = []
            for img in image_elements:
                try:
                    src = img.get_attribute('src')
                    if src and src.startswith("http") and src not in unique_image_urls:
                        unique_image_urls.append(src)
                except Exception:
                    continue

            unique_image_urls = unique_image_urls[:8]  # Limit to 8

            # Extract item ID from URL
            item_id = self._extract_id(url, "item")

            # Data dict
            data = {
                '商品URL': url,
                '商品画像': unique_image_urls[0] if unique_image_urls else 'N/A',
                '商品名': product_name,
                '商品ID': item_id,
                '販売価格': price,
                '商品状態': condition,
                '出品者ID': seller_id,
            }

            # Add image URLs
            for i, img_url in enumerate(unique_image_urls, 1):
                data[f'画像URL{i}'] = img_url

            logger.info(f"Scraping successful for: {url}")
            return data

        except Exception as e:
            logger.error(f"Scraping failed for URL {url}: {e}")
            return data

        finally:
            # Close the driver after use (or let WebDriverManager handle global cleanup)
            try:
                if driver:
                    driver.quit()
                    logger.info(f"Driver closed for profile: {profile_name}")
            except Exception as e:
                logger.error(f"Failed to close driver for {profile_name}: {e}")

    def _safe_find(self, driver, selector, attribute=None):
        """Safely extract text or attribute from a single element."""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            if attribute:
                value = element.get_attribute(attribute)
                return value.strip() if value else "N/A"
            else:
                text = element.text
                return text.strip() if text else "N/A"
        except Exception:
            logger.debug(f"Element not found for selector: {selector}")
            return "N/A"

    def _extract_id(self, text, key):
        """Extract value after a specific key in a URL (e.g., user/item ID)."""
        try:
            if not text or text == "N/A":
                return "N/A"
            match = re.search(rf'{key}/([a-zA-Z0-9_-]+)', text)
            return match.group(1) if match else "N/A"
        except Exception as e:
            logger.debug(f"Failed to extract ID with key '{key}': {e}")
            return "N/A"

    def clean_price(self, price_str):
        """Convert price string like '1,000円' to float 1000.0."""
        try:
            if not price_str or price_str == "N/A":
                return 0.0
            match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)', price_str)
            if match:
                cleaned_price = match.group(0).replace(',', '')
                return float(cleaned_price)
            return 0.0
        except Exception as e:
            logger.debug(f"Price cleaning failed for '{price_str}': {e}")
            return 0.0
