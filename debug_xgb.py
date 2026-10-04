import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

%matplotlib inline
data_dir = "data/"
lease_df = pd.read_csv(data_dir + "equinoxe_lease_history.csv")
asking_df = pd.read_csv(data_dir + "equinoxe_asking_history.csv")

# Concessions
conc_df = pd.read_csv(data_dir + 'equinoxe_concessions.csv')
conc_df['sDateFrom'] = pd.to_datetime(conc_df['sDateFrom'])
conc_df['sAmount'] = conc_df['sAmount'].fillna(0)

conc_sorted = conc_df.sort_values('sDateFrom')
conc_dummies = pd.get_dummies(conc_sorted['sChargeCode'], prefix='Conc')
conc_processed = pd.concat([conc_sorted[['hUnit', 'sDateFrom']], conc_dummies], axis=1)

conc_amt = conc_sorted.groupby(['hUnit', 'sDateFrom'])['sAmount'].sum().reset_index()
conc_processed = conc_processed.groupby(['hUnit', 'sDateFrom']).max().reset_index()
conc_processed = pd.merge(conc_processed, conc_amt, on=['hUnit', 'sDateFrom'])
conc_processed = conc_processed.sort_values('sDateFrom')

# Merge onto lease_df
lease_df['sLeaseFrom_dt'] = pd.to_datetime(lease_df['sLeaseFrom'])
lease_sorted = lease_df.sort_values('sLeaseFrom_dt')

lease_df = pd.merge_asof(
    lease_sorted,
    conc_processed,
    by='hUnit',
    left_on='sLeaseFrom_dt',
    right_on='sDateFrom',
    direction='backward',
    tolerance=pd.Timedelta('365D')
)

concession_cols = [c for c in lease_df.columns if c.startswith('Conc_')]
lease_df[concession_cols] = lease_df[concession_cols].fillna(0).astype(int)
lease_df['sAmount'] = lease_df['sAmount'].fillna(0)

# Flag for 'Lease-Up' Strategy vs 'Established' Buildings
established_buildings = ['Daniel-Johnson', 'Levesque']
established_prop_codes = ['stelz1', 'stelz2'] # stelz3 is brand new!

def is_lease_up(row):
    b = str(row['sBuilding']).strip()
    p = str(row['sPropCode']).strip()
    if b in established_buildings:
        return 0
    elif b == 'Saint-Elzear' and p in established_prop_codes:
        return 0
    else:
        return 1

lease_df['Is_LeaseUp'] = lease_df.apply(is_lease_up, axis=1)

keep_cols = ['Is_LeaseUp', 'hUnit', 'sBuilding', 'sCity', 'sState', 'sTermSeq', 'sRent', 'sRentEffective', 'sBeds', 'sBaths', 'sSqft', 'sUnitType', 'sRenewal', 'sLeaseFrom', 'sTermMonths', 'sAmount'] + concession_cols
lease_df = lease_df[keep_cols].copy()

lease_df['sLeaseFrom'] = pd.to_datetime(lease_df['sLeaseFrom'])
lease_df['LeaseMonth'] = lease_df['sLeaseFrom'].dt.month.astype(str)
lease_df['MergeMonth'] = lease_df['sLeaseFrom'].dt.to_period('M').astype(str)

lease_df = lease_df.sort_values(by=['hUnit', 'sTermSeq'])
lease_df['Previous_sRentEffective'] = lease_df.groupby('hUnit')['sRentEffective'].shift(1)
lease_df['Previous_sAmount'] = lease_df.groupby('hUnit')['sAmount'].shift(1)
lease_df['Previous_sLeaseFrom'] = lease_df.groupby('hUnit')['sLeaseFrom'].shift(1)

lease_df['Previous_Concession_Ratio'] = lease_df['Previous_sAmount'].abs() / (lease_df['Previous_sRentEffective'] * 12)
lease_df['Previous_Concession_Ratio'] = lease_df['Previous_Concession_Ratio'].fillna(0)

for col in concession_cols:
    lease_df[f'Previous_{col}'] = lease_df.groupby('hUnit')[col].shift(1)

model_df = lease_df.dropna(subset=['Previous_sRentEffective']).copy()
for col in concession_cols:
    model_df[f'Previous_{col}'] = model_df[f'Previous_{col}'].fillna(0).astype(int)

