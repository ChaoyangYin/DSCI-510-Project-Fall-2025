import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results', 'tables')
SAVE_DIR = os.path.join(PROJECT_ROOT, 'results', 'plots')
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_analysis_results():
    """Load the tables saved from run_analysis.py.
    
    Returns:
        Dictionary with the saved tables.
    """
    return {
        'correlations': pd.read_csv(os.path.join(RESULTS_DIR, "correlations.csv"), index_col=0),
        'genre_summary': pd.read_csv(os.path.join(RESULTS_DIR, "genre_summary.csv"), index_col=0),
        'yearly_trends': pd.read_csv(os.path.join(RESULTS_DIR, "yearly_trends.csv"), index_col=0),
        'monthly_seasonality': pd.read_csv(os.path.join(RESULTS_DIR, "monthly_seasonality.csv"), index_col=0),
        'top_movies': pd.read_csv(os.path.join(RESULTS_DIR, "top_movies.csv"))
    }

def create_visualizations() -> None:
    """Create and save all visualizations using results from run_analysis.py.
    
    Saves 7 plots to the results/ folder for inclusion in the final report.
    
    Returns:
        None (plots are saved as PNG files).
    """
    results = load_analysis_results()
    
    # Plot 1: Correlation Heatmap (from run_analysis correlations)
    plt.figure(figsize=(10, 8))
    sns.heatmap(results['correlations'], annot=True, cmap='coolwarm', center=0, fmt='.3f')

    # Tilt x-axis labels 45 degrees
    plt.xticks(rotation=45, ha='right')   
    plt.yticks(rotation=0)
    plt.title("Correlation Matrix of Key Variables")
    plt.tight_layout()  
    plt.savefig(os.path.join(SAVE_DIR, "correlation_heatmap.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Bar - Average ROI by Genre (from genre_summary)
    plt.figure(figsize=(12, 8))
    sns.barplot(x='roi', y=results['genre_summary'].index, data=results['genre_summary'])
    plt.title("Average ROI by Genre (Top 10)")
    plt.savefig(os.path.join(SAVE_DIR, "roi_by_genre.png"))
    plt.close()
    
    # Plot 3: Line - Revenue Trends Over Years (from yearly_trends)
    plt.figure(figsize=(12, 8))
    plt.plot(results['yearly_trends'].index, results['yearly_trends']['revenue'], marker='o')
    plt.plot(results['yearly_trends'].index, results['yearly_trends']['revenue_adj'], marker='o')
    plt.title("Average Revenue Over Years")
    plt.xlabel("Year")
    plt.ylabel("Average Revenue")
    plt.legend(["Revenue", "Adjusted Revenue"])
    plt.savefig(os.path.join(SAVE_DIR, "revenue_over_years.png"))
    plt.close()
    
    # Plot 4: Line - ROI Trends Over Years (from yearly_trends)
    plt.figure(figsize=(12, 8))
    plt.plot(results['yearly_trends'].index, results['yearly_trends']['roi'], marker='o')
    plt.title("Average ROI Over Years")
    plt.xlabel("Year")
    plt.ylabel("Average ROI")
    plt.legend(["ROI"])
    plt.savefig(os.path.join(SAVE_DIR, "ROI_over_years.png"))
    plt.close()
    
    # Plot 5: Bar - Average Critic-Audience Gap by Genre
    plt.figure(figsize=(12, 8))
    sns.barplot(x='critic_audience_gap', y=results['genre_summary'].index, data=results['genre_summary'])
    plt.title("Average Critic-Audience Gap by Genre")
    plt.savefig(os.path.join(SAVE_DIR, "gap_by_genre.png"))
    plt.close()
    
    # Plot 6: Bar - Monthly Seasonality (Best Launch Time)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=results['monthly_seasonality'].index, y='revenue', data=results['monthly_seasonality'])
    plt.title("Average Revenue by Month (Best Launch Time)")
    plt.savefig(os.path.join(SAVE_DIR, "monthly_seasonality.png"))
    plt.close()
    
    # Plot 7: Bar plot - Top factors influencing ROI and Adjusted ROI
    plt.figure(figsize=(12, 10))

    # Get correlations with ROI and ROI_adj, exclude self
    roi_corr = results['correlations']['roi'].drop(['roi', 'roi_adj']).abs()
    roi_adj_corr = results['correlations']['roi_adj'].drop(['roi', 'roi_adj']).abs()

    # Take top 10 factors (by average absolute correlation)
    top_factors = roi_corr.add(roi_adj_corr).div(2).sort_values(ascending=True).tail(10).index

    # Create DataFrame for plotting
    plot_df = pd.DataFrame({
        'ROI Correlation': roi_corr[top_factors],
        'Adjusted ROI Correlation': roi_adj_corr[top_factors]
    })

    # Horizontal bar plot
    ax = plot_df.plot(kind='barh', figsize=(12, 10), width=0.8)
    # Add numbers at the end of each bar
    for i, (idx, row) in enumerate(plot_df.iterrows()):
        # ROI value
        ax.text(row['ROI Correlation'] + 0.001, i - 0.15, f"{row['ROI Correlation']:.3f}", 
                va='center', ha='left', color='black', fontweight='bold')
        # Adjusted ROI value
        ax.text(row['Adjusted ROI Correlation'] + 0.001, i + 0.15, f"{row['Adjusted ROI Correlation']:.3f}", 
                va='center', ha='left', color='black', fontweight='bold')
    
    plt.title("Top Factors Influencing ROI and Adjusted ROI (Absolute Correlation)")
    plt.xlabel("Absolute Correlation Strength")
    plt.ylabel("Factors")
    plt.legend(title="Metric")
    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, "top_factors_roi_bar.png"), dpi=300, bbox_inches='tight')
    plt.close()
    


def main() -> None:
    """Run the complete visualization pipeline."""
    print("Starting visualization...")
    create_visualizations()
    print(f"All 7 visualizations saved to {SAVE_DIR}")

if __name__ == "__main__":
    main()