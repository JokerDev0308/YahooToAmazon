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
        """Helper method to scrape details from a specific Yahoo Fleamarket product URL"""

        data = {}

        try:
            self.driver.get(url)

            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".kKVxMl"))
            )

            # Product Name: try multiple selectors
            product_name = self._safe_find('.cbMEDL')
            if product_name == "N/A":
                product_name = self._safe_find('h1')

            # Price: try multiple selectors and clean
            raw_price = self._safe_find('.eZCKPx')
            if raw_price == "N/A":
                raw_price = self._safe_find('.Price__value')
            price = self.clean_price(raw_price)

            # Condition
            condition = self._safe_find('.fxgRfG')
            if condition == "N/A":
                condition = self._safe_find('.ProductCondition__value')

            # Seller ID: try to get href from multiple selectors
            seller_href = self._safe_find('.bPwzBk a', "href")
            if seller_href == "N/A":
                seller_href = self._safe_find('a[href*="user/"]', "href")
            seller_id = self._extract_id(seller_href, 'user')

            # Images: try multiple selectors, filter empty, deduplicate
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.sc-9b33bf35-3.bDgrAu')
            if not image_elements:
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.bDgrAu')
            if not image_elements:
                image_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img')
            unique_image_urls = []
            for img in image_elements:
                src = img.get_attribute('src')
                if src and src not in unique_image_urls:
                    unique_image_urls.append(src)
            unique_image_urls = unique_image_urls[:8]

            # Build data dict
            data = {
                '商品URL': url,
                '商品画像': unique_image_urls[0] if unique_image_urls else 'N/A',
                '商品名': product_name,
                '商品ID': self._extract_id(url, "item"),
                '販売価格': price,
                '商品状態': condition,
                '出品者ID': seller_id,
            }
            for i, img_url in enumerate(unique_image_urls, 1):
                data[f'画像URL{i}'] = img_url

            return data

        except Exception as e:
            logger.error(f"URL scraping failed for {url}: {e}")
            return data

    def _safe_find(self, selector, attribute=None):
        """Helper method to safely find elements and get their text or attribute"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            if attribute:
                attr_val = element.get_attribute(attribute)
                return attr_val if attr_val else "N/A"
            else:
                text_val = element.text
                return text_val if text_val else "N/A"
        except Exception as e:
            logger.debug(f"_safe_find failed for selector {selector}: {e}")
            return "N/A"

    def _extract_id(self, href, pre):
        """Helper method to extract seller ID from the href of an anchor tag"""
        try:
            if not href or href == "N/A":
                return "N/A"
            match = re.search(rf'{pre}/([a-zA-Z0-9_-]+)', href)
            if match:
                return match.group(1)
            return "N/A"
        except Exception as e:
            logger.error(f"Failed to extract seller ID: {e}")
            return "N/A"

    def clean_price(self, price_str):
        """Extract numeric price from string like '1,000円（税込）'"""
        try:
            if not price_str or price_str == "N/A":
                return 0.0
            match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)', price_str)
            if match:
                cleaned_price = match.group(0).replace(',', '')
                return float(cleaned_price)
            return 0.0
        except Exception as e:
            logger.debug(f"clean_price failed for input {price_str}: {e}")
            return 0.0

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

