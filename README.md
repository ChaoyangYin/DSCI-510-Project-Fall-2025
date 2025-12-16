# Keys to Box Office Success: An Analysis of Movie Performance Factors and Critic-Audience Opinion Dynamics

**DSCI 510 Final Project - Fall 2025**

**Team Member (Solo)**  
- Name: Chaoyang (Sunny) Yin  
- USC ID: 7522481537  
- USC Email: sunnyyin@usc.edu  
- GitHub Username: ChaoyangYin

## Project Overview
This project analyzes factors influencing movie box office performance using data from TMDB and OMDb APIs. It examines how budget, genre, release timing, and especially critic-audience opinion dynamics relate to revenue and ROI. Due to limited separate Rotten Tomatoes audience scores, IMDb rating was used as an audience proxy. Inflation adjustment was applied to enable fair temporal comparisons.

## Repository Structure
├── data/
│   ├── raw/                # Raw JSON from APIs
│   └── processed/          # Cleaned CSV
├── project_proposal.pdf
├── results/                
|   ├── final_report.pdf    # Complete project report
|   ├── tables/             # Saved tables
|   └── plots/              # Saved plots
├── src/
│   ├── get_data.py         # Data collection from TMDB + OMDb
│   ├── clean_data.py       # Cleaning and structuring
│   ├── run_analysis.py     # Statistical analysis and insights
│   └── visualize_results.py # Generate and save visualizations
├── requirements.txt        # Python dependencies
└── README.md               # This file


## How to Run the Project
1. Clone the repository
2. Create `.env` file in root with your API keys:

TMDB_API_KEY=your_tmdb_key
OMDB_API_KEY=your_omdb_key

3. Install dependencies:
In terminal run:
pip install -r requirements.txt

4. Run in order
In root directory run:

python src/get_data.py      # Prompts you to input starting page and desired name for collected JSON, default from page 1 and movies_raw.json. Change start and name for multiple calls to API 
python src/clean_data.py
python src/run_analysis.py
python src/visualize_results.py

## Key Outputs

data/processed/movies_cleaned.csv: Final cleaned dataset
results/: All plots and summary tables, along with report
final_report.pdf: Complete report with findings and visualizations

Note: Raw data collection already completed — scripts will load existing files.