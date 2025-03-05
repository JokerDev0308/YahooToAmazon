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

class YahooAuctionScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo")

    
    def run(self, url):
        """Helper method to scrape details from a specific Yahoo Auction product URL"""
        try:
            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ProductInformation__item"))
            )

            # Get page source and parse all required fields
            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find('.ProductTitle__text'),
                '商品ID':self._extract_id(url, "auction"),
                '販売価格': self.clean_price(self._safe_find('.Price__value')),
                '販売価格(即決)': self.clean_price(self._safe_find('.Price__value--buyNow')),
                '商品状態': self._safe_find('.ProductTable__item:contains("商品の状態") + .ProductTable__data'),
            }

            counts = self.driver.find_elements(By.CSS_SELECTOR, '.Count__detail')
            data['入札件数'] = counts[0].text if counts else "N/A"
            data['残り時間'] = counts[1].text if len(counts) > 1 else "N/A"
            data['出品者ID'] = self._extract_id(self._safe_find('.Seller__name > a', 'href'), "seller")

            # Get all non-clone product images
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.ProductImage__image:not([class*="clone"]) .ProductImage__inner img')
            unique_image_urls = list(dict.fromkeys(img.get_attribute('src') for img in image_elements))[:8]

            # Add image URLs to data dictionary
            for i, img_url in enumerate(unique_image_urls, 1):
                data[f'画像URL{i}'] = img_url

            # # Get all image URLs from main product images
            # image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.ProductImage__inner img')
            # # Only take unique URLs and limit to first 8
            # image_urls = list(dict.fromkeys(img.get_attribute('src') for img in image_elements))[:8]
            
            # # Add image URLs to data dictionary
            # for i, img_url in enumerate(image_urls, 1):
            #     data[f'image{i}'] = img_url

            data['商品画像'] = data.get('画像URL1', 'N/A')

            return data

        except Exception as e:
            logger.error(f"URL scraping failed for {url}: {e}")
            return {field: "N/A" for field in [
                '商品URL', '商品画像', '商品名', '商品ID', '販売価格', '販売価格(即決)',
                '商品状態', '入札件数', '残り時間', '出品者ID',
                '画像URL1', '画像URL2', '画像URL3', '画像URL4',
                '画像URL5', '画像URL6', '画像URL7', '画像URL8'
            ]}

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
        if isinstance(price_str, (int, float)):  # If the input is numeric, convert it to a string
            price_str = str(price_str)
        
        match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?=税|円)', price_str)
        
        if match:
            cleaned_price = match.group(0)  
            cleaned_price = cleaned_price.replace(',', '')  
            
            try:
                return float(cleaned_price)  # Convert to float
            except ValueError:
                return 0.0 
        else:
            return 0.0  

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

