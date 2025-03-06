import streamlit as st

import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
import config

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


    def _handle_file_upload(self):
        uploaded_file = st.file_uploader("Product Url List", type="xlsx")
        if uploaded_file is not None:
            new_df = pd.read_excel(uploaded_file)
            st.write("The product list has been read:", len(new_df))
            new_df.index = new_df.index + 1
            height = min(len(new_df) * 35 + 38, 800)
            st.dataframe(
                new_df, 
                use_container_width=True, 
                height=height, 
                key="product_list_update",
                # column_config={
                #         "商品画像": st.column_config.ImageColumn(),
                #         "画像URL1": st.column_config.ImageColumn(),
                #         "画像URL2": st.column_config.ImageColumn(),
                #         "画像URL3": st.column_config.ImageColumn(),
                #         "画像URL4": st.column_config.ImageColumn(),
                #         "画像URL5": st.column_config.ImageColumn(),
                #         "画像URL6": st.column_config.ImageColumn(),
                #         "画像URL7": st.column_config.ImageColumn(),
                #         "画像URL8": st.column_config.ImageColumn(),
                #         }
                )

            new_df.to_excel(config.SCRAPED_XLSX, index=False)
            st.success(f"Product list was saved {config.SCRAPED_XLSX}")
        else:
            try:
                df = pd.read_excel(config.SCRAPED_XLSX)
                df.index = df.index + 1
                height = min(len(df) * 35 + 38, 800)
                st.dataframe(
                    df, 
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
            except FileNotFoundError:
                st.warning("Product list data is not yet available.")

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

    def display_main_content(self):
        try:
            df = pd.read_excel(config.SCRAPED_XLSX)
            
            df = df.rename(columns=config.column_name_mapping)[config.ordered_columns]
            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df,
                        use_container_width=True,
                        height=height, 
                        key="result",
                        
                        )
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    

    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["Fetch Data From Yahoo! Auction", "Makeing Amazon Product"])
        
        with tab1:
            self._handle_file_upload()
        with tab2:
            self.display_main_content()
            
       

# Initialize and run the app
app = PriceScraperUI()
app.run()
