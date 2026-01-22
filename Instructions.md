📋 Project Execution Instructions
Clone the Repository: Download the project files to your local machine and navigate into the root directory.

Install Dependencies: Run pip install -r requirements.txt to install the necessary libraries (undetected-chromedriver, selenium, scikit-learn, python-dotenv, etc.).

Configure Your Credentials:

Create a new file named .env in the root folder.

Paste the following lines and fill in your actual X (Twitter) details:

X_EMAIL=#please add email

X_USERNAME=#please add username

X_PASSWORD=#please add password

DB_PATH=market_data.db

Run the Scraper (Phase 1):

Execute the main script: python twittersrapper.py.

The bot will automatically log in using the .env credentials, search for #nifty50 and #sensex, and scroll to collect data until the limit is reached.

Wait for the "Successfully saved to DB" messages to appear in your terminal.

Run the Analysis (Phase 2):

Once the database is populated, execute the analysis script separately: python analysis.py.

This script fetches the data from the database, converts text to quantitative signals, and generates a visual plot of market sentiment.

Review the Results:

Market Trends Report: Check the terminal output for the top trending hashtags based on likes and frequency.

Sentiment Plot: A window will open displaying the aggregated trading signals with 95% confidence intervals.

⚠️ Reviewer Notes
Input Needed: The reviewer must provide valid X credentials in the .env file; otherwise, the bot will be blocked by the login screen.

Running Order: The scraper (twittersrapper.py) must be run before the analysis (analysis.py) to ensure the database tables exist and contain data.

Headless Mode: The bot is currently configured with headless=False so the reviewer can see the automation in real-time.
