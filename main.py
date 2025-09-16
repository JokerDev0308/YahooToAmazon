import pandas as pd
import numpy as np
from datetime import datetime
import os
from time import sleep
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import uuid
from pathlib import Path

from webdriver_manager import WebDriverManager
from scripts.yahoo_auction import YahooAuctionScraper
from scripts.yahoo_auction1 import YahooAuctionScraper1
from scripts.yahoo_fleamarket import YahooFleamarketScraper
from scripts.suruga import SurugaScraper
from scripts.manda_rake_order import MandaRakeOrder
import config


class DataHandler:
    @staticmethod
    def load_excel(file_path: str) -> Optional[pd.DataFrame]:
        try:
            return pd.read_excel(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return None

    @staticmethod
    def save_excel(df: pd.DataFrame, file_path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_excel(file_path, index=False)
            print(f"Successfully saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False

    @staticmethod
    def set_progress(progress: int) -> None:
        try:
            progress_file = Path(config.PROGRESS_TXT)
            progress_file.parent.mkdir(exist_ok=True)
            progress_file.write_text(str(progress))
        except Exception as e:
            print(f"Error saving progress: {e}")


class Scraper:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.yahoo_auction_scraper = YahooAuctionScraper()
        self.yahoo_auction_scraper1 = YahooAuctionScraper1()
        self.yahoo_fleamaket_scraper = YahooFleamarketScraper()
        self.suruga_scraper = SurugaScraper()
        self.manda_rake_order = MandaRakeOrder()
        self.batch_size = config.BATCH_SIZE
        self.data_handler = DataHandler()

    def load_data(self) -> bool:
        self.df = self.data_handler.load_excel(config.SCRAPED_XLSX)
        if self.df is None:
            return False
        self.df = self.df[~self.df['商品URL'].isna()]
        return not self.df.empty

    def run_with_new_profile(self, scraper_func, url):
        profile_name = f"profile_{uuid.uuid4().hex[:8]}"
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(scraper_func, url, profile_name)
            return future.result()

    def scraper_auction(self, url, profile_name):
        try:
            return self.yahoo_auction_scraper.run(url, profile_name)
        except Exception as e:
            return {'error': str(e)}

    def scraper_auction1(self, url, profile_name):
        try:
            return self.yahoo_auction_scraper1.run(url, profile_name)
        except Exception as e:
            return {'error': str(e)}

    def scraper_fleaMarket(self, url, profile_name):
        try:
            return self.yahoo_fleamaket_scraper.run(url, profile_name)
        except Exception as e:
            return {'error': str(e)}

    def scraper_suruga(self, url, profile_name):
        try:
            return self.suruga_scraper.run(url, profile_name)
        except Exception as e:
            return {'error': str(e)}

    def scraper_manda_rake_order(self, url, profile_name):
        try:
            return self.manda_rake_order.run(url, profile_name)
        except Exception as e:
            return {'error': str(e)}

    def scrape_running(self) -> None:
        if self.df is None or self.df.empty:
            print("No data to process")
            return

        result = None
        total_records = len(self.df)

        try:
            for index, row in self.df.iterrows():
                if not self._check_running():
                    print("Scraping stopped manually.")
                    break

                print(f"Processing {index + 1}/{total_records}")

                p_url = row.get('商品URL')
                if not p_url:
                    print(f"Missing URL at index {index}")
                    continue

                if 'auctions.yahoo.co.jp' in p_url:
                    if '/auctions.yahoo.co.jp/jp/auction/' in p_url:
                        p_url = p_url.replace('/auctions.yahoo.co.jp/jp/auction/', '/page.auctions.yahoo.co.jp/jp/auction/')
                    result = self.run_with_new_profile(self.scraper_auction1, p_url)

                elif 'paypayfleamarket.yahoo.co.jp' in p_url:
                    result = self.run_with_new_profile(self.scraper_fleaMarket, p_url)

                elif 'suruga-ya.jp' in p_url:
                    result = self.run_with_new_profile(self.scraper_suruga, p_url)

                elif 'order.mandarake.co.jp' in p_url:
                    result = self.run_with_new_profile(self.scraper_manda_rake_order, p_url)

                self._update_dataframe(index, result)
                self.data_handler.set_progress(index + 1)

                if self._should_save_batch(index, total_records):
                    self.save_results()

                sleep(1)

            if self._check_running():
                self.stop_running()

        except Exception as e:
            print(f"Scraping error: {str(e)}")
        finally:
            self.cleanup()

    def _update_dataframe(self, index: int, results: Dict[str, Any]) -> None:
        for key, value in results.items():
            if key not in self.df.columns:
                self.df[key] = np.nan
            self.df.at[index, key] = '' if value in ['N/A', 'nan'] else value

    def _should_save_batch(self, index: int, total_records: int) -> bool:
        return (index + 1) % self.batch_size == 0 or (index + 1) == total_records

    @staticmethod
    def _check_running() -> bool:
        return os.path.exists(config.RUNNING)

    @staticmethod
    def stop_running():
        for path in [config.RUNNING, config.PROGRESS_TXT]:
            try:
                file = Path(path)
                if file.exists():
                    file.unlink()
            except Exception:
                pass

    def save_results(self) -> None:
        if self.df is not None:
            self.data_handler.save_excel(self.df, config.SCRAPED_XLSX)

    @staticmethod
    def cleanup() -> None:
        WebDriverManager.close_all()


def main():
    scraper = None
    try:
        while True:
            scraper = Scraper()
            if scraper.load_data():
                scraper.scrape_running()
            sleep(10)
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
