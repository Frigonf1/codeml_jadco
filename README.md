# JADCO - Collection Équinoxe : Clés en main

## 1. Challenge Overview
Estimate Collection Équinoxe's **2026 rent increase** using historical data across six buildings in Québec and Ontario. 
* Clearly **define the rent increase** you are measuring.
* **Justify your modeling methodology and analytical choices.**
* Reasoning and sound methodology matter more to the jury than proximity to a single arbitrary number.

---

## 2. Objectives & Scope
* **Yardi Data Mastery:** Understand the 4 source tables and standard Yardi `h`/`s` fields.
* **Portfolio Composition:** Identify and explain portfolio composition effects.
* **Unit & Lease Matching:** Match consecutive leases using `sPropCode` + `sUnitCode` (or `hUnit`). *Do not use `sSite` + `sUnitCode`.*
* **Concessions & Net Effective Rent:** Account for tenant concessions by analyzing `sRent` vs. `sRentEffective`.
* **Turnovers vs. Renewals:** Accurately segment lease renewals from turnovers using `sRenewal`.
* **Jurisdictional Context:** Distinguish and account for differing rental regulations in **Québec** vs. **Ontario**.
* **External Data Integration:** Incorporate external macroeconomic / public data sources (e.g., inflation, CPI, market rent benchmarks, TAL/LTB guidelines).
* **Implementation:** Implement and complete the required functions:
  * `estimate_2026()`
  * `backtest()`
* **Validation:** Validate and backtest your method against historical performance for 2023, 2024, and 2025.
* **Limitations:** Note that this extract *cannot* be used to calculate portfolio occupancy, vacancy, or absorption.

---

## 3. Dataset Description
The challenge dataset consists of four raw CSV files (plus starter files):

| File Name | Dimensions | Description |
| :--- | :--- | :--- |
| `equinoxe_listings.csv` | 1,061 units, 29 cols | Property and unit-level listings |
| `equinoxe_lease_history.csv` | 4,302 leases, 35 cols | Lease terms, start/end dates, renewal status |
| `equinoxe_concessions.csv` | 3,560 rows, 18 cols | Concession amounts, types, and schedules |
| `equinoxe_asking_history.csv` | 3,857 rows, 14 cols | Historical asking rents over time |
| `starter.ipynb` | Jupyter Notebook | Starter notebook containing base function signatures |

> **Data Horizons & Caveat:** Signature dates, lease starts, and asking-rent histories extend through December 2025. While certain contractual lease-end and concession dates run past 2025, **they do not serve as an answer key** for the 2026 rent increase.

---

## 4. Evaluation Rubric (100 Points Total)

A jury evaluates your Jupyter notebook and presentation based on the following breakdown:

| Criteria | Points | Focus Areas |
| :--- | :---: | :--- |
| **Definition of the rent increase** | **10 pts** | Clear, rigorous mathematical & operational definition of the target metric. |
| **Data analysis & composition effects**| **15 pts** | Handling portfolio mix shifts, unit-type variations, and property nuances. |
| **Same-unit lease matching** | **15 pts** | Correct matching logic via `sPropCode` + `sUnitCode` (or `hUnit`). |
| **Concessions** | **10 pts** | Proper adjustment between face rent (`sRent`) and effective rent (`sRentEffective`). |
| **Renewals and turnovers** | **10 pts** | Accurate segmentation using `sRenewal` and handling turnover spreads. |
| **External data** | **15 pts** | Integration of public benchmarks, market indices, or provincial regulatory rules. |
| **Forecast and backtest** | **15 pts** | Working `estimate_2026()` and `backtest()` across 2023–2025 with defensible error metrics. |
| **Notebook quality** | **10 pts** | Code readability, structure, markdown documentation, reproducibility, and hygiene. |

---

## 5. Submission & Rules

### Non-Negotiable Rules & Data Privacy
1. **Confidentiality (CRITICAL):**
   * **Do NOT upload raw CRM data or CSVs to public repositories (GitHub, Kaggle, etc.).**
   * Keep `.gitignore` updated so data files and raw outputs are never tracked.
   * Strip raw CRM data and identifying tenant details from outputs/visualizations in submitted deliverables.
2. **Immutable Source Data:**
   * Keep source CSV files untouched and unmodified.
   * All data transformations, joins, and feature engineering must occur programmatically inside the notebook.
3. **Tooling & Environment:**
   * Python and Jupyter Notebook using the provided `starter.ipynb`.
   * Explain transformations and modeling rationale in dedicated Markdown cells.
   * Cite all public data sources, external articles, and AI tools used.

### Submission Deliverables (Devpost)
* **Jupyter Notebook (`.ipynb`):**
  * Fully executable with `estimate_2026()` and `backtest()` completed.
  * Clear Markdown documentation of methodology, assumptions, and findings.
  * Clear execution instructions, library versions, and citations/references.
* **Final Estimate:** Final 2026 estimate expressed as a **percentage**, accompanied by its exact metric definition.
* **Trained Model:** Serialized model artifacts if applicable.
* **Presentation:** Jury presentation materials.
* **Devpost Details:**
  * Submit under the exact **team name** registered on HxBuddy.
  * Select **exactly one prize** corresponding to this challenge.