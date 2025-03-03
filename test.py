import re

href = "https://auctions.yahoo.co.jp/seller/345febjhoos6237" 

match = re.search(r'seller/([a-zA-Z0-9_-]+)', href)

print(match.group(1))