from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from config import TIMEOUT
from webdriver_manager import WebDriverManager
from time import sleep

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MandaRakeOrder:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("manda_rake_order")

    
    def run(self, url):
        """Helper method to scrape details from a specific product URL"""

        try:
            self.driver.get("https://mandarake.co.jp/")

            sleep(2)  # Wait for the homepage to load completely

            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".content"))
            )

            # Get page source and parse all required fields
                        
            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find('div.subject>h1'),
                '商品ID':self._extract_id(url, "item?itemCode="),
            }

            price_element = self.driver.find_element(By.CSS_SELECTOR, '.shohin_price.__price + p').text.strip()
            # Extract all price values from the string
            price_values = self.clean_price(price_element)
            # Use the maximum price found, or "N/A" if none
            price = max(price_values) if price_values else "N/A"


            data['販売価格'] = price

            # counts = self.driver.find_elements(By.CSS_SELECTOR, '.gv-u-fontSize16--_aSkEz8L_OSLLKFaubKB')
            # data['入札件数'] = counts[0].text if counts else "N/A"
            # data['残り時間'] = counts[1].text if len(counts) > 1 else "N/A"
            # data['商品状態']  = counts[2].text if len(counts) > 2 else "N/A"

            # data['入札件数'] = self.driver.find_element(By.CSS_SELECTOR, 'a.gv-u-fontSize16--_aSkEz8L_OSLLKFaubKB').text
            # data['残り時間'] = self.driver.find_element(By.CSS_SELECTOR, 'span.gv-u-fontSize12--s5WnvVgDScOXPWU7Mgqd.gv-u-colorTextGray--OzMlIYwM3n8ZKUl0z2ES').text
            try:
                data['商品状態'] = self.driver.find_element(By.CSS_SELECTOR, 'tr.condition > td').text.strip()
            except Exception:
                data['商品状態'] = ""
            
            # data['出品者ID'] = self._extract_id(self._safe_find('.konYbX > a', 'href'), "seller")

            # Get all non-clone product images
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '#elevate_zoom_gallery a.elevatezoom-gallery')
            image_urls = []

            if image_elements:
                image_urls = [el.get_attribute('data-image') for el in image_elements if el.get_attribute('data-image')]
            else:
                zoom_window = self.driver.find_elements(By.CSS_SELECTOR, '.zoomWindow')
                if zoom_window:
                    style = zoom_window[0].get_attribute('style')
                    match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', style)
                    if match:
                        image_urls.append(match.group(1))

            # Limit to 8 images
            image_urls = image_urls[:8]

            # Enumerate image_urls for later use
            image_urls = list(enumerate(image_urls, 1))

            # Add image URLs to data dictionary
            for i, img_url in image_urls:
                data[f'画像URL{i}'] = img_url

            data['商品画像'] = data.get('画像URL1', 'N/A')

            return data

        except Exception as e:
            logger.error(f"URL scraping failed for {url}: {e}")
            return {"商品URL": url} 

    def _safe_find(self, selector, attribute=None):
        """Helper method to safely find elements and get their text or attribute"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute) if attribute else element.text
        except:
            return "N/A"
        
    def _safe_find_arr(self, selector):
        """Helper method to safely find elements and get their text or attribute"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return elements
        except:
            return "N/A"
        
    def _extract_id(self, href, pre):
        """
        Extracts the value following 'pre' in the URL.
        For example, if pre="item?itemCode=", it extracts the itemCode value.
        """
        try:
            idx = href.find(pre)
            if idx != -1:
                start = idx + len(pre)
                # Extract until next '&' or end of string
                end = href.find('&', start)
                if end == -1:
                    return href[start:]
                else:
                    return href[start:end]
            return None
        except Exception as e:
            logger.error(f"Failed to extract value after '{pre}': {e}")
            return None
        

        
    def clean_price(self, price_str):
        """
        Extracts and returns all integer numbers found in a price string.
        Examples:
            "8,000円" -> [8000]
            "(税込 8,800円)" -> [8800]
            "8,000円 (税込 8,800円)" -> [8000, 8800]
        """
        if not isinstance(price_str, str):
            price_str = str(price_str)
        # Find all numbers with optional commas
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', price_str)
        # Remove commas and convert to int
        return [int(num.replace(',', '')) for num in numbers]

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

