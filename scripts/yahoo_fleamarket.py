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
        self.driver = WebDriverManager.get_driver("yahoo_fleamarket")

    
    def run(self, url):
        """Helper method to scrape details from a specific Yahoo Fleamarket product URL"""
        try:
            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".eOyszT")) 
            )

            # Get page source and parse all required fields
            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find('.gHRTcR'),
                '商品ID':self._extract_id(url, "item"),
                '販売価格': self.clean_price(self._safe_find('.lfSzHD')),
                '商品状態': self._safe_find('.gIvWhM'),
            }

            # counts = self.driver.find_elements(By.CSS_SELECTOR, '.Count__detail')
            # data['入札件数'] = counts[0].text if counts else "N/A"
            # data['残り時間'] = counts[1].text if len(counts) > 1 else "N/A"

            data['出品者ID'] = self._extract_id(self._safe_find('.bPwzBk a', "href"),'user')

            # Get all non-clone product images
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.bvEyKL')
            unique_image_urls = list(dict.fromkeys(img.get_attribute('src') for img in image_elements))[:8]

            # Add image URLs to data dictionary
            for i, img_url in enumerate(unique_image_urls, 1):
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
        
    def _extract_id(self, href, pre):
        """Helper method to extract seller ID from the href of an anchor tag"""
        try:
            # Use a regular expression to extract the seller ID from the URL
            match = re.search(rf'{pre}/([a-zA-Z0-9_-]+)', href)
            if match:
                return match.group(1)  # Return the seller ID part from the URL
        except Exception as e:
            logger.error(f"Failed to extract seller ID: {e}")
            return None
        
    def clean_price(self, price_str):
        # Ensure the input is a string
        # if isinstance(price_str, (int, float)):  # If the input is numeric, convert it to a string
        #     price_str = str(price_str)
        
        # match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?=税|円)', price_str)
        
        # if match:
        #     cleaned_price = match.group(0)  
        #     cleaned_price = cleaned_price.replace(',', '')  
            
        #     try:
        #         return float(cleaned_price)  
        #     except ValueError:
        #         return 0.0 
        # else:
        #     return 0.0  
        try:
            return float(price_str.replace(',', ''))  
        except ValueError:
            return 0.0

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

