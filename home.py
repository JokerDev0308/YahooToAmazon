import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
from amazon_products import make_amazon_products
import config
from time import sleep

# Main application class
class PriceScraperUI:
    def __init__(self):
        self.initialized = False

    def setup_sidebar(self):
        with st.sidebar:
            st.subheader("メニュー")
            self._setup_scraping_controls()

            if st.button('リロード', use_container_width=True):
                st.rerun()

    def scraping_progress(self, limit):
        progress_text = "Operation in progress. Please wait."
        progress_value = 0
        my_bar = st.progress(progress_value, text=progress_text)

        while limit >= progress_value:
            progress_value = self.progress_thread()
            my_bar.progress(progress_value/limit, text=progress_text)
            sleep(1)

        my_bar.empty()

    def progress_thread(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            return executor.submit(self.get_progress).result()

    def get_progress(self) -> float:
        """Get progress value from file with error handling."""
        try:
            progress_file = Path("tmp/progress.txt")
            if progress_file.exists():
                return float(progress_file.read_text())
            return 0.0
        except Exception:
            return 0.0

    def _manage_product_list(self):
        yahoo_products_df = pd.DataFrame(columns=config.yahoo_columns)

        if not self.running():
            uploaded_file = st.file_uploader("商品URLリスト", type="xlsx")
            if uploaded_file is not None:
                new_df = pd.read_excel(uploaded_file)

                for col in new_df.columns:
                    if col in yahoo_products_df.columns:
                        yahoo_products_df[col] = new_df[col]

                st.write("T商品リストを読み込みました:", len(new_df))
                output_path = Path(config.SCRAPED_XLSX)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                yahoo_products_df.to_excel(output_path, index=False)
                st.success(f'データを保存しました {output_path}')
        
            
            
        if Path(config.SCRAPED_XLSX).exists():
            df = pd.read_excel(config.SCRAPED_XLSX)
            for col in df.columns:
                if col in yahoo_products_df.columns:
                    yahoo_products_df[col] = df[col]

        if self.running():
            self.scraping_progress(len(yahoo_products_df))

        yahoo_products_df.index = yahoo_products_df.index + 1
        height = min(len(yahoo_products_df) * 35 + 38, 700)

        st.dataframe(
            yahoo_products_df, 
            use_container_width=True, 
            height=height, 
            key="scraped_product_list",
            # column_config={
            #     "商品画像": st.column_config.ImageColumn(),
            #     "画像URL1": st.column_config.ImageColumn(),
            #     "画像URL2": st.column_config.ImageColumn(),
            #     "画像URL3": st.column_config.ImageColumn(),
            #     "画像URL4": st.column_config.ImageColumn(),
            #     "画像URL5": st.column_config.ImageColumn(),
            #     "画像URL6": st.column_config.ImageColumn(),
            #     "画像URL7": st.column_config.ImageColumn(),
            #     "画像URL8": st.column_config.ImageColumn(),
            #     }
            )
           

    def _setup_scraping_controls(self):
        st.subheader("スクレイピング制御")
        if self.running():
            st.sidebar.button("停 止", type="primary", use_container_width=True, on_click=self.stop_running)
        else:
            st.sidebar.button("開 始", type="secondary", use_container_width=True, on_click=self.start_running)

    def running(self):
        return os.path.exists(config.RUNNING)

    def start_running(self):
        if not self.running():
            os.makedirs(os.path.dirname(config.RUNNING), exist_ok=True)
        with open(config.RUNNING, 'w') as file:
            file.write('1')

    def stop_running(self):
        file_path = Path(config.RUNNING)
        file_path.unlink()

    def making_amazon_products(self):
        if st.button('Amazon商品を作成'):
            try:
                amazon_df: pd.DataFrame = make_amazon_products()
                if not amazon_df.empty:
                    height = min(len(amazon_df) * 35 + 38, 800)
                    st.dataframe(amazon_df, height=height, use_container_width=True)
                else:
                    st.warning("商品が作成されませんでした。入力データを確認してください。")
            except Exception as e:
                st.error(f"Amazon商品の作成中にエラーが発生しました: {str(e)}")
        else:
            st.info("ボタンをクリックしてAmazon商品を作成してください")

    

    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["Yahoo!オークションからデータ取得", "Amazon商品作成"])
        
        with tab1:
            self._manage_product_list()
        with tab2:
            self.making_amazon_products()
            
       

# Initialize and run the app
app = PriceScraperUI()
app.run()
