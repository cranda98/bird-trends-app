## Michigan Bird Species Trends Dashboard

This repository contains a Python Dash application for exploring county-level bird observation trends in Michigan using filtered eBird checklist data and precomputed statistical trend models.
The application allows users to select a county and species and view yearly observation totals alongside model-based trend predictions when available.

## Data Inputs

The application relies on two input datasets stored in the data/ directory.

### Observation Data

```bash
ebd_MI_threecounties.csv.gz
```
Compressed CSV containing eBird checklist records with the following relevant fields:
- OBSERVATION DATE
- OBSERVATION COUNT
- COMMON NAME
- COUNTY
- DURATION MINUTES
- NUMBER OBSERVERS
- ALL SPECIES REPORTED

### Trend Prediction Data

```bash
species_trend_predictions.csv
```

CSV containing precomputed model outputs by species and county, including:
- predicted yearly counts
- lower and upper confidence intervals
- model R² values
- p-values
- number of years used for model fitting

## Data Processing

Before analysis, the observation dataset is filtered to improve comparability and data quality:
- Only complete checklists are retained (ALL SPECIES REPORTED == 1)
- Observation duration limited to 5–180 minutes
- Checklists with more than five observers are excluded
- Observation counts must be positive
- Observation dates are parsed and converted to calendar years
After filtering, observations are aggregated by year and species using summed counts.

This will print the mean songs per hour to the terminal and display a bar chart showing singing frequency by bird species.

## Application Behavior
### User Inputs
- County selection
- Species selection

### Outputs
- Time series of observed yearly counts
- Optional model-predicted trend line with confidence intervals
- Summary statistics computed from observed data

## Trend Calculation

A linear regression slope is computed on yearly observed counts using numpy.polyfit. The slope is used to classify trends as increasing, decreasing, or stable.

## Model Predictions
Model-based predictions are displayed only when minimum quality thresholds are met:
- At least four years of data used in model fitting
- Model R² ≥ 0.2
If these conditions are not satisfied, predicted trends are not shown.

## Running the Application Dependencies
- Python 3.9+
- pandas
- numpy
- dash
- plotly
Install dependencies with:

```bash
pip install pandas numpy dash plotly
```
## Directory Structure

```bash
project-root/
├── app.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── data/
│   ├── ebd_MI_threecounties.csv.gz
│   └── species_trend_predictions.csv
└── README.md
```

### Launch

Run the application with:

```bash
python app.py
```
The server will start locally at:

```bash
http://127.0.0.1:8050/
```

### 5. Updating the conda environment

If environment.yml is modified, update the environment with:

```bash
conda env update -f environment.yml --prune
```

## Interpretation Notes

Observed counts represent reported sightings rather than true population estimates. Trends may reflect variation in observer effort, reporting behavior, or accessibility in addition to ecological change. Model predictions should be interpreted as exploratory rather than definitive.

## Intended Use
This project is intended for exploratory analysis, educational purposes, and demonstration of interactive data-driven trend visualization. It is not intended for regulatory, management, or conservation decision-making without additional validation.
