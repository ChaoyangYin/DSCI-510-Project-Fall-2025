import json
import os
import pandas as pd


# global data paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'movies_raw_total.json')
PROCESSED_DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'processed', 'movies_cleaned.csv')


os.makedirs(os.path.dirname(PROCESSED_DATA_FILE), exist_ok=True)


def load_raw_data(filepath: str = RAW_DATA_PATH) -> list:
    """_summary_

    Args:
        filepath (str, optional): _description_. Defaults to RAW_DATA_PATH.

    Returns:
        list: _description_
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return data


        
def extract_omdb_scores(omdb_data: dict) -> dict:
    """Extract IMDb rating, Rotten Tomatoes Tomatometer, and Metascore from OMDb data.
    
    Returns a dictionary with:
        'imdb_score': float on 0–100 scale or None
        'rt_score': float on 0–100 scale or None 
        'metascore': float on 0–100 scale or None
    
    Args:
        omdb_data: The 'omdb' dictionary from raw movie data.
    
    Returns:
        dict with the three scores.
    """
    scores = {
        "imdb": None,
        "rt": None,
        "meta": None
    }
    
    if 'Ratings' in omdb_data:
        for rating in omdb_data['Ratings']:
            source = rating['Source']
            value = rating['Value']
            
            #   IMDb: 9.8/10 -> 98
            if source == 'Internet Movie Database':
                try:
                    scores["imdb"] = float(value.split('/')[0].strip()) * 10
                except:
                    pass  
            
            #  Rotten Tomatoes: 98% -> 98
            elif source == 'Rotten Tomatoes':
                try:
                    scores["rt"] = float(value.replace('%', '').strip())
                except:
                    pass  
    
    # Metascore 
    ms = omdb_data.get('Metascore')
    if ms and ms != 'N/A':
        try:
            scores["meta"] = float(ms)
        except:
            pass  
    
    return scores

def extract_tmdb_fields(movie: dict) -> dict:
    """Extract core TMDB fields from a single movie dictionary.
    
    Args:
        movie: Raw movie dictionary from TMDB.
    
    Returns:
        dict with cleaned TMDB fields.
    """
    
    # Extract genre names from list returned by movie['genres']
    genres = [glist['name'] for glist in movie.get('genres', [])]
    
    tmdb_fields = {
        "tmdb_id": movie.get('id'),
        "title": movie.get('title'),
        "release_date": movie.get('release_date'),
        "budget": movie.get('budget', 0),
        "revenue": movie.get('revenue', 0),
        "runtime": movie.get('runtime'),
        "vote_average": movie.get('vote_average') *10,  # scale to 0-100
        "vote_count": movie.get('vote_count'),
        "genres": genres  # list of strings
    }
    
    return tmdb_fields


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values, filter for quality, and prepare data for analysis.
    
    Steps:
    - Drop rows with no ratings (both rt and imdb missing)
    - Filter valid financial data (budget > 0, revenue > 0)
    
    Args:
        df: DataFrame from clean CSV (with rt, imdb, budget, revenue, year, roi)
    
    Returns:
        Filtered and quality-checked DataFrame ready for analysis.
    """
    print(f"Starting with {len(df)} rows")
    
    # Handle missing ratings — drop if both critic and audience missing
    before = len(df)
    df = df.dropna(subset=['rt', 'imdb']) # both critics and audience ratings must be present
    print(f"Dropped {before - len(df)} rows with no ratings")
    
    # Filter valid financial data
    before = len(df)
    df = df[df['budget'] > 0]
    df = df[df['revenue'] > 0]
    print(f"Dropped {before - len(df)} rows with budget or revenue = 0")
    
    # drop rows with missing year
    before = len(df)    
    df = df.dropna(subset=['year'])
    print(f"Dropped {before - len(df)} rows with missing year") 
    
    #drop rows with ROI > 100 (likely data errors)
    before = len(df)    
    df['roi'] = df['revenue']/ df['budget'] 
    df = df[df['roi'] <= 100]     
    print(f"Dropped {before - len(df)} rows with ROI > 100")
    print(f"Final dataset: {len(df)} movies ready for analysis")
    return df


def assemble_and_save(rows: list) -> None:
    """Assemble extracted rows into DataFrame, derive features, and save CSV.
    
    Args:
        rows: List of dictionaries, each representing one movie's cleaned data.
    """
    if not rows:
        print("No data to save.")
        return
    
    df = pd.DataFrame(rows)
    
    #creating year and month columns
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year
    df['month'] = df['release_date'].dt.month
    
    # Handle missing values and filter
    print(f"dataframe now contains {df.shape[0]} rows and {df.shape[1]} columns before filtering")
    df = handle_missing(df)
    
    # Explode genres for genre-level analysis
    df_exploded = df.explode('genres')
    df_exploded.to_csv(PROCESSED_DATA_FILE, index=False)
    
    print(f"Cleaned data saved: {PROCESSED_DATA_FILE}")
    print(f"Exploded on genres. Final shape: {df_exploded.shape[0]} rows (after exploding genres)")
    print("Columns:", df_exploded.columns.tolist())
    
    
def main():
    """Main pipeline: merge → load → extract → assemble → save."""
    
    print("Starting data cleaning pipeline...")
    
    # Step 1: Combine all raw JSON files in data/raw/
    raw_dir = os.path.join(PROJECT_ROOT, 'data', 'raw')
    json_files = [f for f in os.listdir(raw_dir) if f.endswith('.json') and f != 'movies_raw_total.json']
    
    if not json_files:
        print("No raw JSON files found!")
        return
    
    print(f"Found {len(json_files)} raw files: {json_files}")
    
    all_movies = []
    seen_ids = set()
    
    for file in json_files:
        file_path = os.path.join(raw_dir, file)
        print(f"Loading {file}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            movies = json.load(f)
        
        # Remove duplicates by tmdb_id
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id and movie_id not in seen_ids:
                seen_ids.add(movie_id)
                all_movies.append(movie)
    
    print(f"Combined {len(all_movies)} unique movies from all files")
    
    total_raw = os.path.join(raw_dir, 'movies_raw_total.json')
    with open(total_raw, 'w', encoding='utf-8') as f:
        json.dump(all_movies, f, indent=2)
    print(f"Saved combined raw data to {total_raw}")
    
    # Step 2: Extract fields
    print("Extracting fields...")
    cleaned_rows = []
    for movie in all_movies:
        tmdb = extract_tmdb_fields(movie)
        omdb_scores = extract_omdb_scores(movie.get('omdb', {}))
        row = dict(tmdb)
        row.update(omdb_scores)
        cleaned_rows.append(row)
    
    print(f"Extracted fields for {len(cleaned_rows)} movies")
    
    # Step 3: Assemble and save
    assemble_and_save(cleaned_rows)

if __name__ == "__main__":
    main()


