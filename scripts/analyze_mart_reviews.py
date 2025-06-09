import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import numpy as np
from textblob import TextBlob
from langdetect import detect, DetectorFactory
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import warnings
warnings.filterwarnings('ignore')

# Set seed for consistent language detection
DetectorFactory.seed = 0

class MartReviewAnalyzer:
    def __init__(self, db_config):
        """Initialize with database configuration"""
        self.db_config = db_config
        self.engine = None
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        
    def connect_to_db(self):
        """Create database connection"""
        try:
            connection_string = f"postgresql://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            self.engine = create_engine(connection_string)
            print("Database connection established successfully!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
        return True
    
    def load_mart_data(self):
        """Load data from mart_location_reviews table"""
        try:
            query = """
                SELECT 
                    bank_name,
                    location,
                    concatenated_text,
                    review_count,
                    avg_rating
                FROM mart_location_reviews
            """
            df = pd.read_sql(query, self.engine)
            print(f"Loaded {len(df)} records from mart_location_reviews")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def detect_language(self, text):
        """Detect language of text"""
        try:
            if pd.isna(text) or text.strip() == "":
                return "unknown"
            return detect(str(text))
        except:
            return "unknown"
    
    def get_sentiment_textblob(self, text):
        """Get sentiment using TextBlob"""
        try:
            if pd.isna(text) or text.strip() == "":
                return "Neutral", 0.0
            
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "Positive", polarity
            elif polarity < -0.1:
                return "Negative", polarity
            else:
                return "Neutral", polarity
        except:
            return "Neutral", 0.0
    
    def preprocess_for_lda(self, texts, language='english'):
        """Preprocess texts for LDA topic modeling"""
        try:
            stop_words = set(stopwords.words(language))
        except:
            stop_words = set(stopwords.words('english'))
        
        processed_texts = []
        
        for text in texts:
            if pd.isna(text) or text.strip() == "":
                processed_texts.append("")
                continue
                
            # Clean text
            text = text.lower()
            text = re.sub(r'[^a-z\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if text.strip() == "":
                processed_texts.append("")
                continue
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and short words
            tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
            
            # Lemmatize
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            processed_texts.append(' '.join(tokens))
        
        return processed_texts
    
    def perform_topic_modeling(self, texts, n_topics=5, max_features=100):
        """Perform LDA topic modeling"""
        processed_texts = self.preprocess_for_lda(texts)
        non_empty_texts = [text for text in processed_texts if text.strip() != ""]
        
        if len(non_empty_texts) < n_topics:
            print(f"Warning: Not enough non-empty texts for {n_topics} topics. Reducing to {max(1, len(non_empty_texts)//2)}")
            n_topics = max(1, len(non_empty_texts)//2)
        
        if len(non_empty_texts) == 0:
            print("No valid texts for topic modeling")
            return None, None, None
        
        vectorizer = CountVectorizer(
            max_features=max_features,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        try:
            doc_term_matrix = vectorizer.fit_transform(non_empty_texts)
        except ValueError as e:
            print(f"Error in vectorization: {e}")
            return None, None, None
        
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10
        )
        
        lda.fit(doc_term_matrix)
        feature_names = vectorizer.get_feature_names_out()
        
        return lda, vectorizer, feature_names
    
    def display_topics(self, lda_model, feature_names, n_top_words=10):
        """Display the top words for each topic"""
        topics = []
        for topic_idx, topic in enumerate(lda_model.components_):
            top_words_idx = topic.argsort()[-n_top_words:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'top_words': top_words,
                'word_weights': [topic[i] for i in top_words_idx]
            })
            print(f"Topic {topic_idx}: {', '.join(top_words)}")
        return topics
    
    def analyze_mart_data(self):
        """Main function to perform complete analysis"""
        print("Starting mart data analysis...")
        
        if not self.connect_to_db():
            return None
        
        df = self.load_mart_data()
        if df is None:
            return None
        
        print("\n1. Detecting languages...")
        df['detected_language'] = df['concatenated_text'].apply(self.detect_language)
        
        print("\n2. Performing sentiment analysis...")
        sentiment_results = df['concatenated_text'].apply(self.get_sentiment_textblob)
        df['sentiment'] = [result[0] for result in sentiment_results]
        df['sentiment_score'] = [result[1] for result in sentiment_results]
        
        print("\n3. Performing topic modeling...")
        lda_model, vectorizer, feature_names = self.perform_topic_modeling(
            df['concatenated_text'].fillna(''), n_topics=5
        )
        
        if lda_model is not None:
            print(f"\nTopics found:")
            topics = self.display_topics(lda_model, feature_names)
        else:
            topics = None
        
        # Display results summary
        print(f"\n=== ANALYSIS SUMMARY ===")
        print(f"Total locations analyzed: {len(df)}")
        print(f"\nLanguage distribution:")
        print(df['detected_language'].value_counts())
        print(f"\nSentiment distribution:")
        print(df['sentiment'].value_counts())
        
        # Save results to CSV
        output_file = 'mart_analysis_results.csv'
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        # Save results to database
        try:
            # Create a new table for analysis results
            df.to_sql('mart_analysis_results', self.engine, if_exists='replace', index=False)
            print(f"\nResults saved to database table 'mart_analysis_results'")
        except Exception as e:
            print(f"Error saving results to database: {e}")
        return {
            'dataframe': df,
            'lda_model': lda_model,
            'vectorizer': vectorizer,
            'topics': topics,
            'feature_names': feature_names
        }

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'DataWare',
        'username': 'ahmed',
        'password': os.getenv('DB_PASSWORD'),
        'port': 5432
    }
    
    # Initialize analyzer
    analyzer = MartReviewAnalyzer(db_config)
    
    # Perform analysis
    results = analyzer.analyze_mart_data()
    
    if results:
        print("\nAnalysis completed successfully!")
        print(f"Results shape: {results['dataframe'].shape}")
        print(f"Columns: {list(results['dataframe'].columns)}") 