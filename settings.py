import streamlit as st

import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
import config

def save_df2excel(df:pd.DataFrame, excel_name:str):
    output_path = Path(excel_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    st.success(f'Data saved to {output_path}')


col1, col2, col3, col4, col5 = st.tabs(["Standard Parameters","Seller Exclusions","Linking With Keywords","Sales Price Table","Product Name Replacement"])

with col1:
    params_df = pd.DataFrame(columns=config.parms_columns)
    
    if Path(config.SETTING_PARAMS).exists():
        saved_params_df = pd.read_excel(config.SETTING_PARAMS)
        for col in saved_params_df:
            if col in params_df:
                params_df[col] = saved_params_df[col].astype(str)
    
    # Use the data editor with the appropriate column types
    edited_params_df = st.data_editor(
        params_df,
        num_rows="dynamic",
        column_config={
            "Item Name": st.column_config.TextColumn(),
            "Explaination": st.column_config.TextColumn(),
            "Setting Values": st.column_config.TextColumn()
        }
    )

    if st.button('Standard Parameters Save'):
        save_df2excel(edited_params_df,config.SETTING_PARAMS)

with col2:
    seller_exclution_df = pd.DataFrame(columns=config.seller_exclution_columns)
    
    if Path(config.SETTING_SELLER_EXCLUTIONS).exists():
        saved_seller_exclution_df = pd.read_excel(config.SETTING_SELLER_EXCLUTIONS)
        for col in saved_seller_exclution_df:
            if col in seller_exclution_df:
                seller_exclution_df[col] = saved_seller_exclution_df[col].astype(str)


    # Use the data editor with the appropriate column types
    edited_seller_exclution_df = st.data_editor(
        seller_exclution_df,
        num_rows="dynamic",
        column_config={
            "Excluded Seller ID": st.column_config.TextColumn(),
        }
    )

    if st.button('Excluded Seller ID Save'):
        save_df2excel(edited_seller_exclution_df,config.SETTING_SELLER_EXCLUTIONS)

with col3:
    keywords_df = pd.DataFrame(columns=config.keywords_columns)
    
    if Path(config.SETTING_KEYWORDS).exists():
        saved_keywords_df = pd.read_excel(config.SETTING_KEYWORDS)
        for col in saved_keywords_df:
            if col in keywords_df:
                keywords_df[col] = saved_keywords_df[col].astype(str)
    
    # Use the data editor with the appropriate column types
    edited_keywords_df = st.data_editor(
        keywords_df,
        num_rows="dynamic",
        column_config={
            "Keyword": st.column_config.TextColumn(),
            "Brand Name": st.column_config.TextColumn(),
            "Manufacturer": st.column_config.TextColumn(),
            "Recommended Browse Nodes": st.column_config.TextColumn(),
            "Generic Keywords": st.column_config.TextColumn()
        }
    )

    if st.button('Keywords Save'):
        save_df2excel(edited_keywords_df,config.SETTING_KEYWORDS)

with col4:
    sales_df = pd.DataFrame(columns=config.sales_columns)
    
    if Path(config.SETTING_SALES_PRICE).exists():
        saved_sales_df = pd.read_excel(config.SETTING_SALES_PRICE)
        for col in saved_sales_df:
            if col in sales_df:
                sales_df[col] = saved_sales_df[col].astype(str)
    
    # Use the data editor with the appropriate column types
    edited_sales_df = st.data_editor(
        sales_df,
        num_rows="dynamic",
        column_config={
            "Purchase Price": st.column_config.TextColumn(),
            "Amazon Sales Price": st.column_config.TextColumn()
        }
    )

    if st.button('Sales Price Save'):
        save_df2excel(edited_sales_df, config.SETTING_SALES_PRICE)

with col5:
    replacements_df = pd.DataFrame(columns=config.product_name_replacements_columns)
    
    if Path(config.SETTING_PRODUCT_NAME_REM).exists():
        saved_replacements_df = pd.read_excel(config.SETTING_PRODUCT_NAME_REM)
        for col in saved_replacements_df:
            if col in replacements_df:
                replacements_df[col] = saved_replacements_df[col].astype(str)
    
    # Use the data editor with the appropriate column types
    edited_replacements_df = st.data_editor(
        replacements_df,
        num_rows="dynamic",
        column_config={
            "Before Replacement": st.column_config.TextColumn(),
            "After Replacement": st.column_config.TextColumn()
        }
    )

    if st.button('Replacement Save'):
        save_df2excel(edited_replacements_df, config.SETTING_PRODUCT_NAME_REM)


