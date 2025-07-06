import requests
from bs4 import BeautifulSoup
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MandaRakeOrder:
    def __init__(self):
        self.session = requests.Session()

    def run(self, url):
        """Scrape details from a specific product URL using BeautifulSoup"""
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            data = {
                '商品URL': url,
                '商品画像': 'N/A',
                '商品名': self._safe_find(soup, 'div.subject>h1'),
                '商品ID': self._extract_id(url, "item?itemCode="),
            }

            price_element = self._safe_find(soup, '.shohin_price.__price + p')
            price_values = self.clean_price(price_element)
            price = max(price_values) if price_values else "N/A"
            data['販売価格'] = price

            try:
                data['商品状態'] = self._safe_find(soup, 'tr.condition > td')
            except Exception:
                data['商品状態'] = ""

            # Get all non-clone product images
            image_elements = soup.select('#elevate_zoom_gallery a.elevatezoom-gallery')
            image_urls = []

            if image_elements:
                image_urls = [el.get('data-image') for el in image_elements if el.get('data-image')]
            else:
                zoom_window = soup.select_one('.zoomWindow')
                if zoom_window and zoom_window.has_attr('style'):
                    style = zoom_window['style']
                    match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', style)
                    if match:
                        image_urls.append(match.group(1))

            # Limit to 8 images
            image_urls = image_urls[:8]
            image_urls = list(enumerate(image_urls, 1))

            for i, img_url in image_urls:
                data[f'画像URL{i}'] = img_url

            data['商品画像'] = data.get('画像URL1', 'N/A')

            return data

        except Exception as e:
            logger.error(f"URL scraping failed for {url}: {e}")
            return {"商品URL": url}

    def _safe_find(self, soup, selector):
        """Safely find element and get its text"""
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else "N/A"

    def _extract_id(self, href, pre):
        """Extracts the value following 'pre' in the URL."""
        try:
            idx = href.find(pre)
            if idx != -1:
                start = idx + len(pre)
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
        """Extracts and returns all integer numbers found in a price string."""
        if not isinstance(price_str, str):
            price_str = str(price_str)
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', price_str)
        return [int(num.replace(',', '')) for num in numbers]