model_df['gap_years'] = (model_df['sLeaseFrom'] - model_df['Previous_sLeaseFrom']).dt.days / 365.25
model_df = model_df[model_df['gap_years'] >= 0.1].copy()
model_df['growth_pct'] = ((model_df['sRentEffective'] / model_df['Previous_sRentEffective']) ** (1 / model_df['gap_years']) - 1) * 100

asking_df = asking_df[['hUnit', 'sMonth', 'sAskingRent']].copy()
asking_df['sMonth_dt'] = pd.to_datetime(asking_df['sMonth'] + '-01')
model_df['sLeaseFrom_dt'] = pd.to_datetime(model_df['MergeMonth'] + '-01')
model_df['sLeaseFrom_dt_minus_12m'] = model_df['sLeaseFrom_dt'] - pd.DateOffset(months=12)

asking_sorted = asking_df.sort_values('sMonth_dt')
model_sorted = model_df.sort_values('sLeaseFrom_dt')

merged_df = pd.merge_asof(
    model_sorted, 
    asking_sorted, 
    by='hUnit', 
    left_on='sLeaseFrom_dt', 
    right_on='sMonth_dt', 
    direction='backward'
)

merged_df = pd.merge_asof(
    merged_df.sort_values('sLeaseFrom_dt_minus_12m'), 
    asking_sorted, 
    by='hUnit', 
    left_on='sLeaseFrom_dt_minus_12m', 
    right_on='sMonth_dt', 
    direction='backward',
    suffixes=('', '_12m_ago')
)

merged_df = merged_df.sort_values(['hUnit', 'sTermSeq'])
merged_df['Market_Gap'] = merged_df['sAskingRent'] - merged_df['Previous_sRentEffective']
merged_df['Market_Gap'] = merged_df['Market_Gap'].fillna(0)
merged_df['Market_Velocity'] = (merged_df['sAskingRent'] - merged_df['sAskingRent_12m_ago']) / merged_df['sAskingRent_12m_ago']
merged_df['Market_Velocity'] = merged_df['Market_Velocity'].fillna(0) 

# CMHC
cmhc_df = pd.read_csv(data_dir + "external_data/cmhc_consolidated.csv")
cmhc_df['Date_dt'] = pd.to_datetime(cmhc_df['Date'] + '-01')
cmhc_sorted = cmhc_df.sort_values('Date_dt')

cma_mapping = {'Mont-Royal': 'Montreal', 'Laval': 'Montreal', 'Pointe-Claire': 'Montreal', 'Ottawa': 'Ottawa'}
merged_df['CMA'] = merged_df['sCity'].map(cma_mapping).fillna('Montreal')

unit_mapping = {0: 'Studio', 1: '1 Bedroom', 2: '2 Bedroom', 3: '3 Bedroom +'}
merged_df['Unit_Type_CMHC'] = merged_df['sBeds'].map(unit_mapping)

merged_df = merged_df.sort_values('sLeaseFrom_dt')

merged_df = pd.merge_asof(
    merged_df,
    cmhc_sorted,
    left_on='sLeaseFrom_dt',
    right_on='Date_dt',
    left_by=['CMA', 'Unit_Type_CMHC'],
    right_by=['City', 'Unit_Type'],
    direction='backward'
)

merged_df['Vacancy_Rate_Pct'] = merged_df.groupby(['CMA', 'Unit_Type_CMHC'])['Vacancy_Rate_Pct'].transform(lambda x: x.bfill().ffill())
merged_df['Average_Rent'] = merged_df.groupby(['CMA', 'Unit_Type_CMHC'])['Average_Rent'].transform(lambda x: x.bfill().ffill())
merged_df['Rent_YoY_Growth_Pct'] = merged_df.groupby(['CMA', 'Unit_Type_CMHC'])['Rent_YoY_Growth_Pct'].transform(lambda x: x.bfill().ffill())

merged_df['CMHC_Market_Premium'] = (merged_df['Previous_sRentEffective'] - merged_df['Average_Rent']) / merged_df['Average_Rent']
merged_df['CMHC_Market_Premium'] = merged_df['CMHC_Market_Premium'].fillna(0)

