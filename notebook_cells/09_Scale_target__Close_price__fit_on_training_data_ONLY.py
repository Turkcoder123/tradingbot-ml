# --- Step 5: Scale the Data (OHLCV + Features) ---
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Scale target (Close price) - fit on training data ONLY
target_scaler = StandardScaler()
train_df['Close_scaled'] = target_scaler.fit_transform(train_df[['Close']])
val_df['Close_scaled'] = target_scaler.transform(val_df[['Close']])
test_df['Close_scaled'] = target_scaler.transform(test_df[['Close']])

# Scale OHLCV features for model input
feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 
                   'Range_5m', 'Range_1h', 'Range_1d']

ohlv_scaler = StandardScaler()
train_df[feature_columns] = ohlv_scaler.fit_transform(train_df[feature_columns])
val_df[feature_columns] = ohlv_scaler.transform(val_df[feature_columns])
test_df[feature_columns] = ohlv_scaler.transform(test_df[feature_columns])

print("Target and OHLCV features scaled successfully.")
print(f"Target scaler mean: {target_scaler.mean_[0]:.6f}, std: {target_scaler.scale_[0]:.6f}")