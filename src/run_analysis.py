import pandas as pd
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROCESSED_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'movies_cleaned.csv')

RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results','tables')
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_clean_data(filepath: str = PROCESSED_PATH) -> pd.DataFrame:
    """Load the cleaned CSV file generated from clean_data.py.
    Args:
        filepath: Path to the cleaned CSV file.
    
    Returns:
        pd.DataFrame containing the cleaned movie data.
    """
    return pd.read_csv(filepath)

def calculate_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate key derived features for analysis.
    adjusted budget/revenue, ROI, critic/audience averages, gaps.
    
    Args:
        df: DataFrame with raw cleaned columns (revenue, budget, rt, imdb).
    
    Returns:
        pd.DataFrame with added ROI and gap columns.
    """
    # Adjust for inflation to base year 2025
    inflation_rates = {  # Annual CPI from 2010 to 2025
        2010: 1.016, 2011: 1.032, 2012: 1.021, 2013: 1.015, 2014: 1.016, 
        2015: 1.001, 2016: 1.013, 2017: 1.021, 2018: 1.024, 2019: 1.018, 
        2020: 1.012, 2021: 1.047, 2022: 1.080, 2023: 1.041, 2024: 1.029, 
        2025: 1.025 # estimated for 2025
    }
    
    # Calculate cumulative factor for each year
    base_year = 2025
    inflation_factors = []
    for year in df['year']:
        if year >= base_year:
            factor = 1.0
        else:
            factor = 1.0
            for y in range(year, base_year):
                rate = inflation_rates.get(y, 1.02)  # default 2% if missing
                factor *= rate
        inflation_factors.append(factor)

    df['inflation_factor'] = inflation_factors
    
    # Adjust budget and revenue based on inflation
    df['budget_adj'] = df['budget'] * df['inflation_factor']
    df['revenue_adj'] = df['revenue'] * df['inflation_factor']
    
    # Calculate ROI and adjusted ROI
    df['roi'] = df['revenue'] / df['budget']
    df['roi_adj'] = df['revenue_adj'] / df['budget_adj']
    
    # Average professional and audience score 
    df['critic_average'] = df[['rt', 'meta']].mean(axis=1, skipna=True)
    df['audience_average'] = df[['imdb', 'vote_average']].mean(axis=1, skipna=True)
    
    # Main gap: RT critic vs IMDb audience 
    df['critic_audience_gap'] = df['rt'] - df['imdb']
    
    # Bonus gap: professional average vs audience average
    df['pro_vs_audience_gap'] = df['critic_average'] - df['audience_average']
    return df


def analyze_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Compute simple correlation matrix for key variables.
    
    Args:
        df: DataFrame with derived features.
    
    Returns:
        pd.DataFrame with correlations.
    """
    # Drop duplicates due to exploded genres
    movie_level = df.drop_duplicates('tmdb_id')
    cols = ['budget', 'revenue', 'roi', 'rt', 'imdb', 'vote_average', 'critic_audience_gap', 'critic_average', 'audience_average', 'budget_adj', 'revenue_adj', 'roi_adj']
    corr = movie_level[cols].corr().round(3)
    
    corr.to_csv(os.path.join(RESULTS_DIR, "correlations.csv"))
    return corr


def analyze_by_genre(df: pd.DataFrame) -> pd.DataFrame:
    """Deep genre analysis — average metrics by genre.
    
    Args:
        df: Exploded DataFrame.
    
    Returns:
        pd.DataFrame with genre stats.
    """
    genre_stats = df.groupby('genres').agg({
        'revenue': 'mean',
        'roi': 'mean',
        'rt': 'mean',
        'imdb': 'mean',
        'critic_audience_gap': 'mean',
        'pro_vs_audience_gap': 'mean',
        'tmdb_id': 'count',
        'roi_adj': 'mean',
        'revenue_adj': 'mean',
        'budget_adj': 'mean'
    }).rename(columns={'tmdb_id': 'movie_count'}).round(2)
    
    genre_stats = genre_stats.sort_values('revenue', ascending=False)
    genre_stats.to_csv(os.path.join(RESULTS_DIR, "genre_summary.csv"))
    return genre_stats

