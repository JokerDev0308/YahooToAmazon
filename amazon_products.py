import pandas as pd
from pathlib import Path


import config

yahoo_products = pd.read_excel(config.SCRAPED_XLSX)

params = pd.read_excel(config.SETTING_PARAMS)
kewords = pd.read_excel(config.SETTING_KEYWORDS)
products_name_replacements = pd.read_excel(config.SETTING_PRODUCT_NAME_REM)
exclude_sellers = pd.read_excel(config.SETTING_SELLER_EXCLUTIONS)
setup_sales_price = pd.read_excel(config.SETTING_SALES_PRICE)


def make_amazon_products():
    global yahoo_products
    
    amazon_products = pd.DataFrame(columns=config.amazon_columns)
    
    yahoo_products = yahoo_products[~yahoo_products['出品者ID'].isin(exclude_sellers['Excluded Seller ID'])]

    amazon_products['item_sku'] = yahoo_products['出品者ID']

    amazon_products['item_name'] = yahoo_products['商品名'].copy()
    for _, old_word, new_word in products_name_replacements[['Before Replacement', 'After Replacement']].itertuples():
        amazon_products['item_name'] = amazon_products['item_name'].str.replace(old_word, new_word)

    amazon_products['external_product_id'] = yahoo_products['商品ID']
    # amazon_products['external_product_id_type'] = ""

    amazon_products['brand_name'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['Keyword', 'Brand']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )

    amazon_products['manufacturer'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['Keyword', 'Manufacturer']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )
    # amazon_products['feed_product_type'] = ""
    # amazon_products['part_number'] = ""
    # amazon_products['product_description'] = ""
    # amazon_products['model'] = ""
    # amazon_products['update_delete'] = ""
    # amazon_products['quantity'] = ""
    # amazon_products['fulfillment_latency'] = ""
    # amazon_products['standard_price'] = ""
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
    # amazon_products['bullet_point1'] = ""
    # amazon_products['bullet_point2'] = ""
    # amazon_products['bullet_point3'] = ""
    # amazon_products['bullet_point4'] = ""
    # amazon_products['bullet_point5'] = ""

    amazon_products['recommended_browse_nodes'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['Keyword', 'Recommended Browse Nodes']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )

    amazon_products['generic_keywords'] = yahoo_products['商品名'].apply(
        lambda product_name: next(
            (brand for _, keyword, brand in kewords[['Keyword', 'Generic Keywords']].itertuples() 
             if keyword in product_name), 
            ""
        )
    )

    # amazon_products['is_adult_product'] = ""
    amazon_products['main_image_url'] = yahoo_products['画像URL1']
    amazon_products['swatch_image_url'] = yahoo_products['画像URL1']
    amazon_products['other_image_url1'] = yahoo_products['画像URL1']
    amazon_products['other_image_url2'] = yahoo_products['画像URL2']
    amazon_products['other_image_url3'] = yahoo_products['画像URL3']
    amazon_products['other_image_url4'] = yahoo_products['画像URL4']
    amazon_products['other_image_url5'] = yahoo_products['画像URL5']
    amazon_products['other_image_url6'] = yahoo_products['画像URL6']
    amazon_products['other_image_url7'] = yahoo_products['画像URL7']
    amazon_products['other_image_url8'] = yahoo_products['画像URL8']
    


    return amazon_products