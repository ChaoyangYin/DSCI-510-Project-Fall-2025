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
├── data/<br>
│   ├── raw/                # Raw JSON from APIs<br>
│   └── processed/          # Cleaned CSV<br>
├── project_proposal.pdf<br>
├── results/<br>
│   ├── final_report.pdf    # Complete project report<br>
│   ├── tables/             # Saved tables<br>
│   └── plots/              # Saved plots<br>
├── src/<br>
│   ├── get_data.py         # Data collection from TMDB + OMDb<br>
│   ├── clean_data.py       # Cleaning and structuring<br>
│   ├── run_analysis.py     # Statistical analysis and insights<br>
│   └── visualize_results.py # Generate and save visualizations<br>
├── requirements.txt        # Python dependencies<br>
└── README.md               # This file<br>


## How to Run the Project
1. Clone the repository
2. Create `.env` file in root with your API keys:<br>

TMDB_API_KEY=your_tmdb_key<br>
OMDB_API_KEY=your_omdb_key<br>

3. Install dependencies:
In terminal run:<br>
pip install -r requirements.txt<br>

## Important Note on Data Collection

To reconstruct the exact dataset (may be subject to change in online database) used in this project, the data collection script (`get_data.py`) must be run in two separate sessions on different days:

- **Empty data\raw first if you want to build the dataset from scratch**
- **First run**: Start page = 1 (collects pages 1–60) (usually around 20 minutes)
- **Second run**: Start page = 61 (collects pages 61–120)

This two-day approach is necessary due to the **OMDb API daily limit of 1,000 requests** on the free tier. Each run uses approximately 1,000–1,200 requests (one per movie for ratings), so splitting across days avoids exceeding the limit.

The final dataset combines both runs (`movies_raw.json` and `movies_raw_day2.json`) into 2,000 unique movies after deduplication.

**Raw data is already included in `data/raw/` — you do not need to re-run collection unless testing.**

4. Run in order:
In root directory run:<br>
IF YOU WANT TO USE EXISTING RAW DATA SKIP python src/get_data.py <br>
python src/get_data.py<br>      # Prompts you to input starting page and desired name for collected JSON, default from page 1 and movies_raw.json. Change start and name for multiple calls to API<br> 
python src/clean_data.py<br>
python src/run_analysis.py<br>
python src/visualize_results.py<br>

## Key Outputs

data/processed/movies_cleaned.csv: Final cleaned dataset
results/: All plots and summary tables, along with report
final_report.pdf: Complete report with findings and visualizations

Note: Raw data collection already completed — scripts will load existing files.
