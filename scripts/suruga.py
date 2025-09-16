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

class SurugaScraper:
    def __init__(self):
        self.driver = None
    
    def run(self, url, profile_name):
        """Helper method to scrape details from a specific product URL"""
        logger.info(f"Suruga")

        try:
            self.driver = WebDriverManager.get_driver(profile_name)
            self.driver.get(url)
            
            # Wait for main content to load
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".padL32"))
            )

            # Get page source and parse all required fields
                        
            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find('#item_title'),
                '商品ID':self._extract_id(url, "detail"),
                '販売価格': self.clean_price(self._safe_find('.price-buy')) or self.clean_price(self._safe_find('.mgnT12 span.text-red')),
                # '販売価格(即決)': self.clean_price(self._safe_find('.gv-u-fontSize12--s5WnvVgDScOXPWU7Mgqd.gv-u-colorContentOnSurfaceVariant--iGAjy0BdpomNMjXrpED_')),
            }


            # counts = self.driver.find_elements(By.CSS_SELECTOR, '.Count__detail')
            # data['入札件数'] = counts[0].text if counts else "N/A"
            # data['残り時間'] = counts[1].text if len(counts) > 1 else "N/A"

            # data['出品者ID'] = self._extract_id(self._safe_find('.bPwzBk a', "href"),'user')

            # Get all non-clone product images
            # Find all image elements inside .swiper-wrapper.total-img
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, '.total-img img')
            # Extract the 'src' attribute from each image element
            unique_image_urls = list(dict.fromkeys(a.get_attribute('zoom-photo-url') for a in image_elements if a.get_attribute('zoom-photo-url')))[:8]

            # Limit to 8 images
            unique_image_urls = unique_image_urls[:8]

            # Add image URLs to data dictionary
            for i, img_url in enumerate(unique_image_urls, 1):
                if img_url.lower().endswith('.webp'):
                    img_url = f"https://images.weserv.nl/?url={img_url}&output=jpg&q=90"
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
        """
        Extracts the numeric price from a string like '5,980円 (税込)' and returns it as a float.
        """
        if not isinstance(price_str, str):
            price_str = str(price_str)
        match = re.search(r'([\d,]+)', price_str)
        if match:
            cleaned_price = match.group(1).replace(',', '')
            try:
                return float(cleaned_price)
            except ValueError:
                return 0.0
        return 0.0

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

