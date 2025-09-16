from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from config import TIMEOUT
from webdriver_manager import WebDriverManager

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFleamarketScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver('fleamarket0914')

    def run(self, url):
        """Scrape product details from a Yahoo Flea Market product page."""
        data = {}

        logger.info(f"Scraping URL: {url}")

        try:
            self.driver.get(url)

            # Wait for a key element to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".kKVxMl"))
            )

            # Product Name
            product_name = self._safe_find('.cbMEDL')
            if product_name == "N/A":
                product_name = self._safe_find('h1')

            # Price
            raw_price = self._safe_find('.eZCKPx')
            if raw_price == "N/A":
                raw_price = self._safe_find('.Price__value')
            price = self.clean_price(raw_price)

            # Product Condition
            condition = self._safe_find('.fxgRfG')
            if condition == "N/A":
                condition = self._safe_find('.ProductCondition__value')

            # Seller ID
            seller_href = self._safe_find('.bPwzBk a', "href")
            if seller_href == "N/A":
                seller_href = self._safe_find('a[href*="user/"]', "href")
            seller_id = self._extract_id(seller_href, 'user')

            # Product Images
            image_selectors = [
                '.sc-9b33bf35-3.bDgrAu',
                '.bDgrAu',
                'img'
            ]

            image_elements = []
            for selector in image_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    image_elements = elements
                    break  # Use first working selector

            unique_image_urls = []
            for img in image_elements:
                try:
                    src = img.get_attribute('src')
                    if src and src.startswith("http") and src not in unique_image_urls:
                        unique_image_urls.append(src)
                except Exception:
                    continue  # Skip broken image elements

            unique_image_urls = unique_image_urls[:8]  # Limit to 8 images

            # Extract item ID from URL
            item_id = self._extract_id(url, "item")

            # Assemble data dictionary
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

            logger.info(f"Scraping completed for: {url}")
            return data

        except Exception as e:
            logger.error(f"Scraping failed for URL {url}: {e}")
            return data

    def _safe_find(self, selector, attribute=None):
        """Safely find an element and return its text or specified attribute, or 'N/A'."""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
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
        """Extract ID from string based on a prefix."""
        try:
            if not text or text == "N/A":
                return "N/A"
            match = re.search(rf'{key}/([a-zA-Z0-9_-]+)', text)
            return match.group(1) if match else "N/A"
        except Exception as e:
            logger.debug(f"Failed to extract ID with key '{key}': {e}")
            return "N/A"

    def clean_price(self, price_str):
        """Convert price string like '1,000円（税込）' to float."""
        try:
            if not price_str or price_str == "N/A":
                return 0.0
            match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)', price_str)
            if match:
                cleaned_price = match.group(0).replace(',', '')
                return float(cleaned_price)
            return 0.0
        except Exception as e:
            logger.debug(f"Failed to clean price from string '{price_str}': {e}")
            return 0.0

    def close(self):
        """Close the Selenium driver."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Web driver closed.")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
