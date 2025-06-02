import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
from amazon_products import make_amazon_products
import config
from datetime import datetime
from time import sleep

# Main application class
class PriceScraperUI:
    def __init__(self):
        self.initialized = False

    def setup_sidebar(self):
        with st.sidebar:
            self._setup_scraping_controls()
            if st.button('リロード', use_container_width=True):
                st.rerun()

    def scraping_progress(self, limit):
        if limit > 0:
            progress_text = "操作中です。少々お待ちください。"
            progress_value = 0
            my_bar = st.progress(progress_value, text=progress_text)

            while limit >= progress_value:
                progress_value = self.progress_thread()
                
                my_bar.progress(progress_value/limit, text=progress_text + f" {progress_value}/{limit}")
                sleep(1)
                if progress_value !=0 and progress_value == limit:
                    st.rerun()
            my_bar.empty()

    def progress_thread(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            return executor.submit(self.get_progress).result()

    def get_progress(self) -> int:
        """Get progress value from file with error handling."""
        try:
            progress_file = Path(config.PROGRESS_TXT)
            if progress_file.exists():
                return int(progress_file.read_text())
            return 0
        except Exception:
            return 0

    def _manage_product_list(self):
        yahoo_products_df = pd.DataFrame(columns=config.yahoo_columns)

        if not self.running():
            uploaded_file = st.file_uploader("商品URLリスト", type="xlsx")
            if uploaded_file is not None:
                new_df = pd.read_excel(uploaded_file, dtype={col: str for col in yahoo_products_df.columns if col == "商品ID"})

                for col in new_df.columns:
                    if col in yahoo_products_df.columns:
                        yahoo_products_df[col] = new_df[col]

                st.write("商品リストを読み込みました:", len(new_df))
                output_path = Path(config.SCRAPED_XLSX)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                yahoo_products_df.to_excel(output_path, index=False)
                st.success(f'データを保存しました {output_path}')

        if Path(config.SCRAPED_XLSX).exists():
            df = pd.read_excel(config.SCRAPED_XLSX, dtype={col: str for col in yahoo_products_df.columns if col == "商品ID"})
            for col in df.columns:
                if col in yahoo_products_df.columns:
                    yahoo_products_df[col] = df[col]

        yahoo_products_df.index = yahoo_products_df.index + 1
        height = min(len(yahoo_products_df) * 35 + 38, 500)

        # Ensure 商品ID is always string and remove .0 if present
        yahoo_products_df['商品ID'] = yahoo_products_df['商品ID'].fillna("").astype(str).str.replace(r'\.0$', '', regex=True)

        if self.running():
            self.scraping_progress(len(yahoo_products_df))

        st.dataframe(
            yahoo_products_df,
            use_container_width=True,
            height=height,
            key="scraped_product_list",
            column_config={
                "商品画像": st.column_config.ImageColumn(),
                "商品ID": st.column_config.TextColumn(),
                "画像URL1": st.column_config.ImageColumn(),
                "画像URL2": st.column_config.ImageColumn(),
                "画像URL3": st.column_config.ImageColumn(),
                "画像URL4": st.column_config.ImageColumn(),
                "画像URL5": st.column_config.ImageColumn(),
                "画像URL6": st.column_config.ImageColumn(),
                "画像URL7": st.column_config.ImageColumn(),
                "画像URL8": st.column_config.ImageColumn(),
            }
        )

        if not self.running() and Path(config.SCRAPED_XLSX).exists():
            with open(config.SCRAPED_XLSX, 'rb') as file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.download_button(
                    label="商品リストをダウンロード",
                    data=file,
                    file_name=f"製品リスト({timestamp}).xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    def _setup_scraping_controls(self):
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
        running_file = Path(config.RUNNING)
        progress_file = Path(config.PROGRESS_TXT)
        if running_file.exists():
            running_file.unlink()
        
        if progress_file.exists():
            progress_file.unlink()

    def making_amazon_products(self):
        if st.button('Amazon製品の作成'):
            try:
                amazon_df: pd.DataFrame = make_amazon_products()
                if amazon_df is not None and not amazon_df.empty:
                    self._display_and_download_products(amazon_df)
                else:
                    st.warning("商品が作成されませんでした。入力データを確認してください。")
            except Exception as e:
                st.error(f"Amazon商品のプレビュー中にエラーが発生しました: {str(e)}")

    def _display_and_download_products(self, amazon_df: pd.DataFrame):
        # Display dataframe
        height = min(len(amazon_df) * 35 + 38, 500)
        st.dataframe(amazon_df, height=height,
            use_container_width=True,
            column_config={
                "main_image_url": st.column_config.ImageColumn(),
                "other_image_url1": st.column_config.ImageColumn(),
                "other_image_url2": st.column_config.ImageColumn(),
                "other_image_url3": st.column_config.ImageColumn(),
                "other_image_url4": st.column_config.ImageColumn(),
                "other_image_url5": st.column_config.ImageColumn(),
                "other_image_url6": st.column_config.ImageColumn(),
                "other_image_url7": st.column_config.ImageColumn(),
                "other_image_url8": st.column_config.ImageColumn(),
            })
        
        # Save and process file
        output_path = Path(config.AMAZON_PRODUCT_OUTPUT).with_suffix('.xlsx')
        amazon_df.to_excel(output_path, index=False)
        
        try:
            final_path = self._process_with_template(output_path)
            self._create_download_button(final_path)
        except FileNotFoundError:
            st.error("テンプレートファイルが見つかりません。")
        except Exception as e:
            st.error(f"ファイル処理中にエラーが発生しました: {str(e)}")

    def _process_with_template(self, output_path: Path) -> Path:
        template_path = Path(config.AMAZON_PRODUCT_TEMPLATE).with_suffix('.xlsx')
        if not template_path.exists():
            raise FileNotFoundError("template.xlsx not found")
        
        template_df = pd.read_excel(template_path, nrows=2, header=None)
        data_df = pd.read_excel(output_path, header=None)
        
        if data_df.iloc[0].tolist() != template_df.iloc[1].tolist():
            data_df = pd.concat([template_df, data_df], ignore_index=True)
        
        data_df.to_excel(output_path, index=False, header=False)
        return output_path

    def _create_download_button(self, file_path: Path):
        with open(file_path, 'rb') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.download_button(
                label="Amazon商品リストをダウンロード",
                data=file,
                file_name=f"Amazon商品リストを({timestamp}).xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["Yahoo!からデータ取得", "Amazon商品作成"])
        
        with tab1:
            self._manage_product_list()
        with tab2:
            self.making_amazon_products()
            
       

# Initialize and run the app
app = PriceScraperUI()
app.run()
