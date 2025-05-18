import requests
import json
import time
import pandas as pd
import os
from datetime import datetime
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bank_reviews_extraction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = "bank_reviews_data"

# List of banks and cities can be customized as needed
BANKS = [
    "Attijariwafa Bank",
    "Banque Populaire",
    "BMCE Bank",
    "Société Générale Maroc",
    "Crédit Agricole du Maroc",
    "Crédit du Maroc",
    "CIH Bank",
    "Al Barid Bank"
]

CITIES = [
    # Casablanca and districts
     "Ain Chock", "Ain Sebaa", "Al Fida", "Ben M'Sick", "Hay Hassani", 
    "Hay Mohammadi", "Maarif", "Moulay Rachid", "Sidi Belyout", "Sidi Bernoussi",
    "Sidi Moumen", "Sidi Othmane",
    
    # Rabat and districts
     "Agdal", "Hassan", "Yacoub El Mansour", "Youssoufia", "Hay Riad",
    
    # Marrakech and districts 
    "Marrakech", "Gueliz", "Medina", "Menara", "Sidi Youssef Ben Ali",
    
    # Fès and districts
     "Fès-Médina", "Jnan El Ouard", "Saiss", "Zouagha",
    
    # Tanger and districts
     "Beni Makada", "Charf-Mghogha", "Charf-Souani", "Tanger-Médina",
    
    # Other major cities
    "Meknès", "Oujda", "Tétouan", "El Jadida", "Kenitra", "Safi", 
    "Nador", "Khouribga", "Béni Mellal", "Taza", "Errachidia", "Larache", 
    "Khemisset", "Settat", "Al Hoceima", "Taroudant", "Berrechid", "Mohammedia", 
    "Temara", "Berkane", "Fquih Ben Salah"
     "Agadir", "Anza", "Dcheira", "Tikiouine", "Bensergao", "Aït Melloul",
    "Inezgane", "Temsia", "Drarga",
    "Biougra", "Oulad Teima"
 
]


