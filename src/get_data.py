import os
import time
import json
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")
OMDB_KEY = os.getenv("OMDB_API_KEY")

all_movies = []

# input parameters
start_page = input("Enter start page number (default 1): ")
if start_page.strip() == "":    
    start_page = 61
start_page = int(start_page)

save_name = input("Enter output filename (default movies_raw.json): ")
if save_name.strip() == "":
    save_name = "movies_raw.json"


print("Collecting ~1000 movies from TMDB and OMDB...")

for page in tqdm(range(start_page, start_page + 60), desc="TMDB Pages"):
    # TMDB request with minimum criteria
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_KEY,
        "sort_by": "revenue.desc",
        "primary_release_date.gte": "2010-01-01",
        "with_original_language": "en",
        "vote_count.gte": 50,
        "page": page
    }
    
    try:
        data = requests.get(url, params=params).json()
    except Exception as e:
        print(f"TMDB request failed on page {page}: {e}")
        break
    
    print(f"Processing TMDB page {page} with {len(data.get('results', []))} movies")
    
    for movie in data.get("results", []):
        movie_id = movie["id"]
        
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        details = requests.get(details_url, params={"api_key": TMDB_KEY}).json()
        imdb_id = details.get("imdb_id")
        
        if details.get("revenue", 0) < 500000 or not imdb_id:
            continue
        
        time.sleep(0.12)
        
        # get OMDB data from IMDb ID
        omdb_url = f"http://www.omdbapi.com/?apikey={OMDB_KEY}&i={imdb_id}"
        try:
            omdb_data = requests.get(omdb_url).json()
        except Exception:
            print(f"OMDB request failed for IMDb ID: {imdb_id}")
            omdb_data = None
        
        details["omdb"] = omdb_data
        
        all_movies.append(details)
        time.sleep(0.12)
        
        # Stop if we have 1000 movies
        if len(all_movies) >= 1000:
            break
    
    if len(all_movies) >= 1000:
        break

             
# Save to data/raw/ directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)
outfile = os.path.join(RAW_DIR, save_name)

with open(outfile, "w", encoding="utf-8") as f:
    json.dump(all_movies, f, indent=2)

print(f"\nDONE! Collected {len(all_movies)} movies")
print(f"File saved : {outfile}")