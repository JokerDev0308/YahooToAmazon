# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 1  # Selenium wait timeout
CHROMEDRIVER_PATH = "drivers/chromedriver-linux64/chromedriver"
JANCODE_SCV = 'data/jan_codes.csv'
SCRAPED_XLSX = 'data/scraped_data.xlsx'

RUNNING = "tmp/running"
WAITING = False
CURRENT_USER = None
LOGIN_STATE = {}


column_name_mapping = {
    '商品URL': '商品URL',
    '商品画像': '商品画像',
    '商品名': '商品名',
    '商品ID': '商品ID',
    '販売価格': '販売価格',
    '販売価格(即決)': '販売価格(即決)',
    '商品状態': '商品状態',
    '入札件数': '入札件数',
    '残り時間': '残り時間',
    '画像URL1': '画像URL1',
    '画像URL2': '画像URL2',
    '画像URL3': '画像URL3',
    '画像URL4': '画像URL4',
    '画像URL5': '画像URL5',
    '画像URL6': '画像URL6',
    '画像URL7': '画像URL7',
    '画像URL8': '画像URL8',
    '出品者ID': '出品者ID'
}

ordered_columns = [
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

