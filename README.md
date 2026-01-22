TwitterScrapper/
├── data/
│   ├── market_data.db       # Created by script
│   └── analysis_results.txt # Sample output from Trends Report
├── src/
│   ├── __init__.py
│   └── twittersrapper.py    # Main WebBot class code
├── .gitignore               # Exclude chrome_profile and DB from git
├── README.md                # Project overview and setup
├── requirements.txt         # Dependency list
├── main.py                  # Entry point to run the bot
└── technical_doc.md         # Brief technical approach

# TwitterScrapper

A robust Selenium-based web scraper built with `undetected_chromedriver` to bypass bot detection. It extracts financial market updates from X (Twitter) and stores them in a normalized SQLite database.

## Setup Instructions
1. **Clone the repository:**
   `git clone https://github.com/Onzork9/TwitterScrapper.git`
2. **Install dependencies:**
   `pip install -r requirements.txt`
3. **Run the bot:**
   `python main.py`

## Features
- **Stealth Browsing:** Uses `undetected_chromedriver` and proxy rotation.
- **Relational Storage:** Normalizes data into `users`, `tweets`, and `hashtags` tables.
- **Analytics:** Generates a "Market Trends Report" based on hashtag frequency and engagement.