def analyze_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Yearly trends analysis.
    
    Args:
        df: DataFrame (use movie-level).
    
    Returns:
        pd.DataFrame with yearly stats.
    """
    movie_level = df.drop_duplicates('tmdb_id')
    yearly = movie_level.groupby('year').agg({
        'revenue': 'mean',
        'roi': 'mean',
        'rt': 'mean',
        'imdb': 'mean',
        'critic_audience_gap': 'mean',
        'tmdb_id': 'count',
        'roi_adj': 'mean',
        'revenue_adj': 'mean',
        'budget_adj': 'mean'
    }).rename(columns={'tmdb_id': 'movie_count'}).round(2)
    

    yearly.to_csv(os.path.join(RESULTS_DIR, "yearly_trends.csv"))
    return yearly

def analyze_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly seasonality — best month to launch.
    
    Args:
        df: DataFrame (movie-level).
    
    Returns:
        pd.DataFrame with monthly stats.
    """
    movie_level = df.drop_duplicates('tmdb_id')
    monthly = movie_level.groupby('month').agg({
        'revenue': 'mean',
        'roi': 'mean',
        'tmdb_id': 'count',
        'roi_adj': 'mean',
        'revenue_adj': 'mean',
        'budget_adj': 'mean'
    }).rename(columns={'tmdb_id': 'movie_count'}).round(2)
    
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly.index = monthly.index.map(month_names)
    monthly.to_csv(os.path.join(RESULTS_DIR, "monthly_seasonality.csv"))
    return monthly

def analyze_top_movies(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N movies by revenue.
    
    Args:
        df: DataFrame.
        n: Number of movies.
    
    Returns:
        pd.DataFrame with top movies.
    """
    movie_level = df.drop_duplicates('tmdb_id')
    top = movie_level.sort_values('revenue', ascending=False).head(n)
    top_adj = movie_level.sort_values('revenue_adj', ascending=False).head(n)
    print("\nTOP 10 MOVIES BY REVENUE:")
    print(top[['title', 'year', 'revenue', 'roi', 'rt', 'imdb', 'critic_audience_gap']])
    print("\nTOP 10 MOVIES BY ADJUSTED REVENUE:")
    print(top_adj[['title', 'year', 'revenue_adj', 'roi_adj', 'rt', 'imdb', 'critic_audience_gap']])
    top.to_csv(os.path.join(RESULTS_DIR, "top_movies.csv"), index=False)
    return top

def print_key_insights(df: pd.DataFrame, genre_stats: pd.DataFrame, monthly: pd.DataFrame) -> None:
    
    """Print key insights for report."""
    
    print("\n" + "="*60)
    print("KEY INSIGHTS")
    
    print("\n1. Best Launch Timing:")
    best_month = monthly['revenue'].idxmax()
    print(f"   Highest average revenue in {best_month}")
    
    print("\n2. Genre Performance:")
    top_genre = genre_stats.iloc[0]
    print(f"   {top_genre.name} has highest average revenue and ROI")
    
    print("\n3. Opinion Dynamics:")
    print(f"   Average critic-audience gap: {df['critic_audience_gap'].mean():.1f} points")
    
    print("\n4. Factors Most Strongly Correlated with ROI:")
    corr = analyze_correlations(df)

    # Exclude self-correlation (ROI with ROI = 1.0)
    roi_corr = corr['roi'].drop(['roi','roi_adj']).abs().sort_values(ascending=False)
    print(f"   Top correlations with ROI:\n{roi_corr.head(5)}")

    # Same for adjusted ROI
    roi_adj_corr = corr['roi_adj'].drop(['roi','roi_adj']).abs().sort_values(ascending=False)
    print(f"   Top correlations with Adjusted ROI:\n{roi_adj_corr.head(5)}")


def main() -> None:
    
    """Main pipeline: load → extract → analyze → save."""
    
    print("Starting analysis...\n")
    
    df = load_clean_data()
    print(f"Loaded {len(df)} rows (exploded genres)")
    
    df = calculate_derived_features(df)
    
    corr = analyze_correlations(df)
    print("CORRELATION MATRIX:")
    print(corr)
    yearly = analyze_by_year(df)
    print("\nYEARLY TRENDS:")
    print(yearly)
    monthly = analyze_by_month(df)
    print("\nMONTHLY SEASONALITY (Best launch time):")
    print(monthly.sort_values('revenue', ascending=False))
    top = analyze_top_movies(df)
    genre_stats = analyze_by_genre(df)
    print("\nGENRE ANALYSIS (Top 10 by revenue):")
    print(genre_stats.head(10))
    
    print_key_insights(df, genre_stats, monthly)
    
    print("\nAnalysis complete! Tables saved to results/")

if __name__ == "__main__":
    main()
