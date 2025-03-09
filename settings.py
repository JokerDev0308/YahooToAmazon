import streamlit as st

import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
import config

# Custom CSS
LOGIN_STYLE = """
    <style>
        #login{
            text-align:center;
        }
        .stButton{
            text-align:center;
        }
        .stButton>button{
            min-width:7rem;
        }
    </style>
"""

def save_df2excel(df:pd.DataFrame, excel_name:str):
    output_path = Path(excel_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    st.success(f'データを {output_path} に保存しました')


col1, col2, col3, col4, col5, col6 = st.tabs(["定型パラメータ","除外セラー","キーワードとの紐づけ","販売価格テーブル","商品名置換テーブル", "パスワード設定"])

with col1:
    params_df = pd.DataFrame(columns=config.parms_columns)

    uploaded_file = st.file_uploader("定型パラメータをアップロード", type="xlsx")
    if uploaded_file is not None:
        new_df = pd.read_excel(uploaded_file)

        for col in new_df.columns:
            if col in params_df.columns:
                params_df[col] = new_df[col]

        save_df2excel(params_df,config.SETTING_PARAMS)
        
    elif Path(config.SETTING_PARAMS).exists():
        saved_params_df = pd.read_excel(config.SETTING_PARAMS)
        for col in saved_params_df:
            if col in params_df:
                params_df[col] = saved_params_df[col].astype(str)
    
    height = min(len(params_df) * 35 + 38, 600)
    edited_params_df = st.data_editor(
        params_df,
        height=height,
        num_rows="dynamic",
        use_container_width= True,
        column_config={
            "項目名": st.column_config.TextColumn(),
            "説明": st.column_config.TextColumn(),
            "設定値": st.column_config.TextColumn()
        }
    )

    if st.button('定型パラメータを保存'):
        save_df2excel(edited_params_df,config.SETTING_PARAMS)

with col2:
    seller_exclution_df = pd.DataFrame(columns=config.seller_exclution_columns)
    
    uploaded_file = st.file_uploader("除外セラーをアップロード", type="xlsx")
    if uploaded_file is not None:
        new_df = pd.read_excel(uploaded_file)

        for col in new_df.columns:
            if col in seller_exclution_df.columns:
                seller_exclution_df[col] = new_df[col]

        save_df2excel(seller_exclution_df,config.SETTING_SELLER_EXCLUTIONS)

    elif Path(config.SETTING_SELLER_EXCLUTIONS).exists():
        saved_seller_exclution_df = pd.read_excel(config.SETTING_SELLER_EXCLUTIONS)
        for col in saved_seller_exclution_df:
            if col in seller_exclution_df:
                seller_exclution_df[col] = saved_seller_exclution_df[col].astype(str)


    height = min(len(seller_exclution_df) * 35 + 38, 600)
    edited_seller_exclution_df = st.data_editor(
        seller_exclution_df,
        height=height,
        num_rows="dynamic",
        column_config={
            "除外セラーID": st.column_config.TextColumn(),
        }
    )

    if st.button('除外セラーを保存'):
        save_df2excel(edited_seller_exclution_df,config.SETTING_SELLER_EXCLUTIONS)

with col3:
    keywords_df = pd.DataFrame(columns=config.keywords_columns)
    
    uploaded_file = st.file_uploader("キーワード紐づけリストをアップロード", type="xlsx")
    if uploaded_file is not None:
        new_df = pd.read_excel(uploaded_file)

        for col in new_df.columns:
            if col in keywords_df.columns:
                keywords_df[col] = new_df[col]

        save_df2excel(keywords_df,config.SETTING_KEYWORDS)

    elif Path(config.SETTING_KEYWORDS).exists():
        saved_keywords_df = pd.read_excel(config.SETTING_KEYWORDS)
        for col in saved_keywords_df:
            if col in keywords_df:
                keywords_df[col] = saved_keywords_df[col].astype(str)
    
    height = min(len(keywords_df) * 35 + 38, 600)
    edited_keywords_df = st.data_editor(
        keywords_df,
        num_rows="dynamic",
        use_container_width=True,
        height=height,
        column_config={
            "キーワード": st.column_config.TextColumn(),
            "brand_name (ブランド名)": st.column_config.TextColumn(),
            "manufacturer (メーカ名)": st.column_config.TextColumn(),
            "recommended_browse_nodes (推奨ブラウズノード)": st.column_config.TextColumn(),
            "generic_keywords (検索キーワード)": st.column_config.TextColumn()
        }
    )

    if st.button('キーワードを保存'):
        save_df2excel(edited_keywords_df,config.SETTING_KEYWORDS)

with col4:
    sales_df = pd.DataFrame(columns=config.sales_columns)
    
    uploaded_file = st.file_uploader("販売価格テーブルをアップロード", type="xlsx")
    if uploaded_file is not None:
        new_df = pd.read_excel(uploaded_file)

        for col in new_df.columns:
            if col in sales_df.columns:
                sales_df[col] = new_df[col]

        save_df2excel(sales_df,config.SETTING_SALES_PRICE)

    elif Path(config.SETTING_SALES_PRICE).exists():
        saved_sales_df = pd.read_excel(config.SETTING_SALES_PRICE)
        for col in saved_sales_df:
            if col in sales_df:
                sales_df[col] = saved_sales_df[col]
    
    height = min(len(sales_df) * 35 + 38, 600)
    edited_sales_df = st.data_editor(
        sales_df,
        num_rows="dynamic",
        height=height,
        column_config={
            "仕入れ価格": st.column_config.NumberColumn(),
            "アマゾン販売価格": st.column_config.NumberColumn()
        }
    )

    if st.button('販売価格を保存'):
        save_df2excel(edited_sales_df, config.SETTING_SALES_PRICE)

with col5:
    replacements_df = pd.DataFrame(columns=config.product_name_replacements_columns)
    
    uploaded_file = st.file_uploader("商品名置換テーブルをアップロード", type="xlsx")
    if uploaded_file is not None:
        new_df = pd.read_excel(uploaded_file)

        for col in new_df.columns:
            if col in replacements_df.columns:
                replacements_df[col] = new_df[col]

        save_df2excel(replacements_df,config.SETTING_PRODUCT_NAME_REM)


    if Path(config.SETTING_PRODUCT_NAME_REM).exists():
        saved_replacements_df = pd.read_excel(config.SETTING_PRODUCT_NAME_REM)
        for col in saved_replacements_df:
            if col in replacements_df:
                # Replace NaN values with empty string before converting to str
                replacements_df[col] = saved_replacements_df[col].fillna('').astype(str)
    
    height = min(len(replacements_df) * 35 + 38, 600)
    edited_replacements_df = st.data_editor(
        replacements_df,
        num_rows="dynamic",
        height=height,
        column_config={
            "置換前": st.column_config.TextColumn(),
            "置換後": st.column_config.TextColumn()
        }
    )

    if st.button('置換設定を保存'):
        save_df2excel(edited_replacements_df, config.SETTING_PRODUCT_NAME_REM)

with col6:
    session_manager = SessionManager()
    col1, col2, col3 = st.columns(3)
    with col2:
        with st.container(border=True):
            st.markdown(LOGIN_STYLE, unsafe_allow_html=True)
            
            old_password = st.text_input("古いパスワード", type="password")
            new_password = st.text_input("新しいパスワード", type="password")
            confirm_password = st.text_input("新しいパスワードの確認", type="password")
            
            if st.button("保存"):
                res =  session_manager.reset_password('admin', old_password, new_password, confirm_password)

                if res['status'] == 'error':
                    st.error(res['message'])
                elif res['status'] == 'success':
                    st.success(res["message"])
                else:
                    st.error('不明なエラー')
                       