class BankReviewsExtractor:
    """A simplified class to extract only essential bank review data from Google Maps API"""
    
    def __init__(self, api_key, output_dir=OUTPUT_DIR):
        """Initialize the extractor with API key and output directory"""
        self.api_key = api_key
        self.output_dir = output_dir
        
        # Create output directory if needed
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized BankReviewsExtractor with output to {self.output_dir}")
    
    def _get_headers_v1(self):
        """Return headers for Google Places API V1"""
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.reviews"
        }
    
    def search_banks_v1(self, query, page_token=None):
        """Search for banks using Google Places API V1"""
        url = "https://places.googleapis.com/v1/places:searchText"
        
        data = {
            "textQuery": query,
            "maxResultCount": 20
        }
        
        if page_token:
            data["pageToken"] = page_token
            
        try:
            response = requests.post(url, json=data, headers=self._get_headers_v1())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for '{query}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return {"places": [], "status": "ERROR"}
    
    def get_place_reviews_v1(self, place_id):
        """Get place reviews using Google Places API V1"""
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "reviews,rating"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting reviews for place {place_id}: {e}")
            return {"reviews": [], "status": "ERROR"}
    
    def extract_review_data(self, place, bank_name, city):
        """Extract only the essential review data from a place object"""
        reviews_data = []
        
        # Basic place information
        place_name = place.get('displayName', {}).get('text', '')
        address = place.get('formattedAddress', '')
        
        # Process reviews if available
        reviews = place.get('reviews', [])
        
        if not reviews:
            logger.debug(f"No reviews found for {place_name}")
            return reviews_data
        
        for review in reviews:
            # Extract only the essential review information
            review_text = review.get('text', {}).get('text', '')
            review_rating = review.get('rating', 0)
            
            # Get review date
            if 'publishTime' in review:
                publish_time = review.get('publishTime', '')
                # Convert from ISO format to YYYY-MM-DD
                try:
                    review_date = publish_time.split('T')[0]
                except:
                    review_date = None
            else:
                review_date = None
            
            # Create a simple record with only the requested fields
            reviews_data.append({
                'bank_name': bank_name,
                'branch_name': place_name,
                'location': address,
                'review_text': review_text,
                'rating': review_rating,
                'review_date': review_date
            })
        
        return reviews_data
    
    def process_bank_city(self, bank, city, max_results):
        """Process a specific bank in a specific city"""
        logger.info(f"Processing {bank} in {city}")
        
        query = f"{bank} in {city}"
        search_results = self.search_banks_v1(query)
        
        all_reviews = []
        results_count = 0
        
        for place in search_results.get('places', []):
            place_reviews = self.extract_review_data(place, bank, city)
            all_reviews.extend(place_reviews)
            results_count += len(place_reviews)
            
            if results_count >= max_results:
                break
            
        logger.info(f"Collected {len(all_reviews)} reviews for {bank} in {city}")
        return all_reviews
    
    def process_all_banks(self, banks, cities, max_results, max_workers):
        """Process all specified bank-city combinations to extract reviews"""
        logger.info(f"Processing {len(banks)} banks in {len(cities)} cities")
        
        # Create combinations of banks and cities
        combinations = [(bank, city, max_results) for bank in banks for city in cities]
        
        all_reviews = []
        
        # Process combinations concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_bank_city, bank, city, max_results): 
                      (bank, city) for bank, city, _ in combinations}
            
            for future in as_completed(futures):
                bank, city = futures[future]
                try:
                    reviews = future.result()
                    all_reviews.extend(reviews)
                    logger.info(f"Completed processing {bank} in {city}: {len(reviews)} reviews")
                except Exception as e:
                    logger.error(f"Error processing {bank} in {city}: {str(e)}")
        
        # Save individual bank-city results
        for bank in banks:
            for city in cities:
                bank_city_reviews = [r for r in all_reviews if r['bank_name'] == bank and r['location'].find(city) != -1]
                if bank_city_reviews:
                    filename = f"{self.output_dir}/{bank.replace(' ', '_')}_{city.replace(' ', '_')}.csv"
                    df = pd.DataFrame(bank_city_reviews)
                    df.to_csv(filename, index=False, encoding='utf-8')
                    logger.info(f"Saved {len(bank_city_reviews)} reviews to {filename}")
        
        # Save combined results
        combined_filename = f"{self.output_dir}/all_bank_reviews.csv"
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            df.to_csv(combined_filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(all_reviews)} combined reviews to {combined_filename}")
        
        return len(all_reviews)
    
    def combine_results(self, banks, cities):
        """Combine all individual CSV files into one master CSV"""
        all_data = []
        
        # Pattern to match bank-city CSV files
        pattern = f"{self.output_dir}/*.csv"
        
        for filename in glob.glob(pattern):
            try:
                df = pd.read_csv(filename)
                all_data.append(df)
            except Exception as e:
                logger.error(f"Error reading {filename}: {str(e)}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Ensure we only have the requested fields
            fields = ['bank_name', 'branch_name', 'location', 'review_text', 'rating', 'review_date']
            combined_df = combined_df[fields]
            
            combined_path = f"{self.output_dir}/all_bank_reviews.csv"
            combined_df.to_csv(combined_path, index=False, encoding='utf-8')
            logger.info(f"Combined {len(combined_df)} reviews into {combined_path}")


def main():
    """Main function to execute the bank review extraction"""
    parser = argparse.ArgumentParser(description="Extract bank reviews from Google Maps API")
    
    # Use API key from .env file as default if available
    default_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    default_max_results = int(os.getenv("MAX_RESULTS_PER_QUERY", "10"))
    default_max_workers = int(os.getenv("MAX_WORKERS", "3"))
    
    parser.add_argument("--api-key", "-k", default=default_api_key, 
                        help="Google Maps API key (defaults to GOOGLE_MAPS_API_KEY from .env)")
    parser.add_argument("--output-dir", "-o", default=OUTPUT_DIR, 
                        help="Output directory for results")
    parser.add_argument("--max-results", "-m", type=int, default=default_max_results, 
                        help=f"Maximum results per bank-city pair (defaults to {default_max_results})")
    parser.add_argument("--max-workers", "-w", type=int, default=default_max_workers, 
                        help=f"Maximum number of concurrent workers (defaults to {default_max_workers})")
    parser.add_argument("--specific-bank", "-b", help="Extract for a specific bank only")
    parser.add_argument("--specific-city", "-c", help="Extract for a specific city only")
    
    args = parser.parse_args()
    
    # Validate API key
    if not args.api_key:
        logger.error("No API key provided. Set it in .env file or use --api-key parameter.")
        return
    
    extractor = BankReviewsExtractor(args.api_key, args.output_dir)
    
    # Filter banks and cities if specified
    banks_to_process = [args.specific_bank] if args.specific_bank else BANKS
    cities_to_process = [args.specific_city] if args.specific_city else CITIES
    
    # Process banks and cities
    total_reviews = extractor.process_all_banks(
        banks=banks_to_process,
        cities=cities_to_process,
        max_results=args.max_results,
        max_workers=args.max_workers
    )
    
    logger.info(f"Extraction complete. Total reviews collected: {total_reviews}")


if __name__ == "__main__":
    main()