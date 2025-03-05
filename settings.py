import streamlit as st

import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
import config

    
col1, col2, col3, col4, col5 = st.tabs(["Standard Parameters","Seller Exclusions","Linking With Keywords","Sales Price Table","Product Name Replacement"])

with col1:
    empty_param_df = pd.DataFrame({
                    'Item Name': [],
                    'Explaination': [],
                    'Setting Values': []
                })
    if Path(config.SETTING_PARAMS).exists():
        try:
            params_df = pd.read_excel(config.SETTING_PARAMS)
            if params_df.empty:
                params_df = empty_param_df.copy()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            params_df = empty_param_df.copy()
    else:
        params_df = empty_param_df.copy()

    # Ensure all columns are of string type to avoid type mismatch
    params_df['Item Name'] = params_df['Item Name'].astype(str)
    params_df['Explaination'] = params_df['Explaination'].astype(str)
    params_df['Setting Values'] = params_df['Setting Values'].astype(str)

    # Use the data editor with the appropriate column types
    edited = st.data_editor(
        params_df,
        num_rows="dynamic",
        column_config={
            "Item Name": st.column_config.TextColumn(),
            "Explaination": st.column_config.TextColumn(),
            "Setting Values": st.column_config.TextColumn()
        }
    )

    if st.button('Standard Parameters Save'):
        output_path = Path(config.SETTING_PARAMS)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edited.to_excel(output_path, index=False)
        st.success(f'Data saved to {output_path}')

with col2:
    empty_seller_exclution_df = pd.DataFrame({
                    'Excluded Seller ID': []
                })
    if Path(config.SETTING_SELLER_EXCLUTIONS).exists():
        try:
            params_df = pd.read_excel(config.SETTING_SELLER_EXCLUTIONS)
            if params_df.empty:
                params_df = empty_seller_exclution_df.copy()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            params_df = empty_seller_exclution_df.copy()
    else:
        params_df = empty_seller_exclution_df.copy()

    # Ensure all columns are of string type to avoid type mismatch
    params_df['Excluded Seller ID'] = params_df['Excluded Seller ID'].astype(str)

    # Use the data editor with the appropriate column types
    edited = st.data_editor(
        params_df,
        num_rows="dynamic",
        column_config={
            "Excluded Seller ID": st.column_config.TextColumn(),
        }
    )

    if st.button('Excluded Seller ID Save'):
        output_path = Path(config.SETTING_SELLER_EXCLUTIONS)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edited.to_excel(output_path, index=False)
        st.success(f'Data saved to {output_path}')

with col3:
    empty_keywords_df = pd.DataFrame({
                    'Keyword': [],
                    'Brand Name': [],
                    'Manufacturer': [],
                    'Recommended Browse Nodes': [],
                    'Generic Keywords': [],
                })
    if Path(config.SETTING_KEYWORDS).exists():
        try:
            params_df = pd.read_excel(config.SETTING_KEYWORDS)
            if params_df.empty:
                params_df = empty_keywords_df.copy()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            params_df = empty_keywords_df.copy()
    else:
        params_df = empty_keywords_df.copy()

    # Ensure all columns are of string type to avoid type mismatch
    params_df['Keyword'] = params_df['Keyword'].astype(str)
    params_df['Brand Name'] = params_df['Brand Name'].astype(str)
    params_df['Manufacturer'] = params_df['Manufacturer'].astype(str)
    params_df['Recommended Browse Nodes'] = params_df['Recommended Browse Nodes'].astype(str)
    params_df['Generic Keywords'] = params_df['Generic Keywords'].astype(str)

    # Use the data editor with the appropriate column types
    edited = st.data_editor(
        params_df,
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
        output_path = Path(config.SETTING_KEYWORDS)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edited.to_excel(output_path, index=False)
        st.success(f'Data saved to {output_path}')


with col4:
    empty_sales_df = pd.DataFrame({
                    'Purchase Price': [],
                    'Amazon Sales Price': [],
                })
    if Path(config.SETTING_SALES_PRICE).exists():
        try:
            params_df = pd.read_excel(config.SETTING_SALES_PRICE)
            if params_df.empty:
                params_df = empty_sales_df.copy()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            params_df = empty_sales_df.copy()
    else:
        params_df = empty_sales_df.copy()

    # Ensure all columns are of string type to avoid type mismatch
    params_df['Purchase Price'] = params_df['Purchase Price'].astype(str)
    params_df['Amazon Sales Price'] = params_df['Amazon Sales Price'].astype(str)

    # Use the data editor with the appropriate column types
    edited = st.data_editor(
        params_df,
        num_rows="dynamic",
        column_config={
            "Purchase Price": st.column_config.TextColumn(),
            "Amazon Sales Price": st.column_config.TextColumn(),
        }
    )

    if st.button('Sales Price Save'):
        output_path = Path(config.SETTING_SALES_PRICE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edited.to_excel(output_path, index=False)
        st.success(f'Data saved to {output_path}')



with col5:
    empty_replacements_df = pd.DataFrame({
                    'Before Replacement': [],
                    'After Replacement': [],
                })
    if Path(config.SETTING_PRODUCT_NAME_REM).exists():
        try:
            params_df = pd.read_excel(config.SETTING_PRODUCT_NAME_REM)
            if params_df.empty:
                params_df = empty_replacements_df.copy()
        except Exception as e:
            st.error(f"Error reading file: {e}")
            params_df = empty_replacements_df.copy()
    else:
        params_df = empty_replacements_df.copy()

    # Ensure all columns are of string type to avoid type mismatch
    params_df['Before Replacement'] = params_df['Before Replacement'].astype(str)
    params_df['After Replacement'] = params_df['After Replacement'].astype(str)

    # Use the data editor with the appropriate column types
    edited = st.data_editor(
        params_df,
        num_rows="dynamic",
        column_config={
            "Before Replacement": st.column_config.TextColumn(),
            "After Replacement": st.column_config.TextColumn(),
        }
    )

    if st.button('Replacement Save'):
        output_path = Path(config.SETTING_PRODUCT_NAME_REM)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        edited.to_excel(output_path, index=False)
        st.success(f'Data saved to {output_path}')


