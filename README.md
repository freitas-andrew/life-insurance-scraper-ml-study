# Uncovering the Cost of Risk

<!-- TABLE OF CONTENTS -->
## 📑 Table of Contents

- [Uncovering the Cost of Risk](#uncovering-the-cost-of-risk)
  - [📑 Table of Contents](#-table-of-contents)
  - [📝 About The Project](#-about-the-project)
  - [📊 Project report](#-project-report)
  - [🛠️ Prerequisites](#️-prerequisites)
  - [🚀 Installation](#-installation)
  - [📁 Project Structure](#-project-structure)
  - [▶️ Usage](#️-usage)
    - [Step 1: Running the Scrapers](#step-1-running-the-scrapers)
    - [Step 2: Cleaning the data](#step-2-cleaning-the-data)
    - [Step 3: Generating Figures](#step-3-generating-figures)
    - [Step 4: Updating the report notebook](#step-4-updating-the-report-notebook)
  - [🔍 Details](#-details)
  
<!-- ABOUT THE PROJECT -->
## 📝 About The Project

This project analyzes life insurance pricing in the US and UK using machine learning (**Random Forests** and **SHAP** for interpretability). By collecting and modeling large datasets of quotes, it predicts premiums based on policyholder information and identifies the key factors influencing pricing, providing insights for both consumers and insurers.

## 📊 Project report

To access the complementary report for this project with detailed explanations, visuals, and findings, see the [**report.ipynb**](./report/report.ipynb) notebook.

> **NOTE**: To fully experience the notebook and view the generated outputs (e.g., graphs, models, etc.), please **download and run it locally** using Jupyter or a similar environment.  
>
> **Alternatively**, if you cannot run it locally, you can **view the** [**report.pdf**](./report/report.pdf) for a static representation of the content.

<!-- PREREQUESITES -->
## 🛠️ Prerequisites

- [**Python 3.10+**](https://www.python.org/downloads/) with pip _(only required if not using conda)_
- [**Miniforge**](https://github.com/conda-forge/miniforge) or other conda installation _(optional, but recommended)_
- [**Google Chrome**](https://www.google.com/chrome/) or Chromium browser

<!-- INSTALLATION -->
## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/freitas-andrew/life-insurance-scraper-ml-study
   cd life-insurance-scraper-ml-study
   ```

2. **Set up Python environment**

- Option 1: Using **Conda** _(recommended)_

    ```bash
    conda env create -f environment.yml
    conda activate life-scraper-ml
    ```

- Option 2: Using **venv** _(simpler)_

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

<!-- PROJECT STRUCTURE -->
## 📁 Project Structure

Overview of the project's structure:

```text
life-insurance-scraper-ml-study/
├── data
│   ├── clean
│   │   └── all_quotes.csv          # Combined & processed data to analyse
│   └── raw
│       ├── drewberry_urls.csv      # Scraped urls w/ preconfigured details
│       ├── final_UK_quotes.csv     # Scraped Drewberry data (UK)
│       └── final_US_quotes.csv     # Scraped Lifeinsure data (US)
├── output
│   └── figures
│       ├── Fig01-premdist.png      # Premium distribution plot
│       ├── Fig02-corrhmap.png      # Correlation heatmap
│       ├── Fig03-avgdem.png        # Average demographics plot
│       ├── Fig04-PDPs.png          # Partial Dependence Plots for features
│       ├── Fig05-ICEs.png          # Individual Conditional Expectation plots
│       ├── Fig06-SHAPimp.png       # SHAP feature importance plot
│       ├── Fig07-SHAPbee.png       # SHAP bee swarm plot
│       ├── Fig08-SHAPwater.png     # SHAP waterfall plot (10th percentile)
│       ├── Fig09-SHAPwater.png     # (50th percentile)
│       └── Fig10-SHAPwater.png     # (90th percentile)
├── report
│   ├── report.ipynb                # Jupyter notebook for report
│   └── report.pdf                  # PDF export of final report
├── src
│   ├── 01_scrape
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   ├── data_sample.py      # Defined sample of inputted consumer data
│   │   │   └── driver_utils.py     # Utilites for scrapers
│   │   ├── drewberry_scraper.py    # Additionally maps consumer info → URL
│   │   └── lifeinsure_scraper.py
│   ├── 02_clean.ipynb              # Notebook to Prepare and merge data
│   └── 03_visualise.ipynb          # Generation of figures
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── environment.yml                 # Conda environment configuration
└── requirements.txt                # Python dependencies to install via pip

10 directories, 26 files
```
<!-- USAGE EXAMPLES -->
## ▶️ Usage

### Step 1: Running the Scrapers

```bash
python src/01_scrape/drewberry_scraper.py
```

```bash
python src/01_scrape/lifeinsure_scraper.py
```

These commands run each scraper individually and save their ouptuts to `drewberry_urls.csv` & `UK_quotes.csv` and `US_quotes.csv`, respectively.

**⚠️ IMPORTANT NOTES:**

  1. **Data Notes:** the final report uses `final_UK_quotes.csv` and `final_US_quotes.csv`, which are fixed snapshots of data, to ensure consistency in the report and to avoid data being overwritten. _**If you wish to generate new figures with updated data you can overwrite these files**_, but the figures in the final report will change accordingly.
  2. **Execution Time:** Scrapers may take a significant amount of time to run — potentially several hours — depending on network speed, and website response times.
  3. **Stability:** The scrapers rely on the structure of external websites and may break if the website changes, or if memory usage is too high.

### Step 2: Cleaning the data

```bash
jupyter nbconvert --to notebook --execute --inplace ./src/02_clean.ipynb
```

Executes the `02_clean.ipynb` notebook to preprocess and merge the raw scraped data into a clean dataset (`all_quotes.csv`) ready for analysis. **Note that,** as mentioned before, this specifically uses the `final_UK_quotes.csv` and the `final_US_quotes.csv`.

### Step 3: Generating Figures

```bash
jupyter nbconvert --to notebook --execute --inplace ./src/visualise.ipynb
```

Executes the `03_visualise.ipynb` notebook to train the Random Forest model _(may result in a prolonged execution time)_ and generate all report visualisations, saving them under the _`output/figures/`_ directory. _(Execution may take a long time depending on system resources)_

### Step 4: Updating the report notebook

```bash
jupyter nbconvert --to notebook --execute --inplace ./report/report.ipynb
```

Executes the `report.ipynb` notebook to refresh outputs, summaries, and visualizations with the latest processed data and figures.

<!-- DETAILS -->
## 🔍 Details

- **Author:** [_**Andrew Freitas**_](https://github.com/freitas-andrew/life-insurance-scraper-ml-study)
- **Source code:** [_GitHub Repository_](https://github.com/freitas-andrew/life-insurance-scraper-ml-study/tree/master/scrapers)
