# YahooToAmazon Scraping Project

This project scrapes product data from Yahoo and Amazon, processes it, and stores it in various formats.

## Features

- Scrapes product data from Yahoo and Amazon websites
- Processes and transforms product information
- Stores data in CSV and Excel formats
- Streamlit-based user interface
- Session management and configuration options

## Project Structure

```
.
├── .devcontainer/
│   └── devcontainer.json
├── .streamlit/
│   └── config.toml
├── data/
│   ├── amazon-product-table-result.csv
│   ├── amazon-product-table-template.csv
│   ├── amazon-product-table-template.xlsx
│   └── scraped_data.xlsx
├── drivers/
├── scripts/
├── system/
├── tmp/
├── amazon_products.py
├── app.py
├── config.py
├── home.py
├── main.py
├── requirements.txt
├── session_manager.py
├── settings.py
├── test.py
└── webdriver_manager.py
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` and `settings.py` to customize:
- File paths
- Column mappings
- Application settings

## Usage

1. Start the application:
```bash
python main.py
streamlit run app.py
```

2. Use the interface to:
    - Upload product URLs from Excel
    - Scrape data from Yahoo
    - Generate Amazon product listings
    - Download results as CSV

## Data Flow

1. Upload product URLs
2. System scrapes Yahoo product data
3. Data is processed and transformed
4. Amazon product listings are generated
5. Results can be downloaded as CSV

## Requirements

- Python 3.11+
- Chrome WebDriver
- Required Python packages listed in requirements.txt

## License

Apache License 2.0