# CPI
cpi_df = pd.read_csv(data_dir + 'external_data/1810000401_databaseLoadingData.csv')
cpi_df = cpi_df[cpi_df['Products and product groups'] == 'Shelter'].copy()
cpi_df['Date_dt'] = pd.to_datetime(cpi_df['REF_DATE'] + '-01')
cpi_df = cpi_df.sort_values('Date_dt')
cpi_df = cpi_df[['Date_dt', 'VALUE']].rename(columns={'VALUE': 'CPI_Index_Shelter'})

merged_df['LeaseFrom_Lagged_18m'] = merged_df['sLeaseFrom_dt'] - pd.DateOffset(months=18)
merged_df = merged_df.sort_values('LeaseFrom_Lagged_18m')

merged_df = pd.merge_asof(
    merged_df,
    cpi_df,
    left_on='LeaseFrom_Lagged_18m',
    right_on='Date_dt',
    direction='backward'
)
merged_df['CPI_Index_Shelter'] = merged_df['CPI_Index_Shelter'].bfill().ffill()

# Imputations
merged_df['sBaths'] = merged_df['sBaths'].fillna(merged_df['sBaths'].median())
merged_df['sSqft'] = merged_df['sSqft'].fillna(merged_df['sSqft'].median())
merged_df['sTermMonths'] = merged_df['sTermMonths'].fillna(12)

# Keep Lease_Year for backtesting!
merged_df['Lease_Year'] = merged_df['sLeaseFrom_dt'].dt.year

features = ['Lease_Year', 'CPI_Index_Shelter', 'Is_LeaseUp', 'sBeds', 'sBaths', 'sSqft', 'sTermMonths', 'sRenewal', 'LeaseMonth', 'Market_Gap', 'Market_Velocity', 'Previous_sRentEffective', 'Vacancy_Rate_Pct', 'Rent_YoY_Growth_Pct', 'CMHC_Market_Premium', 'sBuilding', 'sState', 'Previous_Concession_Ratio'] + concession_cols + [f'Previous_{c}' for c in concession_cols]
X = merged_df[features].copy()
X['sRenewal'] = X['sRenewal'].astype(int)

# Dummy encoding for Seasonality and Geography
X = pd.get_dummies(X, columns=['LeaseMonth', 'sBuilding', 'sState'], drop_first=True)
y = merged_df['growth_pct']
print(f"Dataset fully loaded and engineered. Shape: {X.shape}")
print(X.head(10))
target_years = [2023, 2024, 2025]
results = []
models = {}

print("Starting Walk-Forward Backtesting for XGBoost...")

for year in target_years:
    print(f"\n--- Backtesting Year: {year} ---")
    
    # Train: All data strictly BEFORE the target year
    train_mask = X['Lease_Year'] < year
    # Test: All data strictly IN the target year
    test_mask = X['Lease_Year'] == year
    
    X_train = X[train_mask].drop(columns=['Lease_Year']).astype(float)
    y_train = y[train_mask]
    
    X_test = X[test_mask].drop(columns=['Lease_Year']).astype(float)
    y_test = y[test_mask]
    
    if len(X_test) == 0:
        print(f"Skipping {year} - No test data available.")
        continue
        
    print(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples.")
    
    # Initialize and train XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='reg:squarederror'
    )
    
    xgb_model.fit(X_train, y_train)
    models[year] = xgb_model
    
    # Predict
    preds = xgb_model.predict(X_test)
    
    # Evaluate
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    
    print(f"Results for {year}: R2 = {r2:.4f} | MAE = {mae:.4f}% | RMSE = {rmse:.4f}%")
    results.append({
        'Year': year,
        'R2': r2,
        'MAE': mae,
        'RMSE': rmse
    })

# Summary
res_df = pd.DataFrame(results)
print("\n--- Average Out-of-Sample Performance ---")
print(res_df.mean(numeric_only=True))
# Feature Importance (using the last trained model)
last_year = target_years[-1]
final_model = models[last_year]

imp_df = pd.DataFrame({
    'Feature': X.drop(columns=['Lease_Year']).columns,
    'Importance': final_model.feature_importances_
}).sort_values('Importance', ascending=False).head(15)

plt.figure(figsize=(10, 6))
sns.barplot(data=imp_df, x='Importance', y='Feature', hue='Feature', legend=False)
plt.title(f'XGBoost Top 15 Feature Importances (Model {last_year})')
plt.xlabel('Gain Importance')
plt.tight_layout()
plt.show()