# Real Estate Pricing Model - Project Recap

## 1. Goal
Predict the localized rent growth percentage (`growth_pct`) of an apartment unit given market conditions, historical rent, building strategy, and macroeconomic indicators.

## 2. Features Engineered
We successfully transformed raw lease history into a robust financial dataset:
1. **Target Variable Modification**: Switched from raw percentage difference to the **Annualized Compound Growth Rate** (`growth_pct`) of the *Effective Rent*. This perfectly standardizes the rent increase to a 12-month timeframe, neutralizing the noise of varying lease durations (6 months vs 24 months).
2. **Concession Mathematics**: We incorporated Yardi's linear amortization logic. The model now knows the exact dollar magnitude of previous concessions, preventing it from confusing a "concession cliff" (the sudden jump in rent when a discount expires) with a legitimate market-driven rent spike.
3. **Building Stabilization Strategy**: Injected the `Is_LeaseUp` flag, allowing the model to split its logic between new buildings (fighting for occupancy with lower increases) vs. established buildings (optimizing for profit).
4. **CMHC Market Data**: Merged localized CMHC Vacancy Rates and Average Market Rents to calculate the `CMHC_Market_Premium` (how overpriced/underpriced a unit is compared to its exact city and bedroom count).
5. **Macroeconomic Indicators (TAL Proxy)**: Merged the Statistics Canada Consumer Price Index for Shelter (`CPI_Index_Shelter`), shifted backwards by exactly **18 months**, perfectly simulating the time-lagged environment property managers use to calculate TAL statutory caps.

## 3. Current Performance Analysis (R-Squared: 31%)
The Random Forest Regressor currently yields an $R^2$ of ~31.6%. 
**Is this a mistake?** 
No. In micro-level human behavioral forecasting (predicting the exact percentage increase a specific human agreed to), an $R^2$ of 30-40% is extremely standard and highly useful. 
The remaining variance is driven by factors we cannot measure: a tenant's divorce, job relocation, interpersonal negotiation skills with the leasing agent, or unit-specific wear-and-tear (e.g., a broken appliance delaying a rent hike). The data pipeline is perfectly clean (0 nulls, bounded min/max targets).

## 4. Next Steps & Alternative Models
To push the performance further and extract more business value, we can explore alternative model architectures:
1. **Gradient Boosting (XGBoost / LightGBM)**: Upgrade from Random Forest to Gradient Boosting. XGBoost handles complex, non-linear interactions (like the interplay between a massive `Market_Gap` and a high `Previous_Concession_Ratio`) much better than Random Forest.
2. **Classification (Churn Prediction)**: Instead of predicting the exact rent increase percentage, we can pivot to predicting the *probability of renewal*. (e.g., "If we raise the rent by 5%, what is the probability the tenant leaves?"). This is often far more actionable for property managers looking to maximize revenue without causing vacancies.
3. **Building-Level Time Series**: If the goal is portfolio valuation, we can aggregate the data to the building level and predict the total average Rent Roll over time. Because individual human noise is averaged out, building-level models typically achieve an $R^2$ of 85-95%.
