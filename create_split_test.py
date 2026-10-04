import json
import xgboost as xgb
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

nb = json.load(open('xgboost_backtesting.ipynb', encoding='utf-8'))
source = []
for c in nb.get('cells', []):
    if c['cell_type'] == 'code':
        source.append(''.join(c['source']))
code = '\n'.join(source)

# I only want to run the pipeline part
code = code.split("target_years = [2023, 2024, 2025]")[0]

code += """
X_train, X_test, y_train, y_test = train_test_split(X.drop(columns=['Lease_Year']), y, test_size=0.2, random_state=42)
xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
xgb_model.fit(X_train, y_train)
preds = xgb_model.predict(X_test)
print(f'Random Split R2: {r2_score(y_test, preds):.4f}')
"""
with open('run_split_test.py', 'w', encoding='utf-8') as f:
    f.write(code)
