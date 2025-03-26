import re

def clean_price(price_str):
        # Ensure the input is a string
        if isinstance(price_str, (int, float)):  # If the input is numeric, convert it to a string
            price_str = str(price_str)
        
        match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?=税|円)', price_str)
        
        if match:
            cleaned_price = match.group(0)  
            cleaned_price = cleaned_price.replace(',', '')  
            
            try:
                return float(cleaned_price)  # Convert to float
            except ValueError:
                return 0.0 
        else:
            return 0.0  
        

t = '300円'
t2 = '36,700円'

print(clean_price(t))
print(clean_price(t2))
