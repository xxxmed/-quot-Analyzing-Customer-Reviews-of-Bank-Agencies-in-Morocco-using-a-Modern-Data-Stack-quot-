import requests
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Function to search for banks in Morocco
def search_banks(bank_name, location="Morocco", page_token=None):
    """
    Search for banks in Morocco using the Google Places API
    """
    endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Construct the search query
    query = f"{bank_name} bank in {location}"
    
    params = {
        "query": query,
        "key": API_KEY
    }
    
    # Add page token if available for pagination
    if page_token:
        params["pagetoken"] = page_token
    
    response = requests.get(endpoint_url, params=params)
    return response.json()

# Function to get place details including reviews
def get_place_details(place_id):
    """
    Get detailed information about a place, including reviews
    """
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,geometry,rating,reviews",
        "key": API_KEY
    }
    
    response = requests.get(endpoint_url, params=params)
    return response.json()

# Main function to extract reviews
def extract_bank_reviews(bank_names, max_results=100):
    """
    Extract reviews for specified banks in Morocco
    """
    all_reviews = []
    
    for bank_name in bank_names:
        results_count = 0
        next_page_token = None
        
        print(f"Searching for {bank_name} branches...")
        
        # Continue until we reach max_results or no more pages
        while results_count < max_results:
            # Search for bank branches
            search_results = search_banks(bank_name, page_token=next_page_token)
            
            # Check if the search was successful
            if search_results['status'] != 'OK':
                print(f"Error searching for {bank_name}: {search_results['status']}")
                break
            
            # Process each bank branch
            for place in search_results.get('results', []):
                place_id = place['place_id']
                
                # Get detailed information including reviews
                place_details = get_place_details(place_id)
                
                if place_details['status'] != 'OK':
                    print(f"Error getting details for place {place_id}: {place_details['status']}")
                    continue
                
                result = place_details.get('result', {})
                
                # Skip places without reviews
                if 'reviews' not in result:
                    continue
                
                # Extract location coordinates
                location = result.get('geometry', {}).get('location', {})
                lat = location.get('lat', '')
                lng = location.get('lng', '')
                
                # Process each review
                for review in result.get('reviews', []):
                    # Convert timestamp to readable date
                    review_date = datetime.fromtimestamp(
                        review.get('time', 0)
                    ).strftime('%Y-%m-%d')
                    
                    review_data = {
                        'bank_name': bank_name,
                        'branch_name': result.get('name', ''),
                        'location': result.get('formatted_address', ''),
                        'latitude': lat,
                        'longitude': lng,
                        'rating': review.get('rating', ''),
                        'review_text': review.get('text', ''),
                        'review_date': review_date,
                        'reviewer_name': review.get('author_name', '')
                    }
                    
                    all_reviews.append(review_data)
                
                results_count += 1
                
                # Check if we've reached the maximum number of results
                if results_count >= max_results:
                    break
            
            # Check if there are more pages of results
            next_page_token = search_results.get('next_page_token')
            
            # If there's no next page token, we've reached the end
            if not next_page_token:
                break
            
            # Wait 2 seconds before making the next request (API requirement)
            time.sleep(2)
    
    # Create a DataFrame from all reviews
    df = pd.DataFrame(all_reviews)
    return df

# List of major banks in Morocco
moroccan_banks = [
    "Attijariwafa Bank",
    "Banque Populaire",
    "BMCE Bank",
    "Société Générale Maroc",
    "Crédit Agricole du Maroc",
    "Crédit du Maroc",
    "CIH Bank",
    "Al Barid Bank",
    "Arab Bank Morocco",
    "BMCI"
]

# Save the data to CSV
if __name__ == "__main__":
    # Make sure you've set up your API key in a .env file or directly here
    if not API_KEY:
        print("Please set your Google Maps API key in the .env file")
        exit(1)
        
    print("Starting extraction of bank reviews...")
    reviews_df = extract_bank_reviews(moroccan_banks, max_results=50)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"moroccan_bank_reviews_{timestamp}.csv"
    reviews_df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"Extraction complete. {len(reviews_df)} reviews saved to {filename}")
    
    # Display a summary
    print("\nSummary of collected data:")
    print(reviews_df['bank_name'].value_counts())
    print("\nAverage ratings by bank:")
    print(reviews_df.groupby('bank_name')['rating'].mean().sort_values(ascending=False))