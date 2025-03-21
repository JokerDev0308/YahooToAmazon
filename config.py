# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 1  # Selenium wait timeout


CHROMEDRIVER_PATH = "drivers/chromedriver"
USERS_XLSX = 'data/users.json'
SCRAPED_XLSX = 'data/scraped_data.xlsx'
AMAZON_PRODUCT_TEMPLATE = 'data/amazon-product-table-template.xlsx'
AMAZON_PRODUCT_OUTPUT = 'data/amazon-product-table-result.xlsx'

PROGRESS_TXT = 'tmp/progress.txt'

SETTING_PARAMS = 'data/settings/params.xlsx'
SETTING_SELLER_EXCLUTIONS = 'data/settings/seller_exclusions.xlsx'
SETTING_KEYWORDS = 'data/settings/keywords.xlsx'
SETTING_SALES_PRICE = 'data/settings/sales_price.xlsx'
SETTING_PRODUCT_NAME_REM = 'data/settings/product_name_rem.xlsx'

BATCH_SIZE = 10

RUNNING = "tmp/running"
WAITING = False
CURRENT_USER = None
LOGIN_STATE = {}


yahoo_columns = [
    '商品URL',
    '商品画像',
    '商品名',
    '商品ID',
    '販売価格',
    '販売価格(即決)',
    '商品状態',
    '入札件数',
    '残り時間',
    '画像URL1',
    '画像URL2',
    '画像URL3',
    '画像URL4',
    '画像URL5',
    '画像URL6',
    '画像URL7',
    '画像URL8',
    '出品者ID'
]

amazon_columns = [
    'item_sku', 'item_name', 'external_product_id', 'external_product_id_type',
    'brand_name', 'manufacturer', 'feed_product_type', 'part_number',
    'product_description', 'model', 'update_delete', 'quantity',
    'fulfillment_latency', 'standard_price', 'standard_price_points_percent',
    'condition_type', 'condition_note', 'product_site_launch_date',
    'merchant_release_date', 'restock_date', 'optional_payment_type_exclusion',
    'delivery_schedule_group_id', 'sale_price', 'sale_price_points',
    'sale_from_date', 'sale_end_date', 'item_package_quantity', 'list_price',
    'website_shipping_weight', 'website_shipping_weight_unit_of_measure',
    'item_weight', 'item_weight_unit_of_measure', 'item_height', 'item_length',
    'item_width', 'item_length_unit_of_measure', 'item_display_weight',
    'item_display_weight_unit_of_measure', 'item_display_length',
    'item_display_length_unit_of_measure', 'bullet_point1', 'bullet_point2',
    'bullet_point3', 'bullet_point4', 'bullet_point5', 'recommended_browse_nodes',
    'generic_keywords', 'is_adult_product', 'main_image_url', 'swatch_image_url',
    'other_image_url1', 'other_image_url2', 'other_image_url3', 'other_image_url4',
    'other_image_url5', 'other_image_url6', 'other_image_url7', 'other_image_url8'
]


parms_columns = ['項目名', '説明', '設定値']
seller_exclution_columns = ['除外セラーID']
keywords_columns = ['キーワード', 'brand_name (ブランド名)', 'manufacturer (メーカ名)', 'recommended_browse_nodes (推奨ブラウズノード)', 'generic_keywords (検索キーワード)']
sales_columns = ['仕入れ価格', 'アマゾン販売価格']
product_name_replacements_columns = ['置換前', '置換後']