# House Listing Scraper

This project consists of Python scripts that scrape and collect data about house listings, including their prices, from a website.

## Features

- SQLAlchemy models for house listings and their price histories.
- Utility functions to extract and format house listing data.
- Web scraping capability for collecting real-time data from a housing website.
- Data insertion into a database.

## Dependencies

- SQLAlchemy: For ORM-based database interactions.
- ChromeDriver: For controlling the Chrome web browser.
- Selenium: For automating the web browser.

## Database Structure

1. **HouseListing**:

   - Address (Composite Primary Key)
   - City (Composite Primary Key)
   - State (Composite Primary Key)
   - Zip (Composite Primary Key)
   - Beds
   - Baths
   - Sqft

2. **PriceListing**:
   - Transaction ID (Primary Key)
   - Address (Composite Foriegn Key)
   - City (Composite Foriegn Key)
   - State (Composite Foriegn Key)
   - Zip (Composite Foriegn Key)
   - Price
   - Date

## Usage

Before you run the script, make sure you have the necessary dependencies installed.

1. Navigate to the project directory.
2. Run the script:

```bash
python ./src/main.py
```
