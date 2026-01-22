import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer

class MarketAnalyzer:
    def __init__(self, db_path="market_data.db"):
        self.db_path = db_path

    def fetch_data(self):
        """Connects to DB and returns a joined DataFrame."""
        conn = sqlite3.connect(self.db_path)
        # We join tweets and users to have a full dataset for analysis
        query = """
        SELECT t.*, u.display_name 
        FROM tweets t 
        JOIN users u ON t.username = u.username
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def generate_signals(self, df):
        """Converts text content into numerical trading signals."""
        # 1. Text-to-Signal: Simple Sentiment Scoring
        def get_sentiment(text):
            text = text.lower()
            score = 0
            if any(word in text for word in ['rally', 'bullish', 'up', 'breakout']):
                score += 1
            if any(word in text for word in ['crash', 'bearish', 'down', 'fall']):
                score -= 1
            return score

        df['sentiment_score'] = df['content'].apply(get_sentiment)

        # 2. Signal Aggregation: Weighted by Engagement
        # Tweets with more likes/views have higher impact
        df['weighted_signal'] = df['sentiment_score'] * (np.log1p(df['likes'] + df['views']))

        # 3. Confidence Intervals (Rolling 10-period window)
        window = 10
        df['signal_avg'] = df['weighted_signal'].rolling(window=window).mean()
        df['std_dev'] = df['weighted_signal'].rolling(window=window).std()
        
        # 95% Confidence Interval
        df['upper_ci'] = df['signal_avg'] + (1.96 * df['std_dev'] / np.sqrt(window))
        df['lower_ci'] = df['signal_avg'] - (1.96 * df['std_dev'] / np.sqrt(window))
        
        return df

    def plot_results(self, df):
        """Memory-efficient visualization using downsampling."""
        # Sampling if dataset > 500 rows to keep it lightweight
        plot_df = df.iloc[::2, :] if len(df) > 500 else df
        
        plt.figure(figsize=(12, 6))
        
        # Plot signal and shaded confidence interval
        plt.plot(plot_df.index, plot_df['signal_avg'], label='Aggregated Signal', color='#2ca02c')
        plt.fill_between(plot_df.index, plot_df['lower_ci'], plot_df['upper_ci'], 
                         color='gray', alpha=0.2, label='95% Confidence Interval')
        
        plt.axhline(0, color='black', linestyle='--', alpha=0.5)
        plt.title("Market Sentiment Signal Analysis (TF-IDF Weighted)")
        plt.xlabel("Tweet Sequence")
        plt.ylabel("Signal Strength")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    raw_data = analyzer.fetch_data()
    
    if not raw_data.empty:
        processed_data = analyzer.generate_signals(raw_data)
        analyzer.plot_results(processed_data)
        
        # Output Top Keywords via TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
        vectorizer.fit_transform(processed_data['content'])
        print("Top Market Keywords:", vectorizer.get_feature_names_out())
    else:
        print("No data found in database. Run the scraper first!")