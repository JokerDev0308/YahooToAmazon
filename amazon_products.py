import pandas as pd
from pathlib import Path
import config
import jaconv

def make_amazon_products()->pd.DataFrame:
    yahoo_products = pd.read_excel(config.SCRAPED_XLSX)

    params = pd.read_excel(config.SETTING_PARAMS)
    kewords = pd.read_excel(config.SETTING_KEYWORDS)
    products_name_replacements = pd.read_excel(config.SETTING_PRODUCT_NAME_REM)
    exclude_sellers = pd.read_excel(config.SETTING_SELLER_EXCLUTIONS)
    setup_sales_price = pd.read_excel(config.SETTING_SALES_PRICE)

    yahoo_products = yahoo_products[~yahoo_products['商品名'].isna()]    
    yahoo_products = yahoo_products[~yahoo_products['出品者ID'].isin(exclude_sellers['除外セラーID'])]
    yahoo_products = yahoo_products.reset_index(drop=True)
    yahoo_products.index = yahoo_products.index + 1

    amazon_products = pd.DataFrame(columns=config.amazon_columns)
    amazon_products['item_sku'] = yahoo_products['商品ID']
    amazon_products['item_name'] = yahoo_products['商品名']

    # for _, old_word, new_word in products_name_replacements[['置換前', '置換後']].itertuples():
    #     # If the new word is not NaN, replace the old word with the new word
    #     if pd.notna(new_word):
    #         # For English words, use case-insensitive replacement
    #         # For Japanese, convert both hiragana and katakana to the same form
    #         old_word_str = str(old_word)
    #         new_word_str = str(new_word)
    #         if old_word_str.isascii():
    #             amazon_products['item_name'] = amazon_products['item_name'].str.replace(
    #                 old_word_str, new_word_str, case=False, regex=False)
    #         else:
    #         # Convert text to hiragana for comparison
    #             amazon_products['item_name'] = amazon_products['item_name'].apply(
    #                 lambda x: x.replace(jaconv.kata2hira(old_word_str), jaconv.kata2hira(new_word_str))
    #                 if jaconv.kata2hira(old_word_str) in jaconv.kata2hira(x) else x)
    #     else:
    #         old_word_str = str(old_word)
    #         if old_word_str.isascii():
    #             amazon_products['item_name'] = amazon_products['item_name'].str.replace(
    #                 old_word_str, "", case=False, regex=False)
    #         else:
    #             amazon_products['item_name'] = amazon_products['item_name'].apply(
    #                 lambda x: x.replace(jaconv.kata2hira(old_word_str), "")
    #                 if jaconv.kata2hira(old_word_str) in jaconv.kata2hira(x) else x)

    for _, old_word, new_word in products_name_replacements[['置換前', '置換後']].itertuples():
        # If the new word is not NaN, replace the old word with the new word
        old_word = old_word.strip()

        if pd.notna(new_word):
            old_word_str = str(old_word)
            new_word_str = str(new_word)
            if old_word_str.isascii():
                amazon_products['item_name'] = amazon_products['item_name'].str.replace(
                    old_word_str, new_word_str, case=False, regex=False)                    
            else:
            # For Japanese text, use word boundaries to prevent partial matches
                amazon_products['item_name'] = amazon_products['item_name'].apply(
                    lambda x: x.replace(old_word_str, new_word_str) if old_word_str in x else x)
        else:
            old_word_str = str(old_word)
            if old_word_str.isascii():
                amazon_products['item_name'] = amazon_products['item_name'].str.replace(
                    old_word_str, "", case=False, regex=False)
            else:
            # For Japanese text, use exact matching for removal
                amazon_products['item_name'] = amazon_products['item_name'].apply(
                    lambda x: x.replace(old_word_str, "") if old_word_str in x else x)

    # for _, old_word, new_word in products_name_replacements[['置換前', '置換後']].itertuples():
    #     # If the new word is not NaN, replace the old word with the new word
    #     old_word = old_word.strip()
    #     new_word = new_word.strip() if pd.notna(new_word) else ''

    #     amazon_products['item_name'] = amazon_products['item_name'].str.replace(
    #                 old_word, new_word, case=False, regex=False) 

                

    amazon_products['item_name'] = amazon_products['item_name'].str.replace(r'\s+', ' ', regex=True).str.strip()
    amazon_products['item_name'] = amazon_products['item_name'].str.lstrip()

    # amazon_products['external_product_id'] = ""
    # amazon_products['external_product_id_type'] = ""

    amazon_products['brand_name'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['キーワード', 'brand_name (ブランド名)']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )

    amazon_products['manufacturer'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['キーワード', 'manufacturer (メーカ名)']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )

    for _, row in params.iterrows():
        amazon_products[row['項目名']] = row['設定値']

    # amazon_products['feed_product_type'] = ""
    amazon_products['part_number'] = yahoo_products['商品ID']

    # Copy cleaned item_name to product_description and bullet_point1
    amazon_products['product_description'] = amazon_products['item_name'] + "です。"

    amazon_products['model'] = yahoo_products['商品ID']
    amazon_products['update_delete'] = "Update"
    # amazon_products['quantity'] = ""
    # amazon_products['fulfillment_latency'] = ""
   
    amazon_products['standard_price'] = pd.DataFrame({'price1': yahoo_products['販売価格'], 'price2': yahoo_products['販売価格(即決)']}).max(axis=1)


    amazon_products['standard_price'] = amazon_products['standard_price'].apply(
        lambda price: next(
            (amazon_price for _, purchase_price, amazon_price in setup_sales_price[['仕入れ価格', 'アマゾン販売価格']].itertuples() 
             if purchase_price <= (2500 if price < setup_sales_price['仕入れ価格'].iloc[0] else price) < setup_sales_price['仕入れ価格'].shift(-1).fillna(float('inf')).loc[_]),
            setup_sales_price['アマゾン販売価格'].iloc[-1]  # Default to last price if no range matches
        )
    )
    
    # amazon_products['standard_price_points_percent'] = ""
    # amazon_products['condition_type'] = ""
    # amazon_products['condition_note'] = ""
    # amazon_products['product_site_launch_date'] = ""
    # amazon_products['delivery_schedule_group_id'] = ""
    # amazon_products['sale_price'] = ""
    # amazon_products['sale_price_points'] = ""
    # amazon_products['sale_from_date'] = ""
    # amazon_products['sale_end_date'] = ""
    # amazon_products['item_package_quantity'] = ""
    # amazon_products['website_shipping_weight'] = ""
    # amazon_products['website_shipping_weight_unit_of_measure'] = ""
    # amazon_products['item_weight'] = ""
    # amazon_products['item_weight_unit_of_measure'] = ""
    # amazon_products['item_height'] = ""
    # amazon_products['item_length'] = ""
    # amazon_products['item_width'] = ""
    # amazon_products['item_length_unit_of_measure'] = ""
    # amazon_products['item_display_weight'] = ""
    # amazon_products['item_display_weight_unit_of_measure'] = ""
    # amazon_products['item_display_length'] = ""
    # amazon_products['item_display_length_unit_of_measure'] = ""
    amazon_products['bullet_point1'] = amazon_products['item_name'] + "です。"
    # amazon_products['bullet_point2'] = ""
    # amazon_products['bullet_point3'] = ""
    # amazon_products['bullet_point4'] = ""
    # amazon_products['bullet_point5'] = ""

    amazon_products['recommended_browse_nodes'] = amazon_products.apply(
        lambda row: next(
            (brand for _, keyword, brand in kewords[['キーワード', 'recommended_browse_nodes (推奨ブラウズノード)']].itertuples() 
             if keyword in row['item_name']), 
            row['recommended_browse_nodes']
        ), axis=1
    )

    amazon_products['generic_keywords'] = amazon_products.apply(
        lambda row: next(
            (brand for _, keyword, brand in kewords[['キーワード', 'generic_keywords (検索キーワード)']].itertuples() 
             if keyword in row['item_name']), 
            row['generic_keywords']
        ), axis=1
    )

    # amazon_products['is_adult_product'] = ""
    amazon_products['main_image_url'] = yahoo_products['画像URL1']
    amazon_products['swatch_image_url'] = ""
    amazon_products['other_image_url1'] = yahoo_products['画像URL2']
    amazon_products['other_image_url2'] = yahoo_products['画像URL3']
    amazon_products['other_image_url3'] = yahoo_products['画像URL4']
    amazon_products['other_image_url4'] = yahoo_products['画像URL5']
    amazon_products['other_image_url5'] = yahoo_products['画像URL6']
    amazon_products['other_image_url6'] = yahoo_products['画像URL7']
    amazon_products['other_image_url7'] = yahoo_products['画像URL8']
    amazon_products['other_image_url8'] = ""
    


    # # Ensure Arrow/Streamlit compatibility: convert problematic columns to string
    # for col in ["recommended_browse_nodes", "generic_keywords"]:
    #     if col in amazon_products.columns:
    #         amazon_products[col] = amazon_products[col].astype(str)

    return amazon_products