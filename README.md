# Equinoxe 2026 : Precision Rent Forecasting Engine

**Team:** JFF Podcast team

A predictive machine learning engine that cuts through real estate noise to forecast Jadco's true 2026 cash-flow using constant-unit effective rent analysis.

---

## Project Overview

Real estate portfolio management is often driven by intuition or flawed macroscopic metrics. When analyzing Jadco’s Equinoxe dataset, we quickly realized that looking at median rental prices created a dangerous illusion. The influx of new luxury buildings masked the true economic performance of existing units, and the heavy use of concessions (free months) created a disconnect between contractual rent and actual cash flow. 

Our solution is an end-to-end predictive engine that forecasts the 2026 rent growth for Jadco’s portfolio. Instead of predicting generic market trends, it zeroes in on the true financial reality: the Effective Rent Growth on a Constant-Unit Basis (CAGR). It predicts exactly how much more money a specific unit will yield in the coming year, taking into account the building's lifecycle, the tenant's status (renewal vs. turnover), and the broader Canadian macroeconomic climate.

## Methodology

1. **Financial Auditing:** We crossed historical leases with raw `PromoPay` data to calculate the exact amortized *Effective Rent*, ensuring we train our model on true cash-flow, not display prices.
2. **Feature Engineering:** We created specialized variables such as `Is_LeaseUp` (to identify volatile new buildings)..
3. **Macroeconomic Integration:** We merged local CMHC Vacancy Rates (capturing supply/demand) and Statistics Canada Shelter CPI (with an 18-month lag to simulate TAL regulatory inertia).
4. **Machine Learning:** We fed these complex, non-linear interactions into a Random Forest Regressor, validated through a strict chronological Walk-Forward Backtesting methodology to prevent any temporal data leakage. We also utilize SHAP values to provide explainability to our predictions.

## How to Run the Project

### Prerequisites
Make sure you have Python installed. The project relies on the following major libraries:
- `pandas`
- `scikit-learn`
- `shap`
- `matplotlib`
- `seaborn`
- `jupyter`

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd codeml_jadco
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   Install the required packages using pip:
   ```bash
   pip install pandas scikit-learn shap matplotlib seaborn jupyter
   ```

### Execution

1. Place the required Jadco CSV data files (`equinoxe_listings.csv`, `equinoxe_lease_history.csv`, `equinoxe_concessions.csv`, `equinoxe_asking_history.csv`) into the `data/` folder.
2. Launch Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
3. Open `final_submission.ipynb`.
4. Run the notebook from top to bottom (`Cell > Run All`). The final cells will output the `backtest()` validation results and the final `estimate_2026()` predictions for the Jadco portfolio.

## Repository Structure

- `final_submission.ipynb`: The main executable notebook containing all data exploration, feature engineering, and the final Random Forest model.
- `data/`: Folder intended to house the raw CSV files (excluded via `.gitignore` for confidentiality).

