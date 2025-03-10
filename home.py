import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from pathlib import Path
import os
from time import sleep
import config
from session_manager import SessionManager
from amazon_products import make_amazon_products

class PriceScraperUI:
    def __init__(self):
        self.progress_file = Path(config.PROGRESS_TXT)
        self.running_file = Path(config.RUNNING)
        self.output_path = Path(config.SCRAPED_XLSX)
        self._cache = {}

    @staticmethod
    def _calculate_dataframe_height(df_length: int, row_height: int = 35, max_height: int = 500) -> int:
        return min(df_length * row_height + 38, max_height)

    def get_progress(self) -> int:
        """Get progress value from file with error handling."""
        try:
            return int(self.progress_file.read_text()) if self.progress_file.exists() else 0
        except Exception:
            return 0

    def progress_thread(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(self.get_progress).result()

    def scraping_progress(self, limit: int):
        if limit <= 0:
            return

        progress_text = "操作中です。少々お待ちください。"
        progress_value = 0
        my_bar = st.progress(progress_value, text=progress_text)

        while limit >= progress_value:
            progress_value = self.progress_thread()
            my_bar.progress(progress_value/limit, text=progress_text)
            sleep(1)
            
            # if progress_value and (progress_value % config.BATCH_SIZE == 0 or progress_value == limit):
            #     st.rerun()

        my_bar.empty()

    def setup_sidebar(self):
        with st.sidebar:
            st.subheader("メニュー")
            self._setup_scraping_controls()
            if st.button('リロード', use_container_width=True):
                st.rerun()

    def _setup_scraping_controls(self):
        st.subheader("スクレイピング制御")
        if self.running():
            st.sidebar.button("停 止", type="primary", use_container_width=True, on_click=self.stop_running)
        else:
            st.sidebar.button("開 始", type="secondary", use_container_width=True, on_click=self.start_running)

    def running(self) -> bool:
        return self.running_file.exists()

    def start_running(self):
        if not self.running():
            self.running_file.parent.mkdir(parents=True, exist_ok=True)
            self.running_file.write_text('1')

    def stop_running(self):
        if self.running_file.exists():
            self.running_file.unlink()
        if self.progress_file.exists():
            self.progress_file.unlink()

    def _load_product_data(self, uploaded_file) -> pd.DataFrame:
        yahoo_products_df = pd.DataFrame(columns=config.yahoo_columns)
        
        if uploaded_file:
            new_df = pd.read_excel(uploaded_file)

            if yahoo_products_df['商品URL'] != new_df['商品URL']:
                valid_columns = [col for col in new_df.columns if col in yahoo_products_df.columns]
                yahoo_products_df = pd.DataFrame(new_df[valid_columns], columns=valid_columns)
                
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
                yahoo_products_df.to_excel(self.output_path, index=False)
                st.success(f'データを保存しました {self.output_path}')
            
        elif self.output_path.exists():
            df = pd.read_excel(self.output_path)
            for col in df.columns:
                if col in yahoo_products_df.columns:
                    yahoo_products_df[col] = df[col]
                    
        return yahoo_products_df

    def _manage_product_list(self):
        uploaded_file = None if self.running() else st.file_uploader("商品URLリスト", type="xlsx")
        yahoo_products_df = self._load_product_data(uploaded_file)
        
        if uploaded_file:
            st.write("商品リストを読み込みました:", len(yahoo_products_df))

        yahoo_products_df.index += 1
        height = self._calculate_dataframe_height(len(yahoo_products_df))
        
        if self.running():
            self.scraping_progress(len(yahoo_products_df))

        st.dataframe(yahoo_products_df, use_container_width=True, height=height, key="scraped_product_list")

    def making_amazon_products(self):
        if st.button('Amazon商品を作成'):
            try:
                amazon_df = make_amazon_products()
                if not amazon_df.empty:
                    height = self._calculate_dataframe_height(len(amazon_df), max_height=600)
                    st.dataframe(amazon_df, height=height, use_container_width=True)
                else:
                    st.warning("商品が作成されませんでした。入力データを確認してください。")
            except Exception as e:
                st.error(f"Amazon商品の作成中にエラーが発生しました: {str(e)}")
        else:
            st.info("ボタンをクリックしてAmazon商品を作成してください")

    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["Yahoo!からデータ取得", "Amazon商品作成"])
        
        with tab1:
            self._manage_product_list()
        with tab2:
            self.making_amazon_products()

# if __name__ == "__main__":
app = PriceScraperUI()
app.run()
