import pandas as pd
import numpy as np
from datetime import datetime
import os
from time import sleep
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from webdriver_manager import WebDriverManager
from scripts.yahoo_auction import YahooAuctionScraper
from scripts.yahoo_auction1 import YahooAuctionScraper1
from scripts.yahoo_fleamarket import YahooFleamarketScraper
import config
from pathlib import Path

class DataHandler:
    @staticmethod
    def load_excel(file_path: str) -> Optional[pd.DataFrame]:
        """Load data from Excel file with error handling."""
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
        """Save DataFrame to Excel with error handling."""
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
        """Save progress value to file with error handling."""
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
        self.batch_size = config.BATCH_SIZE
        self.data_handler = DataHandler()
        

    def load_data(self) -> bool:
        """Load data and return success status."""
        self.df = self.data_handler.load_excel(config.SCRAPED_XLSX)
        self.df = self.df[~self.df['商品URL'].isna()]
        return self.df is not None
        
    def scraper_auction(self, url):
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(self.yahoo_auction_scraper.run, url)
                return future.result()
        except Exception as e:
            return {'error': str(e)}
    
    def scraper_auction1(self, url):
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(self.yahoo_auction_scraper1.run, url)
                return future.result()
        except Exception as e:
            return {'error': str(e)}
        
    def scraper_fleaMarket(self, url):
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(self.yahoo_fleamaket_scraper.run, url)
                return future.result()
        except Exception as e:
            return {'error': str(e)}
        

    def scrape_running(self) -> None:
        """Main scraping loop with improved error handling and optimization."""
        if not self.df is not None or self.df.empty:
            print("No data to process")
            return
        
        result = None

        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                if not self._check_running():
                    print("Scraping was stopped")
                    break

                print(f"Processing {index + 1}/{total_records}")

                p_url = row.get('商品URL')
                if not p_url:
                    print(f"Missing URL at index {index}")
                    continue
                else:
                    if 'auctions.yahoo.co.jp' in p_url:
                        if '/auctions.yahoo.co.jp/jp/auction/' in p_url:
                            p_url = p_url.replace('/auctions.yahoo.co.jp/jp/auction/', '/page.auctions.yahoo.co.jp/jp/auction/')
                        # if index == 0:
                        #     result = self.scraper_auction(p_url)
                        # else:
                        result = self.scraper_auction1(p_url)   
                    elif 'paypayfleamarket.yahoo.co.jp' in p_url:
                        result = self.scraper_fleaMarket(p_url)

                self._update_dataframe(index, result)

                self.data_handler.set_progress(index+1)
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
        """Update DataFrame with scraped results."""
        for key, value in results.items():
            # Ensure the column dtype is 'object' to allow any type assignment
            if self.df[key].dtype != 'object':
                self.df[key] = self.df[key].astype('object')

            # Assign the value (if 'N/A', convert to NaN or assign as string if needed)
            if value == 'N/A' or value == "nan":  # Example handling for 'N/A'
                self.df.at[index, key] = ''  # Assign string 'N/A'
            else:
                self.df.at[index, key] = value

    def _should_save_batch(self, index: int, total_records: int) -> bool:
        """Determine if current batch should be saved."""
        return (index + 1) % self.batch_size == 0 or (index + 1) == total_records

    @staticmethod
    def _check_running() -> bool:
        """Check if scraping should continue."""
        return os.path.exists(config.RUNNING)
    
    @staticmethod
    def stop_running():
        running_file = Path(config.RUNNING)
        progress_file = Path(config.PROGRESS_TXT)
        if running_file.exists():
            running_file.unlink()
        if progress_file.exists():
            progress_file.unlink()

    def save_results(self) -> None:
        """Save results to Excel file."""
        if self.df is not None:
            self.data_handler.save_excel(self.df, config.SCRAPED_XLSX)

    @staticmethod
    def cleanup() -> None:
        """Cleanup resources."""
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
