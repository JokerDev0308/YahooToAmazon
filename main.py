import pandas as pd
import numpy as np
from datetime import datetime
import os
from time import sleep
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from webdriver_manager import WebDriverManager
from scripts.yahoo_scraper import YahooAuctionScraper
import config

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

class Scraper:
    def __init__(self, batch_size: int = 10):
        self.df: Optional[pd.DataFrame] = None
        self.yahoo_scraper = YahooAuctionScraper()
        self.batch_size = batch_size
        self.data_handler = DataHandler()

    def load_data(self) -> bool:
        """Load data and return success status."""
        self.df = self.data_handler.load_excel(config.SCRAPED_XLSX)
        return self.df is not None

    def process_product(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Process a single product with error handling."""
        try:
            url = row.get('商品URL')
            if not url:
                return {'error': 'Missing URL'}

            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(self.yahoo_scraper.run, url)
                return future.result()
        except Exception as e:
            return {'error': str(e)}

    def scrape_running(self) -> None:
        """Main scraping loop with improved error handling and optimization."""
        if not self.df is not None or self.df.empty:
            print("No data to process")
            return

        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                if not self._check_running():
                    print("Scraping stopped by user")
                    break

                print(f"Processing {index + 1}/{total_records}: JAN {row.get('JAN', 'N/A')}")
                
                results = self.process_product(index, row)
                self._update_dataframe(index, results)

                if self._should_save_batch(index, total_records):
                    self.save_results()
                    sleep(3)

                sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Scraping error: {str(e)}")
        finally:
            self.cleanup()

    def _update_dataframe(self, index: int, results: Dict[str, Any]) -> None:
        """Update DataFrame with scraped results."""
        if results and isinstance(results, dict):
            for key, value in results.items():
                self.df.at[index, key] = value

    def _should_save_batch(self, index: int, total_records: int) -> bool:
        """Determine if current batch should be saved."""
        return (index + 1) % self.batch_size == 0 or (index + 1) == total_records

    @staticmethod
    def _check_running() -> bool:
        """Check if scraping should continue."""
        return os.path.exists(config.RUNNING)

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
