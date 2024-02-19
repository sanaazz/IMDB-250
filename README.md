# IMDB-250 Data Project

## Overview
The IMDB-250 Data Project is a comprehensive toolkit for scraping, preprocessing, and storing data from IMDB's Top 250 movies list. It aims to facilitate data analysis and insights into trends within top-rated movies. This project includes scripts for data collection (`crawl.py`), preprocessing (`preprocessing.py`), and database interaction (`db.py`), alongside a structured database schema for efficient data storage.

## Features
- **Data Scraping**: Automated collection of movie data from IMDB's Top 250 list.
- **Data Preprocessing**: Cleaning and formatting the scraped data for analysis.
- **Database Integration**: Storing and managing the processed data in a structured database.

## Getting Started

### Prerequisites
- Python 3.x
- Required Python libraries: `beautifulsoup4`, `pandas`, `sqlalchemy`, `requests`
- MySQL or SQLite (depending on your setup)

### Installation
1. Clone the repository: 
    ```bash
    git clone https://github.com/sanaazz/IMDB-250.git
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

### Usage
1. **Data Scraping**: Run `crawl.py` to fetch data from IMDB.
    ```bash
    python crawl.py
   
2. **Data Preprocessing**: Execute `preprocessing.py` to clean and prepare the data.
    ```bash
    python preprocessing.py
   
3. **Database Setup and Data Storage**: Use `db.py` to create the database schema and insert the preprocessed data.
    ```bash
    python db.py

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## License
Distributed under the AGPL-3.0 License. See `LICENSE` for more information.

## Acknowledgments
- IMDB for providing an extensive dataset of top-rated movies.

