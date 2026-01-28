# Michigan Bird Species Trends Dashboard

A Python Dash application for exploring county-level bird observation trends in Michigan using filtered eBird checklist data and precomputed statistical trend models. The application allows users to select a county and species and view yearly observation totals alongside model-based trend predictions when available.

## Features

- Interactive county and species selection
- Time series visualization of observed yearly bird counts
- Model-predicted trend lines with confidence intervals
- Summary statistics including average sightings, peak years, and trend classification
- Quality-filtered eBird data for improved comparability

## Directory Structure

```
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

## Data Inputs

The application relies on two input datasets stored in the `data/` directory.

### Observation Data

**File:** `data/ebd_MI_threecounties.csv.gz`

Compressed CSV containing eBird checklist records with the following relevant fields:
- `OBSERVATION DATE` - Date of bird observation
- `OBSERVATION COUNT` - Number of individuals observed
- `COMMON NAME` - Species common name
- `COUNTY` - Michigan county name
- `DURATION MINUTES` - Checklist duration in minutes
- `NUMBER OBSERVERS` - Number of observers on checklist
- `ALL SPECIES REPORTED` - Whether all species were reported (1 = complete checklist)

### Trend Prediction Data

**File:** `data/species_trend_predictions.csv`

CSV containing precomputed model outputs by species and county, including:
- Predicted yearly counts
- Lower and upper confidence intervals
- Model R² values
- p-values
- Number of years used for model fitting

## Data Processing

Before analysis, the observation dataset is filtered to improve comparability and data quality:

- **Complete checklists only:** Only records where `ALL SPECIES REPORTED == 1` are retained
- **Duration filtering:** Observation duration limited to 5–180 minutes
- **Observer limit:** Checklists with more than 5 observers are excluded
- **Positive counts:** Only observations with counts > 0 are included
- **Date parsing:** Observation dates are parsed and converted to calendar years

After filtering, observations are aggregated by year and species using summed counts.

## Trend Calculation

A linear regression slope is computed on yearly observed counts using `numpy.polyfit`. The slope is used to classify trends as:

- **Increasing** Slope > 0.05
- **Stable** Slope between -0.05 and 0.05
- **Decreasing** Slope < -0.05

## Model Predictions

Model-based predictions are displayed only when minimum quality thresholds are met:

- At least **4 years** of data used in model fitting
- Model **R² ≥ 0.2**

If these conditions are not satisfied, a warning is displayed and predicted trends are not shown.

## Setup and Installation

This project uses `uv` for fast, reproducible Python environment and dependency management.

### Prerequisites

- Python 3.9+

### 1. Install `uv`

```bash
pip install uv
```

Verify installation:

```bash
uv --version
```

### 2. Clone or Download the Project

Navigate to the project root directory.

### 3. Install Dependencies

The project dependencies are managed in `pyproject.toml`. Install them using:

```bash
uv sync
```

**Required packages:**
- pandas
- numpy
- dash
- plotly

### 4. Verify Installation

To confirm the correct Python environment is being used:

```bash
uv run python -c "import sys; print(sys.executable)"
```

## Running the Application

Launch the Dash application:

```bash
uv run python app.py
```

The server will start locally at:

```
http://127.0.0.1:8050/
```

Open this URL in your web browser to access the dashboard.

## Application Usage

### User Inputs

1. **County Selection:** Choose from available Michigan counties (Ingham, and others)
2. **Species Selection:** Choose from observed bird species (e.g., Red-winged Blackbird)

### Outputs

- **Time series plot:** Line chart showing observed yearly counts (blue) and model predictions (red) when available
- **Confidence intervals:** Shaded region around predictions showing uncertainty
- **Trend summary:** 
  - Average sightings per year
  - Peak observation year
  - Trend classification (Increasing/Stable/Decreasing)
  - Model statistics (R², p-value, years used for fitting)

## Updating Dependencies

To add new packages:

```bash
uv add <package-name>
```

To update existing dependencies:

```bash
uv lock --upgrade
```

## Interpretation Notes

**Important considerations when interpreting results:**

- Observed counts represent reported sightings rather than true population estimates
- Trends may reflect variation in observer effort, reporting behavior, or site accessibility in addition to ecological change
- Model predictions should be interpreted as exploratory rather than definitive
- High variability in citizen science data means trends should be viewed with appropriate caution

## Intended Use

This project is intended for:
- Exploratory data analysis
- Educational purposes
- Demonstration of interactive data-driven trend visualization

## License

This project uses eBird data. Please review eBird's [Terms of Use]([https://www.ebird.org/about/terms-of-use](https://ebird.org/about/products-access-terms-of-use)) for data usage policies.

## Acknowledgments

Data provided by eBird, a collaborative project of the Cornell Lab of Ornithology and bird enthusiasts worldwide.
