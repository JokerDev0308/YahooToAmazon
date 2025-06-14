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

class YahooAuctionScraper1:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo_auction1")

    
    def run(self, url):
        """Helper method to scrape details from a specific Yahoo Auction product URL"""
        logger.info(f"Yahoo Auction-1")

        try:
            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".bgnEiA"))
            )

            # Get page source and parse all required fields
                        
            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find('.eTzLQx'),
                '商品ID':self._extract_id(url, "auction"),
                '販売価格': self.clean_price(self._safe_find('.kxUAXU')),
                '販売価格(即決)': self.clean_price(self._safe_find('.eGrksu')),
            }

            # counts = self.driver.find_elements(By.CSS_SELECTOR, '.gv-u-fontSize16--_aSkEz8L_OSLLKFaubKB')
            # data['入札件数'] = counts[0].text if counts else "N/A"
            # data['残り時間'] = counts[1].text if len(counts) > 1 else "N/A"
            # data['商品状態']  = counts[2].text if len(counts) > 2 else "N/A"

            data['入札件数'] = self.driver.find_element(By.CSS_SELECTOR, 'a.gv-u-fontSize16--_aSkEz8L_OSLLKFaubKB').text
            data['残り時間'] = self.driver.find_element(By.CSS_SELECTOR, '.ntWoh span.gv-u-fontSize12--s5WnvVgDScOXPWU7Mgqd.gv-u-colorTextGray--OzMlIYwM3n8ZKUl0z2ES').text
            data['商品状態']  = self.driver.find_elements(By.CSS_SELECTOR, '.czQQLT')[2].text
            
            data['出品者ID'] = self._extract_id(self._safe_find('.konYbX > a', 'href'), "seller")

            # Get all non-clone product images
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.slick-track .slick-slide:not(.slick-cloned) img')
            
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

